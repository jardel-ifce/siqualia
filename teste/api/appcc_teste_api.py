# teste/api/appcc_teste_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from json import JSONDecodeError
import json, uuid, datetime, sys, os, tempfile, shutil

# ========================
# Caminhos (ambiente TESTE)
# ========================
ROOT = Path(__file__).resolve().parents[1]      # teste/
STATIC_DIR = ROOT / "static"
DATA_DIR = ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
RESULT_DIR = DATA_DIR / "resultados"
for d in (STATIC_DIR, CACHE_DIR, RESULT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ========================
# Preditor (predicao_mel.py)
# ========================
pm = None
try:
    # Ajuste conforme a posição real do arquivo predicao_mel.py
    sys.path.append(str(ROOT.parents[0]))  # sobe até o projeto raiz
    import predicao_mel as pm
except Exception as e:
    print("[AVISO] predicao_mel.py não importado; será usado fallback:", e)

# Ordem/nomes das features esperadas pelo modelo de MEL
FEATURES = [
    "tipo_embalagem","estado_embalagem","tampa_correta","vedacao_adequada",
    "higienizacao_previa","uso_epi","local_envase","manipulador_higiene",
    "aspecto_visual","umidade_mel","temperatura_envase","cristalizacao",
    "rotulo_presente","informacoes_completas","data_validade_legivel","lote_identificado",
    "treinamento_equipe","historico_reclamacoes","registro_lote","tempo_exposicao_ar"
]

CLASSES = ["DESPREZÍVEL","BAIXA","MÉDIA","ALTA"]  # ordinal 0..3

# ========================
# Utils JSON seguros
# ========================
def safe_json_load(path: Path):
    """Lê JSON; se não existir, estiver vazio ou inválido, retorna []."""
    if not path.exists():
        return []
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            return []
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except (JSONDecodeError, OSError, ValueError) as e:
        print(f"[WARN] JSON inválido em {path.name}: {e} → iniciando lista vazia")
        return []

def atomic_write_json(path: Path, data):
    """Escreve JSON de forma atômica (tmp + rename)."""
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

# ========================
# FastAPI
# ========================
app = FastAPI(title="APPCC – Assistente (Teste)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# Servir estáticos e página
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def homepage():
    return FileResponse(str(STATIC_DIR / "appcc_teste.html"))

# ========================
# Schemas
# ========================
class PredicaoReq(BaseModel):
    bpfRespostas: dict

class RiscoReq(BaseModel):
    probabilidade: str
    severidade: str

class SaveCacheReq(BaseModel):
    sessionId: str
    state: dict

class FinalizarReq(BaseModel):
    sessionId: str
    registro: dict

# ========================
# Núcleo: predição
# ========================
def _prepare_sample(bpf: dict) -> dict:
    """Reordena/garante as FEATURES."""
    return {k: bpf.get(k) for k in FEATURES}

def _map_class_index_to_name(idx: int) -> str:
    try:
        return CLASSES[int(idx)]
    except Exception:
        return "MÉDIA"

def _ordinal_score_from_class(name: str) -> float:
    # DESPREZÍVEL=0, BAIXA=1, MÉDIA=2, ALTA=3 → normalizado [0,1]
    name = (name or "").upper()
    mapping = {"DESPREZÍVEL":0, "BAIXA":1, "MÉDIA":2, "ALTA":3}
    v = mapping.get(name, 2)
    return v / 3.0

def _predict_with_model(sample: dict):
    """
    Retorna dict:
    {
      'prob_classe': 'DESPREZÍVEL|BAIXA|MÉDIA|ALTA',
      'prob_score': 0..1 (ordinal normalizado),
      'fonte': 'modelo'|'fallback'|'fallback-erro',
      'modelo': <timestamp>|None
    }
    """
    # Fallback heurístico leve
    if pm is None:
        uso_epi = int(sample.get("uso_epi", 2))                 # 0/1/2 (0 pior)
        estado_emb = int(sample.get("estado_embalagem", 1))     # 0/1   (0 pior)
        recl = int(sample.get("historico_reclamacoes", 2))      # 0/1/2 (0 pior)
        score = (2 - uso_epi) + (1 - estado_emb) + (2 - recl)   # 0..5
        cls = CLASSES[min(max(score, 0), 3)]
        return {"prob_classe": cls, "prob_score": _ordinal_score_from_class(cls),
                "fonte": "fallback", "modelo": None}

    # Predição real
    try:
        modelos_por_algo = pm.listar_modelos_por_algoritmo()
        prefer = ["Random Forest", "Gradient Boosting", "SVM", "Regressão Logística"]
        escolhido = None
        for alg in prefer:
            if alg in modelos_por_algo and modelos_por_algo[alg]:
                escolhido = max(modelos_por_algo[alg], key=lambda x: x["timestamp"])
                break
        if not escolhido:
            raise RuntimeError("Sem modelos disponíveis")
        modelo, scaler = pm.carregar_modelo_direto(escolhido)

        # DataFrame de 1 linha
        import pandas as pd
        df = pd.DataFrame([sample])
        X = scaler.transform(df)

        # Classe
        pred_idx = int(modelo.predict(X)[0])
        cls = _map_class_index_to_name(pred_idx)

        # Score ordinal usando predict_proba se disponível
        score = _ordinal_score_from_class(cls)
        if hasattr(modelo, "predict_proba"):
            try:
                proba = modelo.predict_proba(X)[0]  # array [p0,p1,p2,p3]
                # expectativa do índice (0..3) → normaliza /3
                expected = sum(i * float(proba[i]) for i in range(min(len(proba), 4))) / 3.0
                # clamp 0..1
                score = max(0.0, min(1.0, expected))
            except Exception:
                pass

        return {"prob_classe": cls, "prob_score": float(score),
                "fonte": "modelo", "modelo": escolhido["config"]["timestamp"]}
    except Exception as e:
        print("[_predict_with_model] erro:", e)
        # fallback em erro
        return {"prob_classe": "MÉDIA", "prob_score": _ordinal_score_from_class("MÉDIA"),
                "fonte": "fallback-erro", "modelo": None}

# ========================
# Matriz de risco
# ========================
def calcula_risco(prob: str, sev: str) -> str:
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

def exige_medidas(risco: str) -> bool:
    return risco not in ("Desprezível", "Desconhecido")

# ========================
# Endpoints
# ========================
@app.post("/api/predicao")
def api_predicao(req: PredicaoReq):
    sample = _prepare_sample(req.bpfRespostas)
    out = _predict_with_model(sample)
    # também oferecemos compat com endpoint antigo:
    # probabilidade = prob_classe
    return {
        "prob_classe": out["prob_classe"],
        "prob_score": out["prob_score"],
        "fonte": out["fonte"],
        "modelo": out["modelo"],
        "probabilidade": out["prob_classe"],  # compat
    }

# Alias compatível com versões anteriores (/api/probabilidade)
@app.post("/api/probabilidade")
def api_probabilidade(req: PredicaoReq):
    return api_predicao(req)

@app.post("/api/risco")
def api_risco(req: RiscoReq):
    r = calcula_risco(req.probabilidade, req.severidade)
    return {"risco": r, "exige_medidas": exige_medidas(r)}

@app.post("/api/cache/salvar")
def api_cache_salvar(req: SaveCacheReq):
    (CACHE_DIR / f"{req.sessionId}.json").write_text(
        json.dumps(req.state, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"ok": True}

@app.get("/api/cache/abrir")
def api_cache_abrir(sessionId: str):
    p = CACHE_DIR / f"{sessionId}.json"
    if p.exists():
        return {"ok": True, "state": json.loads(p.read_text(encoding="utf-8"))}
    return {"ok": True, "state": {}}

@app.post("/api/finalizar")
def api_finalizar(req: FinalizarReq):
    reg = dict(req.registro)
    reg["id"] = str(uuid.uuid4())
    reg["meta"] = {
        **reg.get("meta", {}),
        "criadoEm": datetime.datetime.utcnow().isoformat() + "Z",
        "origem": "teste",
    }
    out = RESULT_DIR / "formulario_g.json"
    data = safe_json_load(out)
    data.append(reg)
    atomic_write_json(out, data)
    return {"ok": True, "arquivo": str(out), "total_registros": len(data)}

# Execução:
# uvicorn api.appcc_teste_api:app --reload --port 8100
# Abra: http://127.0.0.1:8100/
