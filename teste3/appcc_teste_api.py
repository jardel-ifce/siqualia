# appcc_teste_api.py
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response

# =========================================================
# Schema externo (planejado/curado)
# =========================================================
try:
    from ml.feature_schema import (
        ETAPAS as _ETAPAS_LIST,
        PERIGOS as _PERIGOS_LIST,
        CLASSES,
        schema_for_etapa as _schema_for_etapa_ext,
    )
    ETAPAS = set(_ETAPAS_LIST)
    PERIGOS = set(_PERIGOS_LIST)
except Exception as e:
    print(f"[SIQ] ⚠️ Não foi possível importar ml.feature_schema: {e}")
    ETAPAS = {
        "recepcao", "desoperculacao", "centrifugacao", "peneiragem",
        "decantacao", "envase", "rotulagem", "armazenamento", "expedicao",
        "envase_rotulagem"
    }
    PERIGOS = {"bio", "fis", "qui"}
    CLASSES = {0: "DESPREZÍVEL", 1: "BAIXA", 2: "MÉDIA", 3: "ALTA"}

# =========================================================
# App FastAPI + CORS
# =========================================================
app = FastAPI(title="SIQUALIA • API de Teste", version="0.5")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "siq_config.json"

# --------- Config em runtime (sem env) ----------
def _default_paths() -> Dict[str, str]:
    return {
        "catalog_path": str(BASE_DIR / "ml" / "models" / "mel" / "catalog.json"),
        "results_dir":  str(BASE_DIR / "ml" / "results" / "mel"),
        "static_dir":   str(BASE_DIR / "static"),
    }

CONFIG: Dict[str, str] = _default_paths()

def _load_config_file() -> None:
    global CONFIG
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                CONFIG.update({k: str(v) for k, v in data.items() if k in _default_paths()})
        except Exception as e:
            print(f"[SIQ] ⚠️ Falha ao ler {CONFIG_FILE}: {e}")

def _save_config_file() -> None:
    try:
        CONFIG_FILE.write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        print(f"[SIQ] ⚠️ Falha ao salvar {CONFIG_FILE}: {e}")

_load_config_file()

def _p(path_key: str) -> Path:
    return Path(CONFIG[path_key]).expanduser().resolve()

def _ensure_parent_dir(p: Path):
    p.parent.mkdir(parents=True, exist_ok=True)

# Caminhos ativos (sempre lidos de CONFIG)
def CATALOG_PATH() -> Path:
    return _p("catalog_path")

def RESULTS_DIR() -> Path:
    return _p("results_dir")

def STATIC_DIR() -> Path:
    return _p("static_dir")

print(f"[SIQ] CATALOGO: {CATALOG_PATH()}")
print(f"[SIQ] RESULTS : {RESULTS_DIR()}")
print(f"[SIQ] STATIC  : {STATIC_DIR()}")

# =========================================================
# Cache simples do catálogo
# =========================================================
_catalog: Optional[Dict[str, Any]] = None
_catalog_mtime: Optional[float] = None

def _clear_catalog_cache():
    global _catalog, _catalog_mtime
    _catalog = None
    _catalog_mtime = None

def _load_catalog() -> Optional[Dict[str, Any]]:
    """Lê e faz cache do catalog.json."""
    global _catalog, _catalog_mtime
    cat_path = CATALOG_PATH()
    if not cat_path.exists():
        return None
    mt = cat_path.stat().st_mtime
    if (_catalog is None) or (mt != _catalog_mtime):
        _catalog = json.loads(cat_path.read_text(encoding="utf-8"))
        _catalog_mtime = mt
        print(f"[SIQ] catalog.json recarregado (mtime={_catalog_mtime})")
    return _catalog

def _get_best_combo(etapa: str, perigo: str) -> Optional[Dict[str, Any]]:
    """Retorna o melhor modelo (segundo o catálogo) para etapa×perigo,
    enriquecido com features e paths de importance."""
    cat = _load_catalog()
    if not cat:
        return None
    key = f"{etapa}:{perigo}"
    best = cat.get("best_by_combo", {}).get(key)
    if not best:
        return None
    ts = best.get("timestamp")
    for e in cat.get("entries", []):
        if e.get("etapa") == etapa and e.get("perigo") == perigo and e.get("timestamp") == ts:
            best = {
                **best,
                "features_usadas": e.get("features_usadas"),
                "pipeline_path": e.get("pipeline_path"),
                "importance_csv": e.get("importance_csv"),
                "importance_png": e.get("importance_png"),
            }
            break
    return best

def _find_latest_importance_csv(etapa: str, perigo: str, ts: Optional[str] = None) -> Optional[Path]:
    """Procura um CSV de permutation_importance em RESULTS_DIR/<etapa>/<perigo>/ mais recente."""
    base = RESULTS_DIR() / etapa / perigo
    if not base.exists():
        return None
    candidates: List[Path] = sorted(
        base.glob("permutation_importance_*.csv"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    if not candidates:
        return None
    if ts:
        for c in candidates:
            if ts in c.name:
                return c
    return candidates[0]

# =========================================================
# Helpers de rótulo e auto-metadados (fallback seguro)
# =========================================================
def _humanize(key: str) -> str:
    s = key.replace("_", " ").strip()
    s = s.replace(" pct", " (%)").replace(" c", " (°C)").replace(" h", " (h)").replace(" min", " (min)")
    return " ".join([w.capitalize() for w in s.split()])

def _infer_meta_from_name(feat: str) -> dict:
    f = feat.lower()
    if (
        f.endswith(("_ok", "_integro", "_integra", "_presente"))
        or f.startswith(("has_", "tem_", "is_", "possui_"))
        or "identificado" in f or "identificacao" in f
        or "registro" in f or "registrado" in f
        or "lacres" in f or "lacre" in f
        or "presenca" in f or "presente" in f
    ):
        return {"type": "enum", "label": _humanize(feat),
                "options": [{"label": "Não", "value": 0}, {"label": "Sim", "value": 1}]}
    if (
        f.startswith(("higienizacao_", "higiene_", "treinamento_", "ventilacao_", "integridade_", "condicao_", "condição_"))
        or f.endswith("_risco") or "risco_" in f
        or f.startswith(("material_", "superficie_", "cruzamento_", "separacao_", "separação_"))
    ):
        return {"type": "enum", "label": _humanize(feat),
                "options": [{"label": "Baixo", "value": 0}, {"label": "Médio", "value": 1}, {"label": "Alto", "value": 2}]}
    if f.endswith(("_pct", "_percent", "_porcent")) or "umidade" in f or "pct" in f:
        return {"type": "range", "label": _humanize(feat), "unit": "%", "min": 0, "max": 100, "step": 1}
    if f.endswith("_c") or "temperatura" in f:
        return {"type": "range", "label": _humanize(feat), "unit": "°C", "min": 0, "max": 80, "step": 1}
    if f.endswith("_h") or "horas" in f:
        return {"type": "range", "label": _humanize(feat), "unit": "h", "min": 0, "max": 240, "step": 1}
    if f.endswith("_min") or "minuto" in f:
        return {"type": "range", "label": _humanize(feat), "unit": "min", "min": 0, "max": 180, "step": 1}
    if f.endswith("_dias") or "dia" in f:
        return {"type": "range", "label": _humanize(feat), "unit": "dias", "min": 0, "max": 365, "step": 1}
    return {"type": "range", "label": _humanize(feat), "min": 0, "max": 10, "step": 1}

def _augment_schema_for_features(schema: dict, features: List[str]) -> dict:
    out = {}
    for k in features:
        if k in schema:
            m = dict(schema[k])
            m.setdefault("label", _humanize(k))
            out[k] = m
        else:
            out[k] = _infer_meta_from_name(k)
    return out

# =========================================================
# Front dinâmico (sem StaticFiles fixo)
# =========================================================
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def app_index():
    index_file = STATIC_DIR() / "appcc_teste.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse(f"""
    <html><body style="font-family:system-ui;padding:20px">
      <h1>SIQUALIA • Teste Front</h1>
      <p>Coloque seu <code>appcc_teste.html</code> em: <code>{STATIC_DIR()}</code></p>
      <ul>
        <li>CSS: <code>/static/appcc_teste.css</code></li>
        <li>JS : <code>/static/appcc_teste.js</code></li>
      </ul>
      <p>Catálogo: <code>{CATALOG_PATH()}</code></p>
    </body></html>
    """, status_code=200)

@app.get("/static/{path:path}", include_in_schema=False)
def serve_static(path: str):
    file_path = STATIC_DIR() / path
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(404, "arquivo estático não encontrado")
    return FileResponse(str(file_path))

# =========================================================
# API
# =========================================================
api = APIRouter(prefix="/api", tags=["SIQ"])

@api.get("/health")
def api_health():
    return {
        "ok": True,
        "catalog_path": str(CATALOG_PATH()),
        "results_dir": str(RESULTS_DIR()),
        "static_dir": str(STATIC_DIR()),
    }

@api.get("/config")
def api_get_config():
    return {"ok": True, **CONFIG}

@api.post("/config")
def api_set_config(body: Dict[str, Any]):
    """
    Altera caminhos em runtime. Exemplo body:
    {
      "catalog_path": "/abs/.../catalog.json",
      "results_dir": "/abs/.../results/mel",
      "static_dir": "/abs/.../static",
      "persist": true   # opcional: salva em siq_config.json
    }
    """
    changed = {}
    persist = bool(body.get("persist", False))

    if "catalog_path" in body:
        p = Path(str(body["catalog_path"])).expanduser().resolve()
        if not p.exists():
            raise HTTPException(400, f"catalog_path não existe: {p}")
        CONFIG["catalog_path"] = str(p); changed["catalog_path"] = str(p)
        _clear_catalog_cache()

    if "results_dir" in body:
        p = Path(str(body["results_dir"])).expanduser().resolve()
        if not p.exists():
            raise HTTPException(400, f"results_dir não existe: {p}")
        CONFIG["results_dir"] = str(p); changed["results_dir"] = str(p)

    if "static_dir" in body:
        p = Path(str(body["static_dir"])).expanduser().resolve()
        if not p.exists():
            raise HTTPException(400, f"static_dir não existe: {p}")
        CONFIG["static_dir"] = str(p); changed["static_dir"] = str(p)

    if persist and changed:
        _save_config_file()

    return {"ok": True, "changed": changed, **CONFIG, "persisted": bool(persist and changed)}

def _get_best_combo(etapa: str, perigo: str) -> Optional[Dict[str, Any]]:
    # (mesma função, duplicada aqui apenas por ordenação do arquivo)
    cat = _load_catalog()
    if not cat:
        return None
    key = f"{etapa}:{perigo}"
    best = cat.get("best_by_combo", {}).get(key)
    if not best:
        return None
    ts = best.get("timestamp")
    for e in cat.get("entries", []):
        if e.get("etapa") == etapa and e.get("perigo") == perigo and e.get("timestamp") == ts:
            best = {**best, **{
                "features_usadas": e.get("features_usadas"),
                "pipeline_path": e.get("pipeline_path"),
                "importance_csv": e.get("importance_csv"),
                "importance_png": e.get("importance_png"),
            }}
            break
    return best

@api.get("/models/catalog")
def api_models_catalog():
    cat = _load_catalog()
    if not cat:
        raise HTTPException(404, detail={"erro": "catálogo ausente", "path": str(CATALOG_PATH())})
    return {
        "ok": True,
        "metric": cat.get("metric_for_selection"),
        "generated_at": cat.get("generated_at"),
        "best_by_combo": cat.get("best_by_combo"),
        "total_entries": cat.get("total_entries", 0),
    }

@api.get("/models/status")
def api_models_status(etapa: Optional[str] = None):
    cat = _load_catalog()
    if not cat:
        raise HTTPException(404, detail={"erro": "catálogo ausente", "path": str(CATALOG_PATH())})

    etapas = [etapa] if (etapa and etapa in ETAPAS) else sorted(ETAPAS)
    out: Dict[str, Dict[str, Any]] = {}
    for e in etapas:
        out[e] = {}
        for p in sorted(PERIGOS):
            best = _get_best_combo(e, p)
            out[e][p] = {"ok": bool(best)}
            if best:
                out[e][p].update({
                    "timestamp": best.get("timestamp"),
                    "pipeline_path": best.get("pipeline_path"),
                    "features_usadas": best.get("features_usadas"),
                })
    return {"ok": True, "modelos": out}

@api.get("/features/schema")
def api_features_schema(
    etapa: str,
    perigo: str,
    only_model_features: bool = True,
    augment: bool = True,
    only_perigo: bool = False
):
    etapa = (etapa or "").strip().lower()
    perigo = (perigo or "").strip().lower()
    if etapa not in ETAPAS:
        raise HTTPException(400, "etapa inválida")
    if perigo not in PERIGOS:
        raise HTTPException(400, "tipo_perigo inválido")

    # Base do schema (curado) – pode filtrar por aplicabilidade do perigo
    try:
        base_schema = _schema_for_etapa_ext(etapa, perigo if only_perigo else None, only_perigo)  # type: ignore
    except Exception:
        base_schema = {}

    best = _get_best_combo(etapa, perigo)
    feats = best.get("features_usadas") if best else None

    top_info = {}
    if best:
        csvp = best.get("importance_csv")
        if not csvp or not Path(csvp).exists():
            probe = _find_latest_importance_csv(etapa, perigo, ts=best.get("timestamp"))
            if probe:
                csvp = str(probe)
        if csvp and Path(csvp).exists():
            df = pd.read_csv(csvp).sort_values("importance_mean", ascending=False)
            order = df["feature"].tolist()
            nonzero = int((df["importance_mean"] > 0).sum())
            recommended_n = int(np.clip(nonzero if nonzero > 0 else min(8, len(order)),
                                        3, max(3, min(12, len(order)))))
            top_info = {"importance_csv": csvp, "order": order, "recommended_n": recommended_n}

    # Filtra para só as features do modelo, se pedido
    if only_model_features and feats:
        schema = {k: v for k, v in base_schema.items() if k in feats}
    else:
        schema = dict(base_schema)

    # Garante metadados de tudo que o modelo usa (labels, units, etc.)
    if augment:
        schema = _augment_schema_for_features(schema, feats or list(schema.keys()))

    return {"ok": True, "schema": schema, **({"topn": top_info} if top_info else {})}

@api.get("/importance/top")
def api_importance_top(etapa: str, perigo: str, n: int | None = None):
    etapa = (etapa or "").strip().lower()
    perigo = (perigo or "").strip().lower()
    if etapa not in ETAPAS:
        raise HTTPException(400, "etapa inválida")
    if perigo not in PERIGOS:
        raise HTTPException(400, "tipo_perigo inválido")

    best = _get_best_combo(etapa, perigo)
    if not best:
        raise HTTPException(404, "modelo não encontrado no catálogo")

    csvp = best.get("importance_csv")
    if not csvp or not Path(csvp).exists():
        probe = _find_latest_importance_csv(etapa, perigo, ts=best.get("timestamp"))
        if not probe:
            raise HTTPException(404, "CSV de importance não encontrado")
        csvp = str(probe)

    df = pd.read_csv(csvp).sort_values("importance_mean", ascending=False)
    order = df["feature"].tolist()
    nonzero = (df["importance_mean"] > 0).sum()
    recommended_n = int(np.clip(nonzero if nonzero > 0 else min(8, len(order)), 3, min(12, len(order))))
    use_n = int(n) if (isinstance(n, int) and n and n > 0) else recommended_n

    top = df.head(use_n).to_dict(orient="records")
    return {"ok": True, "arquivo": str(csvp), "recommended_n": recommended_n, "top": top, "order": order}

@api.post("/predicao")
def api_predicao(body: Dict[str, Any]):
    etapa = (body.get("etapa") or "").strip().lower()
    perigo = (body.get("tipo_perigo") or "").strip().lower()
    bpf = body.get("bpfRespostas") or {}

    if etapa not in ETAPAS:
        raise HTTPException(400, detail={"erro": "etapa inválida", "permitidos": sorted(ETAPAS)})
    if perigo not in PERIGOS:
        raise HTTPException(400, detail={"erro": "tipo_perigo inválido", "permitidos": sorted(PERIGOS)})

    best = _get_best_combo(etapa, perigo)
    if not best:
        raise HTTPException(404, detail={"erro": "modelo não encontrado no catálogo", "etapa": etapa, "perigo": perigo})

    pipe_path = best.get("pipeline_path")
    feats = best.get("features_usadas") or []
    if not pipe_path or not feats:
        raise HTTPException(500, detail={"erro": "modelo/feats ausentes no catálogo", "best": best})

    pipe = joblib.load(pipe_path)

    row = {k: bpf.get(k, np.nan) for k in feats}
    X = pd.DataFrame([row], columns=feats).apply(pd.to_numeric, errors="coerce")
    if X.isna().any().any():
        faltam = X.columns[X.isna().any()].tolist()
        raise HTTPException(422, detail={"erro": "campos ausentes/invalidos", "faltando": faltam})

    pred_idx = int(pipe.predict(X)[0])
    cls = CLASSES.get(pred_idx, str(pred_idx))

    prob_score = 0.0
    probs = None
    if hasattr(pipe, "predict_proba"):
        proba = pipe.predict_proba(X)[0]
        probs = {CLASSES.get(i, str(i)): float(proba[i]) for i in range(len(proba))}
        denom = max(1.0, 3.0)
        expected = sum(i * float(proba[i]) for i in range(min(4, len(proba)))) / denom
        prob_score = max(0.0, min(1.0, expected))

    return {
        "ok": True, "fonte": "catalog", "modelo": best.get("timestamp"),
        "tipo_perigo": perigo, "etapa": etapa,
        "features_usadas": feats,
        "prob_classe": cls, "probabilidade": cls,
        "prob_score": round(float(prob_score), 4),
        "probs": probs
    }

# registra o router
app.include_router(api)

# Execução direta (dev)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("appcc_teste_api:app", host="0.0.0.0", port=8100, reload=True)
