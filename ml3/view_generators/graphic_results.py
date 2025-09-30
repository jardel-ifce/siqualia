# ml/view_generators/dataset_generator.py
import os, json, math, argparse
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

# ---------------------------
# ETAPAS suportadas
# ---------------------------
ETAPAS = [
    "recepcao", "desoperculacao", "centrifugacao", "peneiragem",
    "decantacao", "envase", "rotulagem", "armazenamento", "expedicao",
    # alias para compatibilidade com o gerador clássico:
    "envase_rotulagem"
]
PERIGOS = ["bio","fis","qui"]  # Biológico, Físico, Químico

# ---------------------------
# FEATURES por ETAPA
# (codificação entre parênteses; ver sampling mais abaixo)
# ---------------------------

FEATURES_BY_ETAPA = {
    "recepcao": [
        "fornecedor_auditado",            # 0/1
        "laudo_residuos_agrotoxicos",     # 0/1 (ou 1=ok)
        "temperatura_recebimento_c",      # num 10..35
        "tempo_desde_coleta_h",           # num 2..72
        "integridade_containers",         # 0/1
        "sujeira_visivel_externa",        # 0/1
        "umidade_lote_pct",               # num 16..24 (%)
        "documentacao_lote_ok",           # 0/1
        "transporte_segregado_de_quimicos", # 0/1
        "lacre_viagem_integro",           # 0/1
        "lote_identificado"               # 0/1
    ],
    "desoperculacao": [
        "higienizacao_utensilios",        # 0/1
        "material_utensilios_grau_alimentar", # 0/1
        "uso_epi",                         # 0/1/2
        "higiene_das_maos",               # 0/1
        "teor_umidade_mel_pct",           # num 16..24
        "controle_particulas_plasticos_areia", # 0/1
        "pontos_agua_potavel_ok",         # 0/1
        "separacao_fluxo_cru_pronto",     # 0/1
        "lote_identificado"               # 0/1
    ],
    "centrifugacao": [
        "velocidade_centrifuga_rpm",      # num 200..800
        "tempo_centrifugacao_min",        # num 2..20
        "limpeza_equipamento_pre_turno",  # 0/1
        "lubrificante_grau_alimentar",    # 0/1
        "vazamento_lubrificante",         # 0/1
        "uso_epi",                         # 0/1/2
        "higiene_das_maos",               # 0/1
        "inspecao_fragmentos_cera_pos_centrifuga", # 0/1
        "lote_identificado"               # 0/1
    ],
    "peneiragem": [
        "malha_peneira_microns",          # num 200..1200
        "integridade_peneira_sem_rasgos", # 0/1
        "frequencia_troca_peneira_h",     # num 1..24
        "higienizacao_peneira_pos_lote",  # 0/1
        "contagem_residuos_retidos_pct",  # num 0..5
        "protecao_contra_poeira",         # 0/1
        "separacao_fluxo",                # 0/1
        "lote_identificado"               # 0/1
    ],
    "decantacao": [
        "tempo_decantacao_h",             # num 2..72
        "temperatura_decantacao_c",       # num 18..35
        "tanque_limpio_sanitizado",       # 0/1
        "cobertura_anti_pragas",          # 0/1
        "remocao_espuma_impurezas",       # 0/1
        "material_tanque_inox_grau_alimentar", # 0/1
        "claridade_visual_nota",          # 0..2
        "lote_identificado"               # 0/1
    ],
    "envase": [
        "tipo_embalagem", "estado_embalagem", "tampa_correta", "vedacao_adequada",
        "higienizacao_previa", "uso_epi", "local_envase", "manipulador_higiene",
        "aspecto_visual", "umidade_mel", "temperatura_envase", "cristalizacao",
        "rotulo_presente", "informacoes_completas", "data_validade_legivel",
        "lote_identificado", "registro_lote", "treinamento_equipe",
        "historico_reclamacoes", "tempo_exposicao_ar"
    ],
    "rotulagem": [
        "rotulo_presente", "informacoes_completas", "data_validade_legivel",
        "lote_identificado", "aviso_nao_recomendado_menores1ano",
        "conformidade_legislacao", "rotulo_intacto_sem_sujos", "registro_lote"
    ],
    "armazenamento": [
        "temperatura_armazenamento_c",    # num 10..35
        "umidade_relativa_ambiente_pct",  # num 30..90
        "tempo_armazenado_dias",          # num 1..365
        "bombonas_integra_limpa",         # 0/1
        "lacres_integro",                 # 0/1
        "segregacao_de_produtos_quimicos",# 0/1
        "piso_limpo_seco",                # 0/1
        "PEPS_FEFO_aplicado",             # 0/1
        "lote_identificado"               # 0/1
    ],
    "expedicao": [
        "temperatura_transporte_c",       # num 10..40
        "tempo_transporte_h",             # num 1..72
        "veiculo_higienizado",            # 0/1
        "carga_compartilhada_quimicos",   # 0/1
        "embalagem_secundaria_protecao",  # 0/1
        "lacres_veiculo_integridade",     # 0/1
        "registro_condicoes_transporte",  # 0/1
        "lote_identificado"               # 0/1
    ],
    # alias histórico: mantém o dataset clássico de envase+rotulagem (20 features)
    "envase_rotulagem": [
        "tipo_embalagem","estado_embalagem","tampa_correta","vedacao_adequada",
        "higienizacao_previa","uso_epi","local_envase","manipulador_higiene",
        "aspecto_visual","umidade_mel","temperatura_envase","cristalizacao",
        "rotulo_presente","informacoes_completas","data_validade_legivel",
        "lote_identificado","registro_lote","treinamento_equipe",
        "historico_reclamacoes","tempo_exposicao_ar"
    ]
}

# ---------------------------
# Sampling de valores plausíveis por coluna
# ---------------------------
def _sample_column(col, n):
    if col in ["fornecedor_auditado","laudo_residuos_agrotoxicos","integridade_containers",
               "sujeira_visivel_externa","documentacao_lote_ok","transporte_segregado_de_quimicos",
               "lacre_viagem_integro","lote_identificado","higienizacao_utensilios",
               "material_utensilios_grau_alimentar","higiene_das_maos","controle_particulas_plasticos_areia",
               "pontos_agua_potavel_ok","separacao_fluxo_cru_pronto","limpeza_equipamento_pre_turno",
               "lubrificante_grau_alimentar","vazamento_lubrificante",
               "inspecao_fragmentos_cera_pos_centrifuga","integridade_peneira_sem_rasgos",
               "higienizacao_peneira_pos_lote","protecao_contra_poeira","separacao_fluxo",
               "tanque_limpio_sanitizado","cobertura_anti_pragas","remocao_espuma_impurezas",
               "material_tanque_inox_grau_alimentar","rotulo_presente","informacoes_completas",
               "data_validade_legivel","conformidade_legislacao","rotulo_intacto_sem_sujos","registro_lote",
               "bombonas_integra_limpa","lacres_integro","segregacao_de_produtos_quimicos","piso_limpo_seco",
               "PEPS_FEFO_aplicado","veiculo_higienizado","carga_compartilhada_quimicos",
               "embalagem_secundaria_protecao","lacres_veiculo_integridade","registro_condicoes_transporte",
               "treinamento_equipe","local_envase","manipulador_higiene","higienizacao_previa",
               "tampa_correta","vedacao_adequada","estado_embalagem","rotulo_intacto_sem_sujos",
               "aviso_nao_recomendado_menores1ano","documentacao_lote_ok"]:
        return rng.integers(0, 2, n)

    if col == "uso_epi":
        return rng.integers(0, 3, n)  # 0,1,2

    if col == "aspecto_visual":
        return rng.integers(0, 3, n)  # 0 suj,1 espuma,2 normal

    if col == "umidade_mel":
        return rng.integers(0, 2, n)  # 0 >20%, 1 ≤20%

    if col == "cristalizacao":
        return rng.integers(0, 3, n)  # 0 excessiva,1 parcial,2 ausente

    if col == "historico_reclamacoes":
        return rng.integers(0, 3, n)  # 0 freq,1 poucas,2 nenhuma

    # valores numéricos contínuos
    if col == "temperatura_recebimento_c":
        return rng.uniform(10, 35, n).round(1)
    if col == "tempo_desde_coleta_h":
        return rng.uniform(2, 72, n).round(1)
    if col == "umidade_lote_pct" or col == "teor_umidade_mel_pct":
        return rng.uniform(16, 24, n).round(1)
    if col == "velocidade_centrifuga_rpm":
        return rng.uniform(200, 800, n).round(0)
    if col == "tempo_centrifugacao_min":
        return rng.uniform(2, 20, n).round(1)
    if col == "malha_peneira_microns":
        return rng.uniform(200, 1200, n).round(0)
    if col == "frequencia_troca_peneira_h":
        return rng.uniform(1, 24, n).round(1)
    if col == "contagem_residuos_retidos_pct":
        return rng.uniform(0, 5, n).round(2)
    if col == "tempo_decantacao_h":
        return rng.uniform(2, 72, n).round(1)
    if col == "temperatura_decantacao_c":
        return rng.uniform(18, 35, n).round(1)
    if col == "claridade_visual_nota":
        return rng.integers(0, 3, n)  # 0,1,2
    if col == "temperatura_armazenamento_c":
        return rng.uniform(10, 35, n).round(1)
    if col == "umidade_relativa_ambiente_pct":
        return rng.uniform(30, 90, n).round(0)
    if col == "tempo_armazenado_dias":
        return rng.uniform(1, 365, n).round(0)
    if col == "temperatura_transporte_c":
        return rng.uniform(10, 40, n).round(1)
    if col == "tempo_transporte_h":
        return rng.uniform(1, 72, n).round(1)
    if col == "tempo_exposicao_ar":
        return rng.integers(5, 61, n)

    if col == "tipo_embalagem":
        return rng.integers(0, 2, n)  # 0 PET, 1 Vidro

    # fallback: 0/1
    return rng.integers(0, 2, n)

def _amostra_etapa(etapa: str, n: int) -> pd.DataFrame:
    cols = FEATURES_BY_ETAPA[etapa]
    data = {c: _sample_column(c, n) for c in cols}
    return pd.DataFrame(data)

# ---------------------------
# Indicadores de condição "ruim" por coluna
# ---------------------------
def _indicador_ruim(col, s):
    """
    Converte a coluna em um score 0..1 de "pior condição".
    """
    # binários (0 ruim, 1 bom)
    bin_0_ruim = {
        "fornecedor_auditado","laudo_residuos_agrotoxicos","integridade_containers",
        "documentacao_lote_ok","transporte_segregado_de_quimicos","lacre_viagem_integro",
        "higienizacao_utensilios","material_utensilios_grau_alimentar",
        "higiene_das_maos","controle_particulas_plasticos_areia",
        "pontos_agua_potavel_ok","separacao_fluxo_cru_pronto","limpeza_equipamento_pre_turno",
        "lubrificante_grau_alimentar","inspecao_fragmentos_cera_pos_centrifuga",
        "integridade_peneira_sem_rasgos","higienizacao_peneira_pos_lote",
        "protecao_contra_poeira","separacao_fluxo","tanque_limpio_sanitizado",
        "cobertura_anti_pragas","remocao_espuma_impurezas",
        "material_tanque_inox_grau_alimentar","rotulo_presente","informacoes_completas",
        "data_validade_legivel","conformidade_legislacao","rotulo_intacto_sem_sujos",
        "registro_lote","bombonas_integra_limpa","lacres_integro",
        "segregacao_de_produtos_quimicos","piso_limpo_seco","PEPS_FEFO_aplicado",
        "veiculo_higienizado","embalagem_secundaria_protecao","lacres_veiculo_integridade",
        "registro_condicoes_transporte","treinamento_equipe","local_envase",
        "manipulador_higiene","higienizacao_previa","tampa_correta","vedacao_adequada",
        "estado_embalagem","aviso_nao_recomendado_menores1ano","lote_identificado"
    }
    if col in bin_0_ruim:
        return (s == 0).astype(float)

    # binários onde 1 é ruim (ex.: sujeira presente, vazamento, carga compartilhada com químicos)
    bin_1_ruim = {"sujeira_visivel_externa","vazamento_lubrificante","carga_compartilhada_quimicos"}
    if col in bin_1_ruim:
        return (s == 1).astype(float)

    # 3 níveis
    if col == "uso_epi":
        return s.map({0:1.0, 1:0.5, 2:0.0}).astype(float)
    if col == "aspecto_visual":
        return s.map({0:1.0, 1:0.5, 2:0.0}).astype(float)
    if col == "cristalizacao":
        return s.map({0:1.0, 1:0.5, 2:0.0}).astype(float)
    if col == "historico_reclamacoes":
        return s.map({0:1.0, 1:0.5, 2:0.0}).astype(float)
    if col == "claridade_visual_nota":
        # 0 ruim (turvo) -> 2 bom (claro)
        return s.map({0:1.0, 1:0.5, 2:0.0}).astype(float)

    # numéricos com limiares
    if col in ["umidade_lote_pct","teor_umidade_mel_pct"]:
        # >20% é ruim → normalize 18..24 → 0..1
        return np.clip((s - 18.0) / (24.0 - 18.0), 0, 1)
    if col == "temperatura_recebimento_c":
        # >30 ruim
        return np.clip((s - 25.0) / 10.0, 0, 1)
    if col == "tempo_desde_coleta_h":
        # >24h pior
        return np.clip((s - 12.0) / 36.0, 0, 1)
    if col == "velocidade_centrifuga_rpm":
        # muito alto pode gerar mais fragmentos (proxy): >600 pior
        return np.clip((s - 500.0) / 300.0, 0, 1)
    if col == "tempo_centrifugacao_min":
        # muito longo pode degradar controle (proxy): >12 pior
        return np.clip((s - 8.0) / 12.0, 0, 1)
    if col == "malha_peneira_microns":
        # malha muito grossa deixa passar partículas: >800 pior
        return np.clip((s - 600.0) / 600.0, 0, 1)
    if col == "frequencia_troca_peneira_h":
        # trocar pouco (alto valor) pior
        return np.clip((s - 8.0) / 24.0, 0, 1)
    if col == "contagem_residuos_retidos_pct":
        # % alto ruim
        return np.clip(s / 5.0, 0, 1)
    if col == "tempo_decantacao_h":
        # muito curto não decanta; muito longo expõe: adotamos U-shape simplificado → penaliza extremos
        mid = 24.0
        return np.clip(np.abs(s - mid) / mid, 0, 1)
    if col == "temperatura_decantacao_c":
        # >30 pior (fermentação)
        return np.clip((s - 25.0) / 10.0, 0, 1)
    if col == "temperatura_armazenamento_c":
        # >25 pior
        return np.clip((s - 20.0) / 15.0, 0, 1)
    if col == "umidade_relativa_ambiente_pct":
        # >70 pior
        return np.clip((s - 60.0) / 40.0, 0, 1)
    if col == "tempo_armazenado_dias":
        # >180 pior
        return np.clip((s - 90.0) / 275.0, 0, 1)
    if col == "temperatura_transporte_c":
        # >30 pior
        return np.clip((s - 25.0) / 15.0, 0, 1)
    if col == "tempo_transporte_h":
        # >24 pior
        return np.clip((s - 12.0) / 60.0, 0, 1)
    if col == "tipo_embalagem":
        # 1=Vidro (assumimos um pouco mais crítico p/ F/Q em envase)
        return (s == 1).astype(float)
    if col == "sujeira_visivel_externa":
        return (s == 1).astype(float)

    # fallback
    return pd.Series(np.zeros(len(s)), index=s.index, dtype=float)

# ---------------------------
# PESOS (base por perigo + ajustes por etapa)
# ---------------------------

# Pesos base por perigo (válidos para qualquer etapa se a coluna existir)
PESOS_BASE_RUIM = {
    "bio": {
        "umidade_lote_pct": 3.0, "teor_umidade_mel_pct": 3.0, "umidade_mel": 3.0,
        "higiene_das_maos": 2.5, "higienizacao_previa": 2.5, "manipulador_higiene": 2.5,
        "uso_epi": 1.5, "temperatura_*": 2.0, "tempo_*": 1.5,
        "pontos_agua_potavel_ok": 1.5, "separacao_fluxo*": 1.5
    },
    "fis": {
        "integridade_*": 3.0, "estado_embalagem": 3.0, "tampa_correta": 2.5, "vedacao_adequada": 2.5,
        "aspecto_visual": 2.0, "protecao_contra_poeira": 1.5, "malha_peneira_microns": 2.0,
        "inspecao_fragmentos_cera_pos_centrifuga": 2.0
    },
    "qui": {
        "laudo_residuos_agrotoxicos": 3.0, "lubrificante_grau_alimentar": 2.5, "vazamento_lubrificante": 2.5,
        "conformidade_legislacao": 2.0, "rotulo_presente": 2.0, "informacoes_completas": 2.0,
        "registro_lote": 1.2, "segregacao_de_produtos_quimicos": 2.0, "tipo_embalagem": 1.5
    }
}

# Pesos adicionais específicos por etapa/perigo (apenas exemplos fortes)
PESOS_ETAPA_EXTRA = {
    "recepcao": {
        "bio": {"temperatura_recebimento_c": 2.0, "tempo_desde_coleta_h": 2.0},
        "fis": {"integridade_containers": 2.5, "sujeira_visivel_externa": 2.0},
        "qui": {"transporte_segregado_de_quimicos": 2.5, "documentacao_lote_ok": 1.5}
    },
    "desoperculacao": {
        "bio": {"higienizacao_utensilios": 2.5, "higiene_das_maos": 2.5, "teor_umidade_mel_pct": 3.0},
        "fis": {"controle_particulas_plasticos_areia": 2.5},
        "qui": {"material_utensilios_grau_alimentar": 2.0}
    },
    "centrifugacao": {
        "bio": {"limpeza_equipamento_pre_turno": 2.5, "higiene_das_maos": 2.0},
        "fis": {"inspecao_fragmentos_cera_pos_centrifuga": 2.5, "velocidade_centrifuga_rpm": 1.8},
        "qui": {"lubrificante_grau_alimentar": 2.5, "vazamento_lubrificante": 2.5}
    },
    "peneiragem": {
        "fis": {"malha_peneira_microns": 2.5, "integridade_peneira_sem_rasgos": 2.5,
                "contagem_residuos_retidos_pct": 2.0}
    },
    "decantacao": {
        "fis": {"claridade_visual_nota": 2.0, "tempo_decantacao_h": 1.5},
        "bio": {"temperatura_decantacao_c": 2.0}
    },
    "envase": {
        "bio": {"higienizacao_previa": 3.0, "manipulador_higiene": 2.5, "umidade_mel": 3.0},
        "fis": {"estado_embalagem": 3.0, "vedacao_adequada": 2.5, "tampa_correta": 2.5},
        "qui": {"tipo_embalagem": 1.5, "registro_lote": 1.5}
    },
    "rotulagem": {
        "bio": {"aviso_nao_recomendado_menores1ano": 1.5},
        "qui": {"conformidade_legislacao": 2.5, "informacoes_completas": 2.0, "rotulo_presente": 2.0},
        "fis": {"rotulo_intacto_sem_sujos": 1.5}
    },
    "armazenamento": {
        "bio": {"temperatura_armazenamento_c": 2.5, "umidade_relativa_ambiente_pct": 2.0},
        "fis": {"bombonas_integra_limpa": 2.5, "lacres_integro": 2.0},
        "qui": {"segregacao_de_produtos_quimicos": 2.5}
    },
    "expedicao": {
        "bio": {"temperatura_transporte_c": 2.5, "tempo_transporte_h": 2.0},
        "fis": {"veiculo_higienizado": 2.0, "embalagem_secundaria_protecao": 2.0},
        "qui": {"carga_compartilhada_quimicos": 2.5}
    },
    "envase_rotulagem": {}  # usa apenas base + inferência do conjunto de 20 features
}

def _collect_pesos(etapa: str, tipo_perigo: str, cols: list) -> dict:
    """
    Resolve os pesos aplicáveis a partir dos padrões PESOS_BASE_RUIM e do overlay de etapa.
    Suporta curingas simples (ex.: 'temperatura_*', 'integridade_*').
    """
    pesos = {}
    base = PESOS_BASE_RUIM.get(tipo_perigo, {})
    extra = PESOS_ETAPA_EXTRA.get(etapa, {}).get(tipo_perigo, {})

    def match_keys(src):
        for k, w in src.items():
            if k.endswith("*"):
                prefix = k[:-1]
                for c in cols:
                    if c.startswith(prefix):
                        pesos[c] = max(pesos.get(c, 0.0), float(w))
            else:
                if k in cols:
                    pesos[k] = max(pesos.get(k, 0.0), float(w))

    match_keys(base)
    match_keys(extra)

    # Se nenhuma chave casou, distribui pesos leves em binários comuns para não zerar o score
    if not pesos:
        for c in cols:
            if c.endswith("_ok") or c.startswith("integridade_") or c in ("higienizacao_previa","higiene_das_maos","uso_epi"):
                pesos[c] = 1.0
    return pesos

# ---------------------------
# Scoring e classe alvo
# ---------------------------
def _score_por_perigo(df: pd.DataFrame, etapa: str, tipo_perigo: str) -> np.ndarray:
    cols = list(df.columns)
    pesos = _collect_pesos(etapa, tipo_perigo, cols)
    if not pesos:
        return np.zeros(len(df))

    score = np.zeros(len(df), dtype=float)
    for col, w in pesos.items():
        if col in df.columns:
            score += w * _indicador_ruim(col, df[col]).to_numpy()

    max_peso = sum(pesos.values())
    score_norm = 100.0 * (score / max_peso) if max_peso > 0 else np.zeros(len(df))
    return np.clip(score_norm, 0, 100)

def _classe_0a3(score_norm: np.ndarray) -> np.ndarray:
    # 0: 0–15 | 1: 15–40 | 2: 40–70 | 3: 70–100
    return np.digitize(score_norm, [15, 40, 70], right=False).astype(int)

# ---------------------------
# Geração principal
# ---------------------------
def gerar_dataset(etapa: str, tipo_perigo: str, n_amostras=1500):
    assert etapa in ETAPAS, f"etapa inválida: {etapa}"
    assert tipo_perigo in PERIGOS, f"perigo inválido: {tipo_perigo}"

    df = _amostra_etapa(etapa, n_amostras)
    score = _score_por_perigo(df, etapa, tipo_perigo)
    df["probabilidade"] = _classe_0a3(score)

    # salvar
    base_ml = Path(__file__).resolve().parents[1]  # ml/
    out_dir = base_ml / "dataset" / "mel" / etapa / tipo_perigo
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"dataset_{etapa}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")

    meta = {
        "etapa": etapa,
        "tipo_perigo": tipo_perigo,
        "amostras": int(n_amostras),
        "features": list(df.columns[:-1]),
        "faixas_alvo": {"0":"Desprezível","1":"Baixa","2":"Média","3":"Alta"}
    }
    with open(out_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    return str(csv_path), meta

def gerar_todas_as_combinacoes(n=1500):
    out = []
    for etapa in ETAPAS:
        for perigo in PERIGOS:
            path, meta = gerar_dataset(etapa, perigo, n)
            out.append((path, meta))
    return out

# ---------------------------
# CLI
# ---------------------------
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gerador de datasets multi-etapas (mel) por tipo de perigo")
    ap.add_argument("--etapa", choices=ETAPAS + ["all"], required=True)
    ap.add_argument("--perigo", choices=PERIGOS + ["all"], required=True)
    ap.add_argument("--n", type=int, default=1500)
    args = ap.parse_args()

    if args.etapa == "all" and args.perigo == "all":
        out = gerar_todas_as_combinacoes(args.n)
        print(f"Gerados {len(out)} datasets.")
    else:
        etapas = ETAPAS if args.etapa == "all" else [args.etapa]
        perigos = PERIGOS if args.perigo == "all" else [args.perigo]
        for e in etapas:
            for p in perigos:
                path, meta = gerar_dataset(e, p, args.n)
                print(f"[OK] {e}/{p} -> {path}")
