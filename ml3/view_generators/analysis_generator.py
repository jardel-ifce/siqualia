# ml/view_generators/analysis_generator.py
"""
GERADOR DE ANÁLISES - PRODUÇÃO DE MEL (Multi-etapas)
====================================================
Analisa todos os datasets gerados em: ml/dataset/mel/<etapa>/<perigo>/dataset_<etapa>.csv
Gera PNGs, CSV resumo e um index.html de navegação.
"""

from __future__ import annotations
import os, argparse, json
from pathlib import Path
from typing import List, Tuple, Dict, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# Config
# ---------------------------
ETAPAS = [
    "recepcao","desoperculacao","centrifugacao","peneiragem",
    "decantacao","envase","rotulagem","armazenamento","expedicao",
    "envase_rotulagem"  # alias histórico
]
PERIGOS = ["bio","fis","qui"]
CLASSES = {0:"DESPREZÍVEL", 1:"BAIXA", 2:"MÉDIA", 3:"ALTA"}


# ---------------------------
# Util
# ---------------------------
def _ds_path(root: Path, etapa: str, perigo: str) -> Path:
    return root / etapa / perigo / f"dataset_{etapa}.csv"

def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p

def _fmt_pct(v: float) -> str: return f"{v:.1f}%"

def _safe_corr(df: pd.DataFrame) -> pd.DataFrame:
    # corr apenas com colunas numéricas
    num = df.select_dtypes(include=[np.number])
    if num.shape[1] < 2:
        return pd.DataFrame()
    return num.corr()


# ---------------------------
# Blocos de análise (reaproveitam a sua lógica anterior)
# ---------------------------
def analisar_distribuicoes(df: pd.DataFrame, titulo="Dataset") -> Dict:
    out = {}
    out["shape"] = tuple(df.shape)
    out["nulos"] = int(df.isnull().sum().sum())
    out["duplicados"] = int(df.duplicated().sum())

    if "probabilidade" in df.columns:
        dist = df["probabilidade"].value_counts().sort_index()
        total = len(df)
        out["dist_target"] = {CLASSES.get(int(i), str(i)): int(c) for i, c in dist.items()}
        out["dist_target_pct"] = {k: (v/total)*100 for k, v in out["dist_target"].items()}
    return out

def analisar_correlacoes(df: pd.DataFrame) -> Dict:
    out = {"top_corr": [], "pairs_high": []}
    if "probabilidade" in df.columns:
        corr = _safe_corr(df)
        if not corr.empty and "probabilidade" in corr.columns:
            s = corr["probabilidade"].drop("probabilidade", errors="ignore").abs().sort_values(ascending=False)
            out["top_corr"] = [(k, float(v)) for k, v in s.head(10).items()]
            # pares altos entre features
            pairs = []
            cols = list(corr.columns)
            for i in range(len(cols)):
                for j in range(i+1, len(cols)):
                    r = corr.iloc[i, j]
                    if abs(r) > 0.7 and cols[i] != "probabilidade" and cols[j] != "probabilidade":
                        pairs.append((cols[i], cols[j], float(r)))
            out["pairs_high"] = pairs
    return out

def analisar_impactos_criticos(df: pd.DataFrame) -> Dict:
    out = {"impactos_cat": {}, "impacto_tempo_exposicao": {}}
    if "probabilidade" not in df.columns:
        return out

    attrs = ["higienizacao_previa","uso_epi","vedacao_adequada","aspecto_visual","rotulo_presente"]
    for attr in attrs:
        if attr in df.columns:
            g = df.groupby(attr)["probabilidade"].agg(["count","mean","std"])
            out["impactos_cat"][attr] = g.round(3).reset_index().to_dict(orient="records")

    if "tempo_exposicao_ar" in df.columns:
        df_ = df.copy()
        df_["tempo_categoria"] = pd.cut(
            df_["tempo_exposicao_ar"], bins=[0, 15, 30, 45, 100],
            labels=["Baixo(≤15min)","Médio(15–30)","Alto(30–45)","Crítico(>45)"]
        )
        g = df_.groupby("tempo_categoria", observed=False)["probabilidade"].agg(["count","mean"]).round(3)
        out["impacto_tempo_exposicao"] = g.reset_index().to_dict(orient="records")
    return out

def analisar_qualidade_dados(df: pd.DataFrame) -> Dict:
    out = {}
    total_cells = df.shape[0] * df.shape[1]
    missing = int(df.isnull().sum().sum())
    out["completude_pct"] = 100.0 * (total_cells - missing) / total_cells if total_cells else 100.0
    out["duplicados"] = int(df.duplicated().sum())

    numericas = df.select_dtypes(include=[np.number]).columns
    out["outliers_iqr"] = []
    for col in numericas:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR = Q3 - Q1
        lb, ub = Q1 - 1.5*IQR, Q3 + 1.5*IQR
        n_out = int(((df[col] < lb) | (df[col] > ub)).sum())
        if n_out > 0:
            out["outliers_iqr"].append({"coluna": col, "outliers": n_out, "pct": 100*n_out/len(df)})
    if "probabilidade" in df.columns:
        dist = df["probabilidade"].value_counts().sort_index()
        if len(dist) and dist.min() > 0:
            out["ratio_max_min"] = float(dist.max() / dist.min())
        else:
            out["ratio_max_min"] = float("inf")
    return out


def gerar_visualizacoes(df: pd.DataFrame, titulo: str, out_dir: Path) -> Path:
    """
    Gera um grid 2x3 de gráficos adaptativos:
      (0,0) Distribuição da classe
      (0,1) Binária x classe  (higienizacao_previa; se não houver, escolhe binária "top")
      (0,2) Distribuição numérica (uso_epi; se não houver, escolhe numérica "top")
      (1,0) Hist numérica por classe (tempo_exposicao_ar; senão, numérica "top")
      (1,1) Heatmap de correlação (top features)
      (1,2) Boxplot numérica por classe (tempo_exposicao_ar; senão, numérica "top")
    Sempre que a variável “padrão” não existir, a função procura alternativa automaticamente.
    """
    out_dir = _ensure_dir(out_dir)
    slug = titulo.lower().replace(" ", "_").replace("/", "-")
    out_path = out_dir / f"analise_exploratoria_{slug}.png"

    import matplotlib.pyplot as plt
    plt.style.use("default")
    fig, axes = plt.subplots(2, 3, figsize=(17, 11))
    fig.suptitle(f"Análise Exploratória - {titulo}", fontsize=15, fontweight="bold")
    colors = ["#16a34a","#facc15","#fb923c","#ef4444"]  # verde, amarelo, laranja, vermelho

    def _off(ax, msg=None):
        ax.axis("off")
        if msg:
            ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=10, color="#666", transform=ax.transAxes)

    # preparar listas de colunas
    num_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c != "probabilidade"]
    bin_cols = [c for c in num_cols if df[c].nunique() <= 2]
    multi_cols = [c for c in num_cols if df[c].nunique() > 2]

    corr = _safe_corr(df)
    corr_to_y = pd.Series(dtype=float)
    if not corr.empty and "probabilidade" in corr.columns:
        corr_to_y = corr["probabilidade"].drop("probabilidade", errors="ignore").abs().sort_values(ascending=False)

    # melhores candidatas (pela correlação com y)
    best_num = next((c for c in corr_to_y.index if c in multi_cols), (multi_cols[0] if multi_cols else None))
    best_bin = next((c for c in corr_to_y.index if c in bin_cols), (bin_cols[0] if bin_cols else None))

    # (0,0) Distribuição das classes
    if "probabilidade" in df.columns:
        dist = df["probabilidade"].value_counts().sort_index()
        axes[0,0].bar([CLASSES.get(i,i) for i in dist.index], dist.values,
                      color=[colors[i] for i in dist.index], alpha=0.8, edgecolor="#111")
        axes[0,0].set_title("Distribuição das Classes"); axes[0,0].set_ylabel("Quantidade")
        ymax = max(dist.values) if len(dist) else 0
        for i, v in enumerate(dist.values):
            axes[0,0].text(i, v + (0.02*ymax if ymax else 0.5), str(v), ha="center", fontweight="bold", fontsize=9)
    else:
        _off(axes[0,0], "Sem coluna alvo 'probabilidade'")

    # (0,1) Binária x classe (higienizacao_previa prioritária; senão, best_bin)
    if {"higienizacao_previa","probabilidade"}.issubset(df.columns):
        tab = pd.crosstab(df["higienizacao_previa"], df["probabilidade"], normalize="columns")*100
        tab = tab.reindex(index=[0,1], fill_value=0)
        bottom = None
        for k in sorted(tab.columns):
            vals = tab[k].values
            axes[0,1].bar(["Não","Sim"], vals, bottom=bottom, alpha=.7, label=CLASSES.get(k,k), color=colors[k])
            bottom = (bottom + vals) if bottom is not None else vals
        axes[0,1].set_title("Higienização vs Probabilidade (%)"); axes[0,1].legend(fontsize=8)
    elif best_bin is not None and "probabilidade" in df.columns:
        tab = pd.crosstab(df[best_bin], df["probabilidade"], normalize="columns")*100
        idx = sorted(df[best_bin].dropna().unique().tolist())
        labels = [str(i) for i in idx]
        bottom = None
        for k in sorted(tab.columns):
            vals = tab.reindex(index=idx, fill_value=0)[k].values
            axes[0,1].bar(labels, vals, bottom=bottom, alpha=.7, label=CLASSES.get(k,k), color=colors[k])
            bottom = (bottom + vals) if bottom is not None else vals
        axes[0,1].set_title(f"{best_bin} vs Probabilidade (%)"); axes[0,1].legend(fontsize=8)
    else:
        _off(axes[0,1], "Sem variável binária aplicável")

    # (0,2) Distribuição numérica (uso_epi prioritário; senão, best_num)
    if "uso_epi" in df.columns:
        epi = df["uso_epi"].value_counts().sort_index()
        axes[0,2].bar(["Ausente","Parcial","Completo"], epi.values, color=["#ef4444","#facc15","#16a34a"], alpha=.8)
        axes[0,2].set_title("Distribuição do Uso de EPI"); axes[0,2].set_ylabel("Quantidade")
    elif best_num is not None:
        axes[0,2].hist(df[best_num], bins=20, alpha=.85, color="#4ea8de")
        axes[0,2].set_title(f"Distribuição de {best_num}"); axes[0,2].set_xlabel(best_num)
    else:
        _off(axes[0,2], "Sem variável numérica aplicável")

    # (1,0) Hist numérica por classe (tempo_exposicao_ar; senão, best_num)
    if {"tempo_exposicao_ar","probabilidade"}.issubset(df.columns):
        for k in sorted(df["probabilidade"].unique()):
            d = df.query("probabilidade == @k")["tempo_exposicao_ar"]
            if len(d): axes[1,0].hist(d, bins=15, alpha=.5, color=colors[k], label=CLASSES.get(k,k))
        axes[1,0].set_title("Tempo de Exposição por Classe"); axes[1,0].set_xlabel("Tempo (min)"); axes[1,0].legend()
    elif best_num is not None and "probabilidade" in df.columns:
        for k in sorted(df["probabilidade"].unique()):
            d = df.query("probabilidade == @k")[best_num]
            if len(d): axes[1,0].hist(d, bins=15, alpha=.5, label=CLASSES.get(k,k), color=colors[k])
        axes[1,0].set_title(f"{best_num} por Classe"); axes[1,0].set_xlabel(best_num); axes[1,0].legend()
    else:
        _off(axes[1,0], "Sem variável numérica por classe")

    # (1,1) Heatmap correlação (top)
    if not corr.empty and "probabilidade" in corr.columns:
        s = corr["probabilidade"].abs().sort_values(ascending=False)
        top = list(s.head(min(8, len(s))).index) + ["probabilidade"]
        top = list(dict.fromkeys([c for c in top if c in corr.columns]))
        sub = corr.loc[top, top]
        im = axes[1,1].imshow(sub.values, cmap="RdBu", vmin=-1, vmax=1, aspect="auto")
        axes[1,1].set_xticks(range(len(top))); axes[1,1].set_yticks(range(len(top)))
        axes[1,1].set_xticklabels(top, rotation=45, ha="right"); axes[1,1].set_yticklabels(top)
        axes[1,1].set_title("Correlação (Top)")
        for i in range(len(top)):
            for j in range(len(top)):
                axes[1,1].text(j, i, f"{sub.iloc[i,j]:.2f}", ha="center", va="center", fontsize=8, color="#111")
        fig.colorbar(im, ax=axes[1,1], shrink=0.6)
    else:
        _off(axes[1,1], "Correlação indisponível")

    # (1,2) Boxplot numérica por classe (tempo_exposicao_ar; senão, best_num)
    if {"tempo_exposicao_ar","probabilidade"}.issubset(df.columns):
        labels = [CLASSES[k] for k in sorted(df["probabilidade"].unique())]
        data = [df.query("probabilidade == @k")["tempo_exposicao_ar"].values for k in sorted(df["probabilidade"].unique())]
        if any(len(x) for x in data):
            try:
                bp = axes[1,2].boxplot(data, tick_labels=labels, patch_artist=True)  # Matplotlib ≥ 3.9
            except TypeError:
                bp = axes[1,2].boxplot(data, labels=labels, patch_artist=True)       # versões antigas
            for i, box in enumerate(bp["boxes"]):
                box.set_facecolor(colors[i % len(colors)]); box.set_alpha(.6)
            axes[1,2].set_title("Tempo de Exposição por Classe"); axes[1,2].set_ylabel("Tempo (min)")
        else:
            _off(axes[1,2], "Sem dados para boxplot")
    elif best_num is not None and "probabilidade" in df.columns:
        labels = [CLASSES[k] for k in sorted(df["probabilidade"].unique())]
        data = [df.query("probabilidade == @k")[best_num].values for k in sorted(df["probabilidade"].unique())]
        if any(len(x) for x in data):
            try:
                bp = axes[1,2].boxplot(data, tick_labels=labels, patch_artist=True)
            except TypeError:
                bp = axes[1,2].boxplot(data, labels=labels, patch_artist=True)
            for i, box in enumerate(bp["boxes"]):
                box.set_facecolor(colors[i % len(colors)]); box.set_alpha(.6)
            axes[1,2].set_title(f"{best_num} por Classe"); axes[1,2].set_ylabel(best_num)
        else:
            _off(axes[1,2], "Sem dados para boxplot")
    else:
        _off(axes[1,2], "Sem variável numérica para boxplot")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


# ---------------------------
# Pipeline por dataset
# ---------------------------
def analisar_dataset(path: Path, etapa: str, perigo: str, out_root: Path, sample: Optional[int]=None) -> Dict:
    df = pd.read_csv(path)
    if sample and len(df) > sample:
        df = df.sample(sample, random_state=42).reset_index(drop=True)

    titulo = f"{etapa} / {perigo.upper()} ({len(df)} amostras)"
    res_dist = analisar_distribuicoes(df, titulo)
    res_corr = analisar_correlacoes(df)
    res_imp  = analisar_impactos_criticos(df)
    res_qc   = analisar_qualidade_dados(df)

    img_path = gerar_visualizacoes(df, titulo=f"{etapa} • {perigo.upper()}", out_dir=out_root/etapa/perigo)

    # pacote de saída p/ consolidar
    return {
        "etapa": etapa,
        "perigo": perigo,
        "amostras": len(df),
        "shape": res_dist.get("shape"),
        "nulos": res_dist.get("nulos", 0),
        "duplicados": res_dist.get("duplicados", 0),
        "dist_target": res_dist.get("dist_target", {}),
        "top_corr": res_corr.get("top_corr", []),
        "pairs_high": res_corr.get("pairs_high", []),
        "qc_completude_pct": res_qc.get("completude_pct", 100.0),
        "qc_ratio_max_min": res_qc.get("ratio_max_min", None),
        "outliers_iqr": res_qc.get("outliers_iqr", []),
        "img": str(img_path)
    }


# ---------------------------
# Index HTML e CSV resumo
# ---------------------------
def salvar_index_html(summary: List[Dict], out_root: Path):
    html = [
        "<!doctype html><meta charset='utf-8'>",
        "<title>Relatórios de Análise - Mel</title>",
        "<style>body{font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif;padding:16px;background:#0b0d11;color:#e8eef6}",
        "a{color:#4ea8de} .card{background:#12161d;border:1px solid #1f2631;border-radius:12px;padding:16px;margin:16px 0}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}",
        ".pill{display:inline-block;padding:4px 8px;border:1px solid #2a3342;border-radius:999px;margin:2px}",
        "img{max-width:100%;height:auto;border-radius:8px;border:1px solid #1f2631}",
        "</style>",
        "<h1>Relatórios de Análise - Produção de Mel</h1>",
        "<div class='grid'>"
    ]
    for row in summary:
        dist = row.get("dist_target", {})
        pills = " ".join([f"<span class='pill'>{k}: {v}</span>" for k,v in dist.items()])
        html += [
            "<div class='card'>",
            f"<h2>{row['etapa']} / {row['perigo'].upper()}</h2>",
            f"<div>Amostras: <b>{row['amostras']}</b> • Nulos: {row['nulos']} • Duplicados: {row['duplicados']}</div>",
            f"<div>Classes: {pills}</div>",
            f"<div style='margin-top:8px'><img src='{Path(row['img']).relative_to(out_root)}' alt='viz'/></div>",
            "</div>"
        ]
    html += ["</div>"]
    (out_root/"index.html").write_text("\n".join(html), encoding="utf-8")


def salvar_resumo_csv(summary: List[Dict], out_root: Path):
    rows = []
    for s in summary:
        base = {
            "etapa": s["etapa"],
            "perigo": s["perigo"],
            "amostras": s["amostras"],
            "nulos": s["nulos"],
            "duplicados": s["duplicados"],
            "qc_completude_pct": round(s.get("qc_completude_pct", 100.0), 2),
            "qc_ratio_max_min": s.get("qc_ratio_max_min"),
        }
        # classes
        for k in ["DESPREZÍVEL","BAIXA","MÉDIA","ALTA"]:
            base[f"class_{k}"] = s.get("dist_target", {}).get(k, 0)
        rows.append(base)
    df = pd.DataFrame(rows)
    _ensure_dir(out_root)
    df.to_csv(out_root/"summary.csv", index=False, encoding="utf-8")


# ---------------------------
# Descoberta e CLI
# ---------------------------
def descobrir_datasets(root: Path, etapas: List[str], perigos: List[str]) -> List[Tuple[str,str,Path]]:
    itens = []
    for e in etapas:
        for p in perigos:
            path = _ds_path(root, e, p)
            if path.exists():
                itens.append((e, p, path))
    return itens

def main():
    ap = argparse.ArgumentParser(description="Analisador de datasets (mel) por etapa e perigo")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1] / "dataset" / "mel"),
                    help="Diretório raiz dos datasets (default: ml/dataset/mel)")
    ap.add_argument("--etapa", choices=ETAPAS+["all"], required=True)
    ap.add_argument("--perigo", choices=PERIGOS+["all"], required=True)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "results" / "analysis"),
                    help="Pasta de saída para PNG/CSV/HTML (default: ml/results/analysis)")
    ap.add_argument("--sample", type=int, default=None, help="Subamostrar N linhas por dataset (opcional)")
    args = ap.parse_args()

    root = Path(args.root)
    out_root = _ensure_dir(Path(args.out))
    etapas = ETAPAS if args.etapa == "all" else [args.etapa]
    perigos = PERIGOS if args.perigo == "all" else [args.perigo]

    itens = descobrir_datasets(root, etapas, perigos)
    if not itens:
        print(f"❌ Nenhum dataset encontrado em {root} com etapas={etapas} perigos={perigos}")
        return

    summary = []
    for etapa, perigo, path in itens:
        print(f"▶ Analisando {etapa}/{perigo} -> {path}")
        res = analisar_dataset(path, etapa, perigo, out_root=out_root, sample=args.sample)
        summary.append(res)

    salvar_resumo_csv(summary, out_root)
    salvar_index_html(summary, out_root)
    print(f"\n✅ Concluído. Veja:\n - {out_root/'summary.csv'}\n - {out_root/'index.html'}")

if __name__ == "__main__":
    main()
