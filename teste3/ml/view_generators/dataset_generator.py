# teste3/ml/view_generators/dataset_generator.py
import os, json, argparse
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

ETAPAS = [
    "recepcao","desoperculacao","centrifugacao","peneiragem",
    "decantacao","envase","rotulagem","armazenamento","expedicao",
    "envase_rotulagem"  # alias histórico
]
PERIGOS = ["bio","fis","qui"]

FEATURES_BY_ETAPA = {
    "recepcao":[
        "fornecedor_auditado","laudo_residuos_agrotoxicos","temperatura_recebimento_c","tempo_desde_coleta_h",
        "integridade_containers","sujeira_visivel_externa","umidade_lote_pct","documentacao_lote_ok",
        "transporte_segregado_de_quimicos","lacre_viagem_integro","lote_identificado"
    ],
    "desoperculacao":[
        "higienizacao_utensilios","material_utensilios_grau_alimentar","uso_epi","higiene_das_maos",
        "teor_umidade_mel_pct","controle_particulas_plasticos_areia","pontos_agua_potavel_ok",
        "separacao_fluxo_cru_pronto","lote_identificado"
    ],
    "centrifugacao":[
        "velocidade_centrifuga_rpm","tempo_centrifugacao_min","limpeza_equipamento_pre_turno","lubrificante_grau_alimentar",
        "vazamento_lubrificante","uso_epi","higiene_das_maos","inspecao_fragmentos_cera_pos_centrifuga","lote_identificado"
    ],
    "peneiragem":[
        "malha_peneira_microns","integridade_peneira_sem_rasgos","frequencia_troca_peneira_h","higienizacao_peneira_pos_lote",
        "contagem_residuos_retidos_pct","protecao_contra_poeira","separacao_fluxo","lote_identificado"
    ],
    "decantacao":[
        "tempo_decantacao_h","temperatura_decantacao_c","tanque_limpio_sanitizado","cobertura_anti_pragas",
        "remocao_espuma_impurezas","material_tanque_inox_grau_alimentar","claridade_visual_nota","lote_identificado"
    ],
    "envase":[
        "tipo_embalagem","estado_embalagem","tampa_correta","vedacao_adequada","higienizacao_previa","uso_epi",
        "local_envase","manipulador_higiene","aspecto_visual","umidade_mel","temperatura_envase","cristalizacao",
        "rotulo_presente","informacoes_completas","data_validade_legivel","lote_identificado","registro_lote",
        "treinamento_equipe","historico_reclamacoes","tempo_exposicao_ar"
    ],
    "rotulagem":[
        "rotulo_presente","informacoes_completas","data_validade_legivel","lote_identificado",
        "aviso_nao_recomendado_menores1ano","conformidade_legislacao","rotulo_intacto_sem_sujos","registro_lote"
    ],
    "armazenamento":[
        "temperatura_armazenamento_c","umidade_relativa_ambiente_pct","tempo_armazenado_dias","bombonas_integra_limpa",
        "lacres_integro","segregacao_de_produtos_quimicos","piso_limpo_seco","PEPS_FEFO_aplicado","lote_identificado"
    ],
    "expedicao":[
        "temperatura_transporte_c","tempo_transporte_h","veiculo_higienizado","carga_compartilhada_quimicos",
        "embalagem_secundaria_protecao","lacres_veiculo_integridade","registro_condicoes_transporte","lote_identificado"
    ],
    "envase_rotulagem":[
        "tipo_embalagem","estado_embalagem","tampa_correta","vedacao_adequada","higienizacao_previa","uso_epi",
        "local_envase","manipulador_higiene","aspecto_visual","umidade_mel","temperatura_envase","cristalizacao",
        "rotulo_presente","informacoes_completas","data_validade_legivel","lote_identificado","registro_lote",
        "treinamento_equipe","historico_reclamacoes","tempo_exposicao_ar"
    ],
}

def _sample(col, n):
    bin01 = {"fornecedor_auditado","laudo_residuos_agrotoxicos","integridade_containers","documentacao_lote_ok",
             "transporte_segregado_de_quimicos","lacre_viagem_integro","lote_identificado","higienizacao_utensilios",
             "material_utensilios_grau_alimentar","higiene_das_maos","controle_particulas_plasticos_areia",
             "pontos_agua_potavel_ok","separacao_fluxo_cru_pronto","limpeza_equipamento_pre_turno","lubrificante_grau_alimentar",
             "inspecao_fragmentos_cera_pos_centrifuga","integridade_peneira_sem_rasgos","higienizacao_peneira_pos_lote",
             "protecao_contra_poeira","separacao_fluxo","tanque_limpio_sanitizado","cobertura_anti_pragas","remocao_espuma_impurezas",
             "material_tanque_inox_grau_alimentar","rotulo_presente","informacoes_completas","data_validade_legivel",
             "conformidade_legislacao","rotulo_intacto_sem_sujos","registro_lote","bombonas_integra_limpa","lacres_integro",
             "segregacao_de_produtos_quimicos","piso_limpo_seco","PEPS_FEFO_aplicado","veiculo_higienizado",
             "embalagem_secundaria_protecao","lacres_veiculo_integridade","registro_condicoes_transporte",
             "treinamento_equipe","local_envase","manipulador_higiene","higienizacao_previa","tampa_correta",
             "vedacao_adequada","estado_embalagem","aviso_nao_recomendado_menores1ano"}
    if col in bin01: return rng.integers(0,2,n)
    if col in {"sujeira_visivel_externa","vazamento_lubrificante","carga_compartilhada_quimicos"}: return rng.integers(0,2,n)
    if col=="uso_epi": return rng.integers(0,3,n)
    if col=="aspecto_visual": return rng.integers(0,3,n)
    if col=="umidade_mel": return rng.integers(0,2,n)
    if col=="cristalizacao": return rng.integers(0,3,n)
    if col=="historico_reclamacoes": return rng.integers(0,3,n)
    if col=="tipo_embalagem": return rng.integers(0,2,n)
    num = {
      "temperatura_recebimento_c":(10,35,1),"tempo_desde_coleta_h":(2,72,1),"umidade_lote_pct":(16,24,1),
      "teor_umidade_mel_pct":(16,24,1),"velocidade_centrifuga_rpm":(200,800,0),"tempo_centrifugacao_min":(2,20,1),
      "malha_peneira_microns":(200,1200,0),"frequencia_troca_peneira_h":(1,24,1),"contagem_residuos_retidos_pct":(0,5,2),
      "tempo_decantacao_h":(2,72,1),"temperatura_decantacao_c":(18,35,1),"claridade_visual_nota":(0,2,0),
      "temperatura_armazenamento_c":(10,35,1),"umidade_relativa_ambiente_pct":(30,90,0),"tempo_armazenado_dias":(1,365,0),
      "temperatura_transporte_c":(10,40,1),"tempo_transporte_h":(1,72,1),"tempo_exposicao_ar":(5,61,0),
    }
    if col in num:
        lo,hi,dec = num[col]
        arr = rng.uniform(lo,hi,n)
        return arr.round(dec) if dec>0 else arr.round(0)
    return rng.integers(0,2,n)

def _amostra(etapa, n):
    cols = FEATURES_BY_ETAPA[etapa]
    return pd.DataFrame({c:_sample(c,n) for c in cols})

def _indicador_ruim(col, s):
    bin_0_ruim = {"fornecedor_auditado","laudo_residuos_agrotoxicos","integridade_containers","documentacao_lote_ok",
                  "transporte_segregado_de_quimicos","lacre_viagem_integro","higienizacao_utensilios",
                  "material_utensilios_grau_alimentar","higiene_das_maos","controle_particulas_plasticos_areia",
                  "pontos_agua_potavel_ok","separacao_fluxo_cru_pronto","limpeza_equipamento_pre_turno",
                  "lubrificante_grau_alimentar","inspecao_fragmentos_cera_pos_centrifuga","integridade_peneira_sem_rasgos",
                  "higienizacao_peneira_pos_lote","protecao_contra_poeira","separacao_fluxo","tanque_limpio_sanitizado",
                  "cobertura_anti_pragas","remocao_espuma_impurezas","material_tanque_inox_grau_alimentar",
                  "rotulo_presente","informacoes_completas","data_validade_legivel","conformidade_legislacao",
                  "rotulo_intacto_sem_sujos","registro_lote","bombonas_integra_limpa","lacres_integro",
                  "segregacao_de_produtos_quimicos","piso_limpo_seco","PEPS_FEFO_aplicado","veiculo_higienizado",
                  "embalagem_secundaria_protecao","lacres_veiculo_integridade","registro_condicoes_transporte",
                  "treinamento_equipe","local_envase","manipulador_higiene","higienizacao_previa","tampa_correta",
                  "vedacao_adequada","estado_embalagem","aviso_nao_recomendado_menores1ano","lote_identificado"}
    if col in bin_0_ruim: return (s==0).astype(float)
    if col in {"sujeira_visivel_externa","vazamento_lubrificante","carga_compartilhada_quimicos"}: return (s==1).astype(float)
    maps = {
      "uso_epi":{0:1,1:0.5,2:0},"aspecto_visual":{0:1,1:0.5,2:0},"cristalizacao":{0:1,1:0.5,2:0},
      "historico_reclamacoes":{0:1,1:0.5,2:0},"claridade_visual_nota":{0:1,1:0.5,2:0}
    }
    if col in maps: return s.map(maps[col]).astype(float)
    if col in {"umidade_lote_pct","teor_umidade_mel_pct"}: return np.clip((s-18)/6,0,1)
    if col=="temperatura_recebimento_c": return np.clip((s-25)/10,0,1)
    if col=="tempo_desde_coleta_h": return np.clip((s-12)/36,0,1)
    if col=="velocidade_centrifuga_rpm": return np.clip((s-500)/300,0,1)
    if col=="tempo_centrifugacao_min": return np.clip((s-8)/12,0,1)
    if col=="malha_peneira_microns": return np.clip((s-600)/600,0,1)
    if col=="frequencia_troca_peneira_h": return np.clip((s-8)/24,0,1)
    if col=="contagem_residuos_retidos_pct": return np.clip(s/5,0,1)
    if col=="tempo_decantacao_h": return np.clip(np.abs(s-24)/24,0,1)
    if col=="temperatura_decantacao_c": return np.clip((s-25)/10,0,1)
    if col=="temperatura_armazenamento_c": return np.clip((s-20)/15,0,1)
    if col=="umidade_relativa_ambiente_pct": return np.clip((s-60)/40,0,1)
    if col=="tempo_armazenado_dias": return np.clip((s-90)/275,0,1)
    if col=="temperatura_transporte_c": return np.clip((s-25)/15,0,1)
    if col=="tempo_transporte_h": return np.clip((s-12)/60,0,1)
    if col=="tipo_embalagem": return (s==1).astype(float)
    return pd.Series(np.zeros(len(s)), index=s.index, dtype=float)

PESOS_BASE_RUIM = {
  "bio":{"umidade_lote_pct":3.0,"teor_umidade_mel_pct":3.0,"umidade_mel":3.0,
         "higiene_das_maos":2.5,"higienizacao_previa":2.5,"manipulador_higiene":2.5,
         "uso_epi":1.5,"temperatura_":2.0,"tempo_":1.5,"pontos_agua_potavel_ok":1.5,"separacao_fluxo":1.5},
  "fis":{"integridade_":3.0,"estado_embalagem":3.0,"tampa_correta":2.5,"vedacao_adequada":2.5,
         "aspecto_visual":2.0,"protecao_contra_poeira":1.5,"malha_peneira_microns":2.0,
         "inspecao_fragmentos_cera_pos_centrifuga":2.0},
  "qui":{"laudo_residuos_agrotoxicos":3.0,"lubrificante_grau_alimentar":2.5,"vazamento_lubrificante":2.5,
         "conformidade_legislacao":2.0,"rotulo_presente":2.0,"informacoes_completas":2.0,
         "registro_lote":1.2,"segregacao_de_produtos_quimicos":2.0,"tipo_embalagem":1.5}
}

PESOS_ETAPA_EXTRA = {
  "recepcao":{"bio":{"temperatura_recebimento_c":2.0,"tempo_desde_coleta_h":2.0},
              "fis":{"integridade_containers":2.5,"sujeira_visivel_externa":2.0},
              "qui":{"transporte_segregado_de_quimicos":2.5,"documentacao_lote_ok":1.5}},
  "desoperculacao":{"bio":{"higienizacao_utensilios":2.5,"higiene_das_maos":2.5,"teor_umidade_mel_pct":3.0},
                    "fis":{"controle_particulas_plasticos_areia":2.5},
                    "qui":{"material_utensilios_grau_alimentar":2.0}},
  "centrifugacao":{"bio":{"limpeza_equipamento_pre_turno":2.5,"higiene_das_maos":2.0},
                   "fis":{"inspecao_fragmentos_cera_pos_centrifuga":2.5,"velocidade_centrifuga_rpm":1.8},
                   "qui":{"lubrificante_grau_alimentar":2.5,"vazamento_lubrificante":2.5}},
  "peneiragem":{"fis":{"malha_peneira_microns":2.5,"integridade_peneira_sem_rasgos":2.5,"contagem_residuos_retidos_pct":2.0}},
  "decantacao":{"fis":{"claridade_visual_nota":2.0,"tempo_decantacao_h":1.5},
                "bio":{"temperatura_decantacao_c":2.0}},
  "envase":{"bio":{"higienizacao_previa":3.0,"manipulador_higiene":2.5,"umidade_mel":3.0},
            "fis":{"estado_embalagem":3.0,"vedacao_adequada":2.5,"tampa_correta":2.5},
            "qui":{"tipo_embalagem":1.5,"registro_lote":1.5}},
  "rotulagem":{"bio":{"aviso_nao_recomendado_menores1ano":1.5},
               "qui":{"conformidade_legislacao":2.5,"informacoes_completas":2.0,"rotulo_presente":2.0},
               "fis":{"rotulo_intacto_sem_sujos":1.5}},
  "armazenamento":{"bio":{"temperatura_armazenamento_c":2.5,"umidade_relativa_ambiente_pct":2.0},
                   "fis":{"bombonas_integra_limpa":2.5,"lacres_integro":2.0},
                   "qui":{"segregacao_de_produtos_quimicos":2.5}},
  "expedicao":{"bio":{"temperatura_transporte_c":2.5,"tempo_transporte_h":2.0},
               "fis":{"veiculo_higienizado":2.0,"embalagem_secundaria_protecao":2.0},
               "qui":{"carga_compartilhada_quimicos":2.5}},
  "envase_rotulagem":{}
}

def _collect_pesos(etapa, perigo, cols):
    pesos = {}
    base = PESOS_BASE_RUIM.get(perigo, {})
    extra = PESOS_ETAPA_EXTRA.get(etapa, {}).get(perigo, {})
    def add(src):
        for k,w in src.items():
            if k.endswith("_"):
                for c in cols:
                    if c.startswith(k):
                        pesos[c] = max(pesos.get(c,0.0), float(w))
            else:
                if k in cols:
                    pesos[k] = max(pesos.get(k,0.0), float(w))
    add(base); add(extra)
    if not pesos:
        for c in cols:
            if c.endswith("_ok") or c.startswith("integridade_") or c in ("higienizacao_previa","higiene_das_maos","uso_epi"):
                pesos[c]=1.0
    return pesos

def _score(df, etapa, perigo):
    cols = list(df.columns)
    pesos = _collect_pesos(etapa, perigo, cols)
    if not pesos: return np.zeros(len(df))
    s = np.zeros(len(df), dtype=float)
    for c,w in pesos.items():
        if c in df.columns:
            s += w * _indicador_ruim(c, df[c]).to_numpy()
    max_peso = sum(pesos.values())
    return np.clip(100.0 * (s / max_peso), 0, 100) if max_peso>0 else np.zeros(len(df))

def _classe(score_norm):
    return np.digitize(score_norm, [15,40,70], right=False).astype(int)

def gerar_dataset(etapa, perigo, n=1500):
    assert etapa in ETAPAS
    assert perigo in PERIGOS
    df = _amostra(etapa, n)
    sc = _score(df, etapa, perigo)
    df["probabilidade"] = _classe(sc)
    base_ml = Path(__file__).resolve().parents[1]
    out_dir = base_ml / "dataset" / "mel" / etapa / perigo
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / f"dataset_{etapa}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    meta = {"etapa":etapa,"tipo_perigo":perigo,"amostras":int(n),"features":list(df.columns[:-1]),
            "faixas_alvo":{"0":"Desprezível","1":"Baixa","2":"Média","3":"Alta"}}
    (out_dir/"metadata.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False),encoding="utf-8")
    return str(csv_path), meta

def gerar_todas(n=1500):
    out=[]
    for e in ETAPAS:
        for p in PERIGOS:
            out.append(gerar_dataset(e,p,n))
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Gerador de datasets multi-etapas (mel) por tipo de perigo")
    ap.add_argument("--etapa", choices=ETAPAS+["all"], required=True)
    ap.add_argument("--perigo", choices=PERIGOS+["all"], required=True)
    ap.add_argument("--n", type=int, default=1500)
    args = ap.parse_args()

    etapas = ETAPAS if args.etapa=="all" else [args.etapa]
    perigos = PERIGOS if args.perigo=="all" else [args.perigo]

    for e in etapas:
        for p in perigos:
            path, _ = gerar_dataset(e,p,args.n)
            print(f"[OK] {e}/{p} -> {path}")
