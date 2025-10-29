# ml/view_generators/predicao_mel.py
# ==================================
# Treino em lote (mel) por etapa × perigo + catálogo de modelos.

# >>> Backend off-screen para evitar Tkinter / GUI:
import os
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
matplotlib.use("Agg", force=True)

# from __future__ import annotations
import argparse, json, time
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score, balanced_accuracy_score
from sklearn.inspection import permutation_importance
import joblib, warnings

warnings.filterwarnings('ignore')

# -----------------------
# Constantes
# -----------------------
ETAPAS = [
    "recepcao","desoperculacao","centrifugacao","peneiragem",
    "decantacao","envase","rotulagem","armazenamento","expedicao",
    "envase_rotulagem"
]
PERIGOS = ["bio","fis","qui"]
CLASSES = {0:"DESPREZÍVEL",1:"BAIXA",2:"MÉDIA",3:"ALTA"}


# -----------------------
# Utils de caminho/IO
# -----------------------
def ts_now() -> str:
    return time.strftime("%Y%m%d_%H%M%S")

def paths(base_file: Path, data_root: Optional[str], models_dir: Optional[str], results_dir: Optional[str]):
    base = base_file.resolve().parents[1]  # .../ml/
    DATA_ROOT = Path(data_root) if data_root else (base / "dataset" / "mel")
    MODELS_DIR = Path(models_dir) if models_dir else (base / "models" / "mel")
    RESULTS_DIR = Path(results_dir) if results_dir else (base / "results" / "mel")
    return DATA_ROOT, MODELS_DIR, RESULTS_DIR

def ds_path(DATA_ROOT: Path, etapa: str, perigo: str) -> Path:
    return DATA_ROOT / etapa / perigo / f"dataset_{etapa}.csv"

def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


# -----------------------
# Treino + importance
# -----------------------
def train_one(DATA_ROOT: Path, MODELS_DIR: Path, RESULTS_DIR: Path,
              etapa: str, perigo: str,
              metric_key: str = "macro_f1",
              rf_params: Optional[Dict] = None) -> Dict:
    """
    Treina 1 modelo (etapa, perigo), salva artefatos e retorna um dict para o catálogo.
    """
    if rf_params is None:
        rf_params = dict(
            n_estimators=300, max_depth=None, min_samples_leaf=2,
            class_weight="balanced_subsample", random_state=42, n_jobs=-1
        )

    csv = ds_path(DATA_ROOT, etapa, perigo)
    if not csv.exists():
        raise FileNotFoundError(f"Dataset não encontrado: {csv}")

    df = pd.read_csv(csv)
    if "probabilidade" not in df.columns:
        raise ValueError(f"Dataset sem coluna 'probabilidade': {csv}")

    y = df["probabilidade"].astype(int)
    X = df.drop(columns=["probabilidade"])
    features = list(X.columns)

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = Pipeline([
        ("scaler", StandardScaler(with_mean=False)),
        ("clf", RandomForestClassifier(**rf_params))
    ])
    pipe.fit(X_train, y_train)

    # métricas primárias
    y_pred = pipe.predict(X_val)
    LABELS = [0, 1, 2, 3]
    metrics = {
        "balanced_accuracy": float(balanced_accuracy_score(y_val, y_pred)),
        "macro_f1": float(f1_score(y_val, y_pred, average="macro", labels=LABELS, zero_division=0)),
        "report": classification_report(y_val, y_pred, labels=LABELS, output_dict=True, zero_division=0)
    }

    # Permutation Importance (em validação)
    imp = permutation_importance(
        pipe, X_val, y_val,
        n_repeats=10, random_state=42, n_jobs=-1,
        scoring="balanced_accuracy"  # consistente com métrica de seleção
    )
    imp_df = pd.DataFrame({
        "feature": features,
        "importance_mean": imp.importances_mean,
        "importance_std": imp.importances_std
    }).sort_values("importance_mean", ascending=False)

    # Salvar artefatos
    ts = ts_now()
    out_m = ensure_dir(MODELS_DIR / etapa / perigo / ts)
    out_r = ensure_dir(RESULTS_DIR / etapa / perigo)

    pipeline_path = out_m / f"pipeline_{etapa}_{ts}.pkl"
    joblib.dump(pipe, pipeline_path)

    # opcional: salvar scaler e clf também (para APIs legadas)
    scaler_path = out_m / f"scaler_{etapa}_{ts}.pkl"
    clf_path = out_m / f"classificador_{etapa}_{ts}.pkl"
    joblib.dump(pipe.named_steps["scaler"], scaler_path)
    joblib.dump(pipe.named_steps["clf"], clf_path)

    config = {
        "etapa": etapa,
        "perigo": perigo,
        "timestamp": ts,
        "features_usadas": features,
        "classes": CLASSES,
        "metrics": metrics,
        "rf_params": rf_params
    }
    (out_m / f"config_{etapa}_{ts}.json").write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")

    # importance (csv + png)
    imp_csv = out_r / f"permutation_importance_{etapa}_{ts}.csv"
    imp_df.to_csv(imp_csv, index=False, encoding="utf-8")
    plt.figure(figsize=(8, 6))
    top = imp_df.head(15)[::-1]
    plt.barh(top["feature"], top["importance_mean"])
    plt.xlabel("Permutation Importance (mean)")
    plt.title(f"Top features • {etapa}/{perigo.upper()} • {ts}")
    plt.tight_layout()
    imp_png = out_r / f"permutation_importance_{etapa}_{ts}.png"
    plt.savefig(imp_png, dpi=200)
    plt.close()

    # Registro para catálogo
    entry = {
        "etapa": etapa,
        "perigo": perigo,
        "timestamp": ts,
        "model_dir": str(out_m),
        "pipeline_path": str(pipeline_path),
        "scaler_path": str(scaler_path),
        "classifier_path": str(clf_path),
        "config_path": str(out_m / f"config_{etapa}_{ts}.json"),
        "importance_csv": str(imp_csv),
        "importance_png": str(imp_png),
        "features_usadas": features,
        "metrics": metrics,
        "metric_for_selection": metric_key,
        "metric_value": float(metrics.get(metric_key, 0.0)),
        "top_features": imp_df.head(10).to_dict(orient="records")
    }
    return entry


# -----------------------
# Catálogo
# -----------------------
def scan_all_models(MODELS_DIR: Path) -> List[Dict]:
    """
    Lê todos os config_*.json existentes e retorna entries.
    """
    entries: List[Dict] = []
    if not MODELS_DIR.exists():
        return entries
    for etapa_dir in MODELS_DIR.iterdir():
        if not etapa_dir.is_dir():
            continue
        for perigo_dir in etapa_dir.iterdir():
            if not perigo_dir.is_dir():
                continue
            for run_dir in sorted([p for p in perigo_dir.iterdir() if p.is_dir()]):
                cfgs = list(run_dir.glob("config_*.json"))
                if not cfgs:
                    continue
                try:
                    cfg = json.loads(cfgs[0].read_text(encoding="utf-8"))
                except Exception:
                    continue
                ts = cfg.get("timestamp") or run_dir.name
                pipeline_path = next(run_dir.glob("pipeline_*.pkl"), None)
                scaler_path = next(run_dir.glob("scaler_*.pkl"), None)
                clf_path = next(run_dir.glob("classificador_*.pkl"), None)
                entries.append({
                    "etapa": cfg.get("etapa"),
                    "perigo": cfg.get("perigo"),
                    "timestamp": ts,
                    "model_dir": str(run_dir),
                    "pipeline_path": str(pipeline_path) if pipeline_path else None,
                    "scaler_path": str(scaler_path) if scaler_path else None,
                    "classifier_path": str(clf_path) if clf_path else None,
                    "config_path": str(cfgs[0]),
                    "features_usadas": cfg.get("features_usadas"),
                    "metrics": cfg.get("metrics", {}),
                })
    return entries

def select_best_by_combo(entries: List[Dict], metric_key: str = "macro_f1") -> Dict[str, Dict]:
    """
    Para cada combinação etapa:perigo escolhe o item com melhor 'metric_key'.
    """
    best: Dict[str, Dict] = {}
    for e in entries:
        combo = f"{e.get('etapa')}:{e.get('perigo')}"
        val = float(e.get("metrics", {}).get(metric_key, 0.0))
        cur = best.get(combo)
        if cur is None or val > float(cur.get("metric_value", -1)):
            best[combo] = {
                "etapa": e.get("etapa"),
                "perigo": e.get("perigo"),
                "timestamp": e.get("timestamp"),
                "metric": metric_key,
                "metric_value": val,
                "model_dir": e.get("model_dir"),
                "pipeline_path": e.get("pipeline_path"),
                "scaler_path": e.get("scaler_path"),
                "classifier_path": e.get("classifier_path"),
                "config_path": e.get("config_path"),
            }
    return best

def write_catalog(MODELS_DIR: Path, RESULTS_DIR: Path, DATA_ROOT: Path,
                  entries: List[Dict], metric_key: str = "macro_f1") -> Path:
    best = select_best_by_combo(entries, metric_key=metric_key)
    catalog = {
        "generated_at": ts_now(),
        "roots": {
            "models_dir": str(MODELS_DIR),
            "results_dir": str(RESULTS_DIR),
            "data_root": str(DATA_ROOT)
        },
        "metric_for_selection": metric_key,
        "total_entries": len(entries),
        "entries": entries,
        "best_by_combo": best
    }
    out = ensure_dir(MODELS_DIR) / "catalog.json"
    out.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


# -----------------------
# CLI
# -----------------------
def main():
    ap = argparse.ArgumentParser(description="Treina modelos (mel) por etapa × perigo e gera models/catalog.json")
    ap.add_argument("--etapa", choices=ETAPAS+["all"], required=True)
    ap.add_argument("--perigo", choices=PERIGOS+["all"], required=True)
    ap.add_argument("--metric", choices=["macro_f1","balanced_accuracy"], default="macro_f1",
                    help="Métrica para seleção no catálogo")
    ap.add_argument("--data_root", default=None, help="Default: ml/dataset/mel (relativo a este arquivo)")
    ap.add_argument("--models_dir", default=None, help="Default: ml/models/mel (relativo a este arquivo)")
    ap.add_argument("--results_dir", default=None, help="Default: ml/results/mel (relativo a este arquivo)")
    ap.add_argument("--only_scan", action="store_true", help="Não treina; apenas varre e atualiza o catalog.json")
    args = ap.parse_args()

    DATA_ROOT, MODELS_DIR, RESULTS_DIR = paths(Path(__file__), args.data_root, args.models_dir, args.results_dir)

    etapas = ETAPAS if args.etapa == "all" else [args.etapa]
    perigos = PERIGOS if args.perigo == "all" else [args.perigo]

    new_entries: List[Dict] = []
    failures: List[Dict] = []

    if not args.only_scan:
        for e in etapas:
            for p in perigos:
                try:
                    print(f"▶ Treinando {e}/{p} …")
                    entry = train_one(DATA_ROOT, MODELS_DIR, RESULTS_DIR, e, p, metric_key=args.metric)
                    new_entries.append(entry)
                    print(f"   ✓ {e}/{p} -> {entry['model_dir']}  ({args.metric}={entry['metric_value']:.3f})")
                except Exception as ex:
                    print(f"   ✗ ERRO {e}/{p}: {ex}")
                    failures.append({"etapa": e, "perigo": p, "erro": str(ex)})

    # varrer TODOS os modelos (inclui novos e antigos)
    scanned = scan_all_models(MODELS_DIR)

    # garantir inclusão dos recém-treinados no scan final
    if new_entries:
        scanned_map = {(x["etapa"], x["perigo"], x["timestamp"]): x for x in scanned}
        for ne in new_entries:
            scanned_map[(ne["etapa"], ne["perigo"], ne["timestamp"])] = {
                **scanned_map.get((ne["etapa"], ne["perigo"], ne["timestamp"]), {}),
                **ne
            }
        scanned = list(scanned_map.values())

    cat_path = write_catalog(MODELS_DIR, RESULTS_DIR, DATA_ROOT, scanned, metric_key=args.metric)
    print(f"\n✅ Catálogo atualizado: {cat_path}")

    if failures:
        print("\n⚠ Combinações com erro:")
        for f in failures:
            print(f" - {f['etapa']}/{f['perigo']}: {f['erro']}")

if __name__ == "__main__":
    main()
