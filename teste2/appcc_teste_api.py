from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
import uvicorn, os, json, tempfile, shutil, datetime
import joblib
import pandas as pd
from typing import Optional, Dict, Any, List
from glob import glob

# ========================
# Caminhos (ambiente TESTE)
# ========================
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
ML_MODELS_DIR = BASE_DIR / "ml" / "models" / "envase_rotulagem"
AVALIACOES_DIR = BASE_DIR / "avaliacoes"
CACHE_DIR = AVALIACOES_DIR / "cache"
RESULT_DIR = AVALIACOES_DIR / "resultados"
for d in (STATIC_DIR, CACHE_DIR, RESULT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ========================
# App
# ========================
app = FastAPI(title="SIQUALIA - App de Teste (Subset por Perigo)", docs_url="/docs", redoc_url="/redoc")

# CORS liberado para DEV; em produção, restrinja origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Servir front
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def index():
    html = STATIC_DIR / "appcc_teste.html"
    if html.exists():
        return FileResponse(str(html))
    return JSONResponse({"ok": True, "msg": "Abra /static/appcc_teste.html"})

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

# ========================
# Contratos e subsets
# ========================
TIPOS_PERIGO = {"bio","fis","qui"}

# Núcleo mínimo que será EXIGIDO por perigo (o restante é ignorado)
FEATURE_SUBSETS = {
    "bio": [
        "umidade_mel","higienizacao_previa","manipulador_higiene","uso_epi",
        "local_envase","temperatura_envase","tempo_exposicao_ar","aspecto_visual"
    ],
    "fis": [
        "estado_embalagem","tampa_correta","vedacao_adequada","tipo_embalagem",
        "aspecto_visual","manipulador_higiene","local_envase"
    ],
    "qui": [
        "informacoes_completas","rotulo_presente","data_validade_legivel",
        "lote_identificado","vedacao_adequada","tipo_embalagem",
        "higienizacao_previa","registro_lote"
    ],
}

CLASSES = ["DESPREZÍVEL", "BAIXA", "MÉDIA", "ALTA"]

class PredicaoReq(BaseModel):
    bpfRespostas: Dict[str, Any]
    tipo_perigo: Optional[str] = "bio"  # "bio" | "fis" | "qui"

class RiscoReq(BaseModel):
    probabilidade: str
    severidade: str

class SaveCacheReq(BaseModel):
    sessionId: str
    state: Dict[str, Any]

class FinalizarReq(BaseModel):
    sessionId: str
    registro: Dict[str, Any]

# ========================
# Utilidades
# ========================
def _safe_json_load(path: Path):
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            return []
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except Exception:
        return []

def _atomic_write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
        shutil.move(tmp_name, path)
    finally:
        try:
            if os.path.exists(tmp_name):
                os.remove(tmp_name)
        except Exception:
            pass

def _map_class_index_to_name(idx: int) -> str:
    try:
        return CLASSES[int(idx)]
    except Exception:
        return "MÉDIA"

def _ordinal_score_from_class(name: str) -> float:
    mapping = {"DESPREZÍVEL":0, "BAIXA":1, "MÉDIA":2, "ALTA":3}
    v = mapping.get((name or "").upper(), 2)
    return v / 3.0

def _find_latest_model(perigo: str) -> Optional[Dict[str, Any]]:
    """Retorna dict com paths e config do último modelo válido para o perigo, ou None."""
    models_dir = ML_MODELS_DIR / perigo
    if not models_dir.exists():
        return None
    pkls = [p for p in models_dir.glob("classificador_mel_*.pkl")]
    candidates = []
    for pkl in pkls:
        ts = pkl.stem.replace("classificador_mel_", "")
        scaler = models_dir / f"scaler_mel_{ts}.pkl"
        cfg = models_dir / f"config_classificador_{ts}.json"
        if scaler.exists() and cfg.exists():
            candidates.append((ts, pkl, scaler, cfg))
    if not candidates:
        return None
    ts, pkl, scaler, cfg = sorted(candidates, key=lambda t: t[0])[-1]
    try:
        conf = json.loads(Path(cfg).read_text(encoding="utf-8"))
    except Exception:
        conf = {}
    return {
        "timestamp": ts,
        "modelo_path": str(pkl),
        "scaler_path": str(scaler),
        "config_path": str(cfg),
        "config": conf
    }

def _required_features(perigo: str, cfg_features: Optional[List[str]]) -> List[str]:
    """
    Usa a ordem salva em 'features_usadas' no config do modelo.
    Se não houver, cai para o subset padrão (FEATURE_SUBSETS).
    """
    if cfg_features and isinstance(cfg_features, list) and len(cfg_features) > 0:
        return list(cfg_features)
    return FEATURE_SUBSETS[perigo]

def _filter_and_validate_sample(sample: Dict[str, Any], perigo: str, required: List[str]) -> pd.DataFrame:
    """Filtra o sample apenas para as 'required' na ordem correta; se faltar, lança HTTP 422."""
    faltando = [c for c in required if c not in sample or sample[c] is None]
    if faltando:
        raise HTTPException(
            status_code=422,
            detail={"erro": "Campos obrigatórios ausentes para o tipo de perigo",
                    "tipo_perigo": perigo, "faltando": faltando}
        )
    # apenas as colunas necessárias, na ordem
    row = {c: sample[c] for c in required}
    return pd.DataFrame([row], columns=required)

def _predict_with_model(sample: Dict[str, Any], perigo: str) -> Dict[str, Any]:
    info = _find_latest_model(perigo)
    required = _required_features(perigo, (info or {}).get("config", {}).get("features_usadas"))

    # Fallback (sem modelo) — continua exigindo o núcleo, por consistência do contrato
    if info is None:
        df = _filter_and_validate_sample(sample, perigo, required)
        try:
            # Fallback simples usando 2–3 sinais dentro do subset (não crítico, apenas para demo)
            base = 0.0
            if "uso_epi" in df.columns: base += (2 - int(df["uso_epi"].iat[0]))
            if "estado_embalagem" in df.columns: base += (1 - int(df["estado_embalagem"].iat[0]))
            if "historico_reclamacoes" in df.columns: base += (2 - int(df["historico_reclamacoes"].iat[0]))
            cls = _map_class_index_to_name(int(max(0, min(3, base))))
            return {"prob_classe": cls, "prob_score": _ordinal_score_from_class(cls),
                    "fonte": "fallback", "modelo": None, "features_usadas": required}
        except Exception:
            return {"prob_classe": "MÉDIA", "prob_score": _ordinal_score_from_class("MÉDIA"),
                    "fonte": "fallback-erro", "modelo": None, "features_usadas": required}

    # Com modelo: valida/filtra pelo subset utilizado no treino (do config)
    df = _filter_and_validate_sample(sample, perigo, required)
    try:
        modelo = joblib.load(info["modelo_path"])
        scaler = joblib.load(info["scaler_path"])
        df = df.apply(pd.to_numeric, errors="coerce")
        if df.isna().any().any():
            raise HTTPException(
                status_code=422,
                detail={"erro": "Campos do subset contêm valores inválidos (não numéricos)",
                        "colunas": df.columns[df.isna().any()].tolist()}
            )
        X = scaler.transform(df)
        pred_idx = int(modelo.predict(X)[0])
        cls = _map_class_index_to_name(pred_idx)
        score = _ordinal_score_from_class(cls)
        probs = None
        if hasattr(modelo, "predict_proba"):
            try:
                proba = modelo.predict_proba(X)[0]
                probs = {CLASSES[i]: float(proba[i]) for i in range(min(len(proba), 4))}
                expected = sum(i * float(proba[i]) for i in range(min(len(proba), 4))) / 3.0
                score = max(0.0, min(1.0, expected))
            except Exception:
                pass
        score = round(float(score), 4)
        return {"prob_classe": cls, "prob_score": score, "probs": probs,
                "fonte": "modelo", "modelo": info["timestamp"], "features_usadas": required}
    except Exception:
        return {"prob_classe": "MÉDIA", "prob_score": _ordinal_score_from_class("MÉDIA"),
                "fonte": "fallback-erro", "modelo": None, "features_usadas": required}

def _calcula_risco(prob: str, sev: str) -> str:
    p = (prob or "").upper()
    s = (sev or "").upper()
    if p == "DESPREZÍVEL":
        return "Baixo" if s == "ALTA" else "Desprezível"
    if p == "BAIXA":
        return "Médio" if s == "ALTA" else "Baixo"
    if p == "MÉDIA":
        return "Alto" if s == "ALTA" else ("Médio" if s == "MÉDIA" else "Baixo")
    if p == "ALTA":
        return "Alto" if s in ("MÉDIA","ALTA") else "Médio"
    return "Desconhecido"

def _exige_medidas(risco: str) -> bool:
    return risco not in ("Desprezível", "Desconhecido")

# ========================
# Router /api
# ========================
api = APIRouter(prefix="/api", tags=["API"])

@api.post("/predicao")
def api_predicao(req: PredicaoReq):
    perigo = (req.tipo_perigo or "bio").lower()
    if perigo not in TIPOS_PERIGO:
        raise HTTPException(status_code=400, detail={"erro":"tipo_perigo inválido","permitidos":sorted(TIPOS_PERIGO)})

    sample = dict(req.bpfRespostas or {})
    out = _predict_with_model(sample, perigo)
    return {
        "ok": True,
        "prob_classe": out["prob_classe"],
        "prob_score": out["prob_score"],
        "fonte": out["fonte"],
        "modelo": out["modelo"],
        "tipo_perigo": perigo,
        "features_usadas": out["features_usadas"],
        # compatibilidade anterior
        "probabilidade": out["prob_classe"],
    }

@api.post("/probabilidade")
def api_probabilidade(req: PredicaoReq):
    return api_predicao(req)

@api.post("/risco")
def api_risco(req: RiscoReq):
    r = _calcula_risco(req.probabilidade, req.severidade)
    return {"ok": True, "risco": r, "exige_medidas": _exige_medidas(r)}

@api.post("/cache/salvar")
def api_cache_salvar(req: SaveCacheReq):
    (CACHE_DIR / f"{req.sessionId}.json").write_text(
        json.dumps(req.state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"ok": True}

@api.get("/cache/abrir")
def api_cache_abrir(sessionId: str):
    p = CACHE_DIR / f"{sessionId}.json"
    if p.exists():
        return {"ok": True, "state": json.loads(p.read_text(encoding="utf-8"))}
    return {"ok": True, "state": {}}

@api.post("/finalizar")
def api_finalizar(req: FinalizarReq):
    reg = dict(req.registro)
    reg["id"] = reg.get("id") or os.urandom(8).hex()
    meta = reg.get("meta", {})
    meta["criadoEm"] = datetime.datetime.utcnow().isoformat() + "Z"
    meta["origem"] = "teste_app"
    reg["meta"] = meta

    out = RESULT_DIR / "formulario_g.json"
    data = _safe_json_load(out)
    data.append(reg)
    _atomic_write_json(out, data)
    return {"ok": True, "arquivo": str(out), "total_registros": len(data)}

@api.get("/models/status")
def api_models_status():
    out = {}
    for perigo in sorted(TIPOS_PERIGO):
        info = _find_latest_model(perigo)
        if info:
            cfg = info.get("config", {})
            out[perigo] = {
                "ok": True,
                "timestamp": info["timestamp"],
                "modelo_path": info["modelo_path"],
                "scaler_path": info["scaler_path"],
                "features_usadas": cfg.get("features_usadas"),
            }
        else:
            out[perigo] = {"ok": False, "motivo": "nenhum modelo encontrado"}
    return {"ok": True, "modelos": out}

@api.get("/importance/top")
def api_importance_top(perigo: str, n: int = 10):
    if perigo not in TIPOS_PERIGO:
        raise HTTPException(status_code=400, detail={"erro":"tipo_perigo inválido","permitidos":sorted(TIPOS_PERIGO)})

    # procura CSVs no seu repositório ML (ajuste este caminho se preferir espelhar resultados no teste_app)
    results_dir = Path(__file__).resolve().parent.parent / "ml" / "results" / "envase_rotulagem" / perigo
    csvs = sorted(glob(str(results_dir / "permutation_importance_*.csv")))
    if not csvs:
        return {"ok": False, "motivo": "sem CSV de importance para este perigo", "path_procurado": str(results_dir)}
    latest = csvs[-1]

    df = pd.read_csv(latest).sort_values("importance_mean", ascending=False).head(n)
    top = df[["feature","importance_mean","importance_std"]].to_dict(orient="records")
    return {"ok": True, "arquivo": latest, "top": top}


app.include_router(api)

if __name__ == "__main__":
    uvicorn.run("appcc_teste_api:app", host="0.0.0.0", port=8100, reload=True)
