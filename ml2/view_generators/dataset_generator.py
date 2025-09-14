# ml/view_generators/dataset_generator.py
import os, sys, json, math
import numpy as np
import pandas as pd
from pathlib import Path
import argparse
rng = np.random.default_rng(42)

# ---------------------------
# Base: geramos os 20 atributos
# ---------------------------
FEATURES = [
    # A) Embalagem
    "tipo_embalagem","estado_embalagem","tampa_correta","vedacao_adequada",
    # B) Higiene/Manipulação
    "higienizacao_previa","uso_epi","local_envase","manipulador_higiene",
    # C) Condições do mel
    "aspecto_visual","umidade_mel","temperatura_envase","cristalizacao",
    # D) Rotulagem/registro
    "rotulo_presente","informacoes_completas","data_validade_legivel","lote_identificado","registro_lote",
    # E) Gestão/Processo
    "treinamento_equipe","historico_reclamacoes","tempo_exposicao_ar"
]

def _amostra_base(n):
    # Valores plausíveis (mesmo espaço já usado no projeto)
    df = pd.DataFrame({
        # A) Embalagem
        "tipo_embalagem": rng.integers(0, 2, n),                  # 0 PET, 1 Vidro
        "estado_embalagem": rng.integers(0, 2, n),                # 0 Danificada, 1 Íntegra
        "tampa_correta": rng.integers(0, 2, n),                   # 0 Não, 1 Sim
        "vedacao_adequada": rng.integers(0, 2, n),                # 0 Inad., 1 Ad.
        # B) Higiene
        "higienizacao_previa": rng.integers(0, 2, n),             # 0 Não, 1 Sim
        "uso_epi": rng.integers(0, 3, n),                         # 0 Ausente,1 Parcial,2 Completo
        "local_envase": rng.integers(0, 2, n),                    # 0 Inad., 1 Ad.
        "manipulador_higiene": rng.integers(0, 2, n),             # 0 Inad., 1 Ad.
        # C) Mel
        "aspecto_visual": rng.integers(0, 3, n),                  # 0 Suj., 1 Espuma, 2 Normal (nota: 2 = melhor)
        "umidade_mel": rng.integers(0, 2, n),                     # 0 >20%, 1 ≤20%
        "temperatura_envase": rng.integers(0, 2, n),              # 0 Inad., 1 Ad.
        "cristalizacao": rng.integers(0, 3, n),                   # 0 Excessiva,1 Parcial,2 Ausente
        # D) Rotulagem
        "rotulo_presente": rng.integers(0, 2, n),
        "informacoes_completas": rng.integers(0, 2, n),
        "data_validade_legivel": rng.integers(0, 2, n),
        "lote_identificado": rng.integers(0, 2, n),
        "registro_lote": rng.integers(0, 2, n),
        # E) Gestão
        "treinamento_equipe": rng.integers(0, 2, n),
        "historico_reclamacoes": rng.integers(0, 3, n),           # 0 Freq., 1 Poucas, 2 Nenhuma
        "tempo_exposicao_ar": rng.integers(5, 61, n)              # minutos 5..60
    })
    return df

# -------------------------------------------
# PESOS por tipo de perigo (usando as MESMAS 20 features)
# quanto MAIOR o peso para condição "ruim", maior o risco
# -------------------------------------------
PESOS_RUIM = {
    "bio": {
        # higiene/ambiente/produto/tempo
        "umidade_mel": 3.0, "higienizacao_previa": 3.0, "manipulador_higiene": 2.5,
        "uso_epi": 1.5, "local_envase": 2.0, "temperatura_envase": 2.0,
        "tempo_exposicao_ar": 1.5, "aspecto_visual": 1.3,
        # complementos
        "treinamento_equipe": 1.2, "registro_lote": 0.7
    },
    "fis": {
        # embalagem/vedação/visual/manuseio
        "estado_embalagem": 3.0, "tampa_correta": 2.5, "vedacao_adequada": 2.5,
        "tipo_embalagem": 1.2, "aspecto_visual": 2.0,
        "manipulador_higiene": 1.5, "local_envase": 1.2, "tempo_exposicao_ar": 1.0
    },
    "qui": {
        # rotulagem/vedação/embalagem/sanitização (proxy por higiene)
        "informacoes_completas": 2.5, "rotulo_presente": 2.0, "data_validade_legivel": 1.5,
        "lote_identificado": 1.5, "vedacao_adequada": 2.0, "tipo_embalagem": 1.5,
        "higienizacao_previa": 1.2, "registro_lote": 1.2
    }
}

def _indicador_ruim(col, serie):
    # define "ruim" por coluna, usando convenções do dataset
    if col in ["tipo_embalagem"]:
        # considerar VIDRO (=1) como um pouco mais crítico para físico/químico (possível estilhaço/migração tampas inadequadas)
        return (serie == 1).astype(float)
    if col in ["estado_embalagem","tampa_correta","vedacao_adequada","higienizacao_previa",
               "local_envase","manipulador_higiene","temperatura_envase",
               "rotulo_presente","informacoes_completas","data_validade_legivel",
               "lote_identificado","registro_lote","treinamento_equipe"]:
        # binário onde 0 é ruim, 1 é bom
        return (serie == 0).astype(float)
    if col == "uso_epi":
        # 0=Ausente (ruim), 1=Parcial (meio), 2=Completo (bom)
        m = serie.map({0:1.0, 1:0.5, 2:0.0})
        return m.astype(float)
    if col == "aspecto_visual":
        # 0 Sujidades (ruim) > 1 Espuma (médio) > 2 Normal (bom)
        m = serie.map({0:1.0, 1:0.5, 2:0.0})
        return m.astype(float)
    if col == "umidade_mel":
        # 0 >20% (ruim), 1 ≤20% (bom)
        return (serie == 0).astype(float)
    if col == "cristalizacao":
        # 0 Excessiva (ruim), 1 Parcial (meio), 2 Ausente (bom)
        m = serie.map({0:1.0, 1:0.5, 2:0.0})
        return m.astype(float)
    if col == "historico_reclamacoes":
        # 0 Freq. (ruim), 1 Poucas (meio), 2 Nenhuma (bom)
        m = serie.map({0:1.0, 1:0.5, 2:0.0})
        return m.astype(float)
    if col == "tempo_exposicao_ar":
        # escalar 5..60 → maior tempo = pior (normalizar em 0..1)
        return (serie - 5.0) / (60.0 - 5.0)
    # padrão: não computa
    return pd.Series(np.zeros(len(serie)), index=serie.index, dtype=float)

def _score_perigo(df, tipo_perigo):
    pesos = PESOS_RUIM[tipo_perigo]
    # soma ponderada das condições ruins definidas acima
    score = np.zeros(len(df), dtype=float)
    for col, w in pesos.items():
        score += w * _indicador_ruim(col, df[col]).to_numpy()
    # normalizar para 0..100 por robustez (divisor heurístico = soma dos pesos)
    max_peso = sum(pesos.values())
    score_norm = 100.0 * (score / max_peso)
    return np.clip(score_norm, 0, 100)

def _classe_0a3(score_norm):
    # thresholds globais (mantidos iguais p/ os 3 perigos na Fase 1)
    # 0: 0–15 | 1: 15–40 | 2: 40–70 | 3: 70–100
    bins = np.digitize(score_norm, [15, 40, 70], right=False)
    return bins.astype(int)

def gerar_dataset_por_tipo_perigo(tipo_perigo: str, n_amostras=1500):
    assert tipo_perigo in {"bio","fis","qui"}
    df = _amostra_base(n_amostras)
    score = _score_perigo(df, tipo_perigo)
    df["probabilidade"] = _classe_0a3(score)

    # salvar em subpasta por perigo
    script_dir = Path(__file__).resolve().parents[1]  # ml/
    out_dir = script_dir / "dataset" / "mel" / "envase_rotulagem" / tipo_perigo
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / "dataset_envase_rotulagem.csv"
    df.to_csv(out_csv, index=False)

    # metadata simples
    meta = {
        "tipo_perigo": tipo_perigo,
        "amostras": len(df),
        "features": FEATURES,
        "faixas_alvo": {"0":"Desprezível","1":"Baixa","2":"Média","3":"Alta"}
    }
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return str(out_csv), meta

# CLI simples para gerar rapidamente
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--perigo", choices=["bio","fis","qui"], required=True)
    ap.add_argument("--n", type=int, default=1500)
    args = ap.parse_args()
    path, meta = gerar_dataset_por_tipo_perigo(args.perigo, args.n)
    print(f"Dataset gerado: {path}")
