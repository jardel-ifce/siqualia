# teste3/ml/feature_schema.py
from __future__ import annotations
from typing import Dict, Any, List

# =========================
# Constantes globais
# =========================
ETAPAS = [
    "recepcao","desoperculacao","centrifugacao","peneiragem",
    "decantacao","envase","rotulagem","armazenamento","expedicao",
    "envase_rotulagem"
]
PERIGOS = ["bio","fis","qui"]
CLASSES = {0:"DESPREZÍVEL",1:"BAIXA",2:"MÉDIA",3:"ALTA"}

# Convenções de enums
SIMNAO = [{"label":"Não","value":0},{"label":"Sim","value":1}]
TRINIVEL_RMQ = [  # Ruim/Médio/Boa ou Inadequada/Parcial/Adequada (ajuste semântico via label do campo)
    {"label":"Baixo/ruim/inadequado","value":0},
    {"label":"Médio/regular/parcial","value":1},
    {"label":"Alto/bom/adequado","value":2},
]

# =========================
# Schema por etapa
# (NOMES ALINHADOS ao dataset_generator.py)
# Cada item tem: type, label, options/unit, help, aplica (lista de perigos)
# =========================

FEATURES_SCHEMA_BY_ETAPA: Dict[str, Dict[str, Any]] = {

    # ---------- RECEPÇÃO ----------
    "recepcao": {
        "fornecedor_auditado": {
            "type":"enum","label":"Fornecedor auditado/qualificado","options":SIMNAO,
            "help":"Fornecedor com auditoria ou avaliação vigente.","aplica":["bio","qui"]
        },
        "laudo_residuos_agrotoxicos": {
            "type":"enum","label":"Laudo de resíduos de agrotóxicos","options":SIMNAO,
            "help":"Apresentação de laudo do lote/fornecedor.","aplica":["qui"]
        },
        "temperatura_recebimento_c": {
            "type":"range","label":"Temperatura no recebimento","unit":"°C","min":5,"max":40,"step":1,
            "help":"Condição térmica na chegada do lote.","aplica":["bio"]
        },
        "tempo_desde_coleta_h": {
            "type":"range","label":"Tempo desde a coleta","unit":"h","min":0,"max":240,"step":1,
            "help":"Horas entre coleta e recebimento.","aplica":["bio"]
        },
        "integridade_containers": {
            "type":"enum","label":"Integridade dos containers","options":[
                {"label":"Comprometida","value":0},{"label":"Íntegra","value":1}
            ],
            "help":"Amassados, trincas, tampa frouxa, etc.","aplica":["fis"]
        },
        "sujeira_visivel_externa": {
            "type":"enum","label":"Sujeira visível externa","options":SIMNAO,
            "help":"Indícios de sujidade nas embalagens/recipientes.","aplica":["fis","bio"]
        },
        "umidade_lote_pct": {
            "type":"range","label":"Umidade do lote","unit":"%","min":16,"max":24,"step":1,
            "help":"Faixas típicas para mel; ↑ umidade favorece leveduras/osmófilos.","aplica":["bio"]
        },
        "documentacao_lote_ok": {
            "type":"enum","label":"Documentação do lote conferida","options":SIMNAO,
            "help":"Romaneio/nota/COA/declarações revisados.","aplica":["qui"]
        },
        "transporte_segregado_de_quimicos": {
            "type":"enum","label":"Transporte segregado de químicos","options":SIMNAO,
            "help":"Evitar co-transporte com cargas químicas voláteis.","aplica":["qui"]
        },
        "lacre_viagem_integro": {
            "type":"enum","label":"Lacre de viagem íntegro","options":SIMNAO,
            "help":"Sem ruptura/violação.","aplica":["fis"]
        },
        "lote_identificado": {
            "type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Identificação do lote visível na chegada.","aplica":["bio","fis","qui"]
        },
    },

    # ---------- DESOPERCULAÇÃO ----------
    "desoperculacao": {
        "higienizacao_utensilios":{
            "type":"enum","label":"Higienização de utensílios","options":SIMNAO,
            "help":"Utensílios limpos/sanitizados antes do uso.","aplica":["bio"]
        },
        "material_utensilios_grau_alimentar":{
            "type":"enum","label":"Material dos utensílios (grau alimentício)","options":SIMNAO,
            "help":"Evitar migração de materiais inadequados.","aplica":["qui"]
        },
        "uso_epi":{
            "type":"enum","label":"Uso de EPI","options":[
                {"label":"Nenhum","value":0},{"label":"Parcial","value":1},{"label":"Completo","value":2}
            ],
            "help":"Luvas, touca, avental etc.","aplica":["bio"]
        },
        "higiene_das_maos":{
            "type":"enum","label":"Higiene das mãos","options":SIMNAO,
            "help":"Lavagem/antissepsia adequada e frequente.","aplica":["bio"]
        },
        "teor_umidade_mel_pct":{
            "type":"range","label":"Umidade do mel (quadros)","unit":"%","min":16,"max":24,"step":1,
            "help":"↑ umidade favorece leveduras/osmófilos.","aplica":["bio"]
        },
        "controle_particulas_plasticos_areia":{
            "type":"enum","label":"Controle de partículas (plástico/areia)","options":SIMNAO,
            "help":"Prevenção/remoção de partículas durante corte.","aplica":["fis"]
        },
        "pontos_agua_potavel_ok":{
            "type":"enum","label":"Água potável disponível para higienização","options":SIMNAO,
            "help":"Uso de água potável para limpeza.","aplica":["bio","qui"]
        },
        "separacao_fluxo_cru_pronto":{
            "type":"enum","label":"Separação de fluxo cru/pronto","options":SIMNAO,
            "help":"Evita contaminação cruzada.","aplica":["bio"]
        },
        "lote_identificado":{
            "type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Rastreabilidade nas operações.","aplica":["bio","fis","qui"]
        },
    },

    # ---------- CENTRIFUGAÇÃO ----------
    "centrifugacao": {
        "velocidade_centrifuga_rpm":{
            "type":"range","label":"Velocidade da centrífuga","unit":"rpm","min":200,"max":800,"step":10,
            "help":"Ajuste conforme equipamento e quadro.","aplica":["fis"]
        },
        "tempo_centrifugacao_min":{
            "type":"range","label":"Tempo de centrifugação","unit":"min","min":2,"max":60,"step":1,
            "help":"Tempo excessivo ↑ risco físico/qualidade.","aplica":["fis","bio"]
        },
        "limpeza_equipamento_pre_turno":{
            "type":"enum","label":"Limpeza do equipamento (pré-turno)","options":SIMNAO,
            "help":"Limpeza/sanitização antes de iniciar.","aplica":["bio"]
        },
        "lubrificante_grau_alimentar":{
            "type":"enum","label":"Lubrificante de grau alimentício","options":SIMNAO,
            "help":"Evitar contaminação química.","aplica":["qui"]
        },
        "vazamento_lubrificante":{
            "type":"enum","label":"Vazamento de lubrificante","options":SIMNAO,
            "help":"Risco de contaminação química.","aplica":["qui"]
        },
        "uso_epi":{
            "type":"enum","label":"Uso de EPI","options":[
                {"label":"Nenhum","value":0},{"label":"Parcial","value":1},{"label":"Completo","value":2}
            ],
            "help":"Proteção do operador.","aplica":["bio"]
        },
        "higiene_das_maos":{
            "type":"enum","label":"Higiene das mãos","options":SIMNAO,
            "help":"Boa prática de manipulação.","aplica":["bio"]
        },
        "inspecao_fragmentos_cera_pos_centrifuga":{
            "type":"enum","label":"Inspeção de fragmentos de cera (pós-centrífuga)","options":SIMNAO,
            "help":"Controle de partículas sólidas.","aplica":["fis"]
        },
        "lote_identificado":{
            "type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Rastreabilidade.","aplica":["bio","fis","qui"]
        },
    },

    # ---------- PENEIRAGEM ----------
    "peneiragem": {
        "malha_peneira_microns":{
            "type":"range","label":"Abertura da malha da peneira","unit":"µm","min":200,"max":1200,"step":50,
            "help":"Quanto menor, maior retenção de partículas.","aplica":["fis"]
        },
        "integridade_peneira_sem_rasgos":{
            "type":"enum","label":"Integridade da peneira (sem rasgos)","options":SIMNAO,
            "help":"Evitar passagem de fragmentos.","aplica":["fis"]
        },
        "frequencia_troca_peneira_h":{
            "type":"range","label":"Frequência de troca da peneira","unit":"h","min":1,"max":24,"step":1,
            "help":"Trocas regulares mantêm eficiência.","aplica":["fis"]
        },
        "higienizacao_peneira_pos_lote":{
            "type":"enum","label":"Higienização da peneira (pós-lote)","options":SIMNAO,
            "help":"Evita biofilme/contaminação.","aplica":["bio"]
        },
        "contagem_residuos_retidos_pct":{
            "type":"range","label":"Resíduos retidos na peneira","unit":"%","min":0,"max":5,"step":0.1,
            "help":"Indicador de carga de sólidos.","aplica":["fis"]
        },
        "protecao_contra_poeira":{
            "type":"enum","label":"Proteção contra poeira","options":SIMNAO,
            "help":"Ambiente controlado.","aplica":["fis"]
        },
        "separacao_fluxo":{
            "type":"enum","label":"Separação de fluxos (limpo/sujo)","options":SIMNAO,
            "help":"Evitar contaminação cruzada.","aplica":["bio"]
        },
        "lote_identificado":{
            "type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Rastreabilidade.","aplica":["bio","fis","qui"]
        },
    },

    # ---------- DECANTAÇÃO ----------
    "decantacao": {
        "tempo_decantacao_h":{
            "type":"range","label":"Tempo de decantação","unit":"h","min":0,"max":72,"step":1,
            "help":"Tempo para separação de impurezas/bolhas.","aplica":["fis","bio"]
        },
        "temperatura_decantacao_c":{
            "type":"range","label":"Temperatura de decantação","unit":"°C","min":10,"max":40,"step":1,
            "help":"Influencia viscosidade e fluxo.","aplica":["bio"]
        },
        "tanque_limpio_sanitizado":{
            "type":"enum","label":"Tanque limpo/sanitizado","options":SIMNAO,
            "help":"Condição higiênica do tanque.","aplica":["bio"]
        },
        "cobertura_anti_pragas":{
            "type":"enum","label":"Cobertura/Proteção contra pragas","options":SIMNAO,
            "help":"Evita queda de partículas/pragas.","aplica":["fis","bio"]
        },
        "remocao_espuma_impurezas":{
            "type":"enum","label":"Remoção de espuma/impurezas","options":SIMNAO,
            "help":"Controle de partículas visíveis.","aplica":["fis"]
        },
        "material_tanque_inox_grau_alimentar":{
            "type":"enum","label":"Tanque inox (grau alimentício)","options":SIMNAO,
            "help":"Evita migração de materiais.","aplica":["qui"]
        },
        "claridade_visual_nota":{
            "type":"range","label":"Claridade visual (nota)","min":0,"max":2,"step":1,
            "help":"0=ruim, 1=média, 2=boa (indicador simples).","aplica":["fis"]
        },
        "lote_identificado":{
            "type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Rastreabilidade.","aplica":["bio","fis","qui"]
        },
    },

    # ---------- ENVASE ----------
    "envase": {
        "tipo_embalagem":{
            "type":"enum","label":"Tipo de embalagem","options":[
                {"label":"Vidro","value":0},{"label":"PET grau alimentício","value":1},{"label":"Outro aprovado","value":2}
            ],
            "help":"Materiais compatíveis com alimento.","aplica":["qui","fis"]
        },
        "estado_embalagem":{
            "type":"enum","label":"Estado da embalagem","options":[
                {"label":"Danificada","value":0},{"label":"Íntegra","value":1}
            ],
            "help":"Amassados/fissuras comprometem a vedação.","aplica":["fis"]
        },
        "tampa_correta":{
            "type":"enum","label":"Tampa correta/apertada","options":SIMNAO,
            "help":"Fechamento adequado.","aplica":["fis"]
        },
        "vedacao_adequada":{
            "type":"enum","label":"Vedações adequadas","options":SIMNAO,
            "help":"Prevenção de entrada de partículas/umidade.","aplica":["fis"]
        },
        "higienizacao_previa":{
            "type":"enum","label":"Higienização prévia da linha","options":[
                {"label":"Ausente","value":0},{"label":"Parcial","value":1},{"label":"Adequada","value":2}
            ],
            "help":"Condição antes de iniciar o envase.","aplica":["bio"]
        },
        "uso_epi":{
            "type":"enum","label":"Uso de EPI","options":[
                {"label":"Nenhum","value":0},{"label":"Parcial","value":1},{"label":"Completo","value":2}
            ],
            "help":"Proteção do operador.","aplica":["bio"]
        },
        "local_envase":{
            "type":"enum","label":"Condição do local de envase","options":[
                {"label":"Inadequado","value":0},{"label":"Adequado","value":1}
            ],
            "help":"Ambiente controlado.","aplica":["bio","fis"]
        },
        "manipulador_higiene":{
            "type":"enum","label":"Higiene do manipulador","options":[
                {"label":"Ruim","value":0},{"label":"Regular","value":1},{"label":"Boa","value":2}
            ],
            "help":"Práticas pessoais (mãos, EPI, paramentação).","aplica":["bio"]
        },
        "aspecto_visual":{
            "type":"enum","label":"Aspecto visual do mel","options":[
                {"label":"Anômalo","value":0},{"label":"Dentro do padrão","value":1},{"label":"Excelente","value":2}
            ],
            "help":"Turbidez, espuma, partículas.","aplica":["fis"]
        },
        "umidade_mel":{
            "type":"enum","label":"Umidade do mel","options":[
                {"label":"≤ 18%","value":0},{"label":"18–20%","value":1},{"label":"> 20%","value":2}
            ],
            "help":"↑ umidade favorece leveduras/osmófilos.","aplica":["bio"]
        },
        "temperatura_envase":{
            "type":"range","label":"Temperatura no envase","unit":"°C","min":18,"max":60,"step":1,
            "help":"Temperatura do mel/equipamento no envase.","aplica":["bio"]
        },
        "cristalizacao":{
            "type":"enum","label":"Cristalização presente","options":SIMNAO,
            "help":"Fenômeno físico (não necessariamente defeito).","aplica":["fis"]
        },
        "rotulo_presente":{
            "type":"enum","label":"Rótulo presente","options":SIMNAO,
            "help":"Exigência legal.","aplica":["qui"]
        },
        "informacoes_completas":{
            "type":"enum","label":"Informações do rótulo completas","options":SIMNAO,
            "help":"Lista de ingredientes/origem/alertas etc.","aplica":["qui"]
        },
        "data_validade_legivel":{
            "type":"enum","label":"Data de validade legível","options":SIMNAO,
            "help":"Sem borrões/ilegibilidade.","aplica":["qui"]
        },
        "lote_identificado":{
            "type":"enum","label":"Lote identificado na embalagem","options":SIMNAO,
            "help":"Rastreabilidade do produto.","aplica":["bio","fis","qui"]
        },
        "registro_lote":{
            "type":"enum","label":"Registro de lote (documental)","options":SIMNAO,
            "help":"Registros do lote disponíveis.","aplica":["qui"]
        },
        "treinamento_equipe":{
            "type":"enum","label":"Treinamento da equipe","options":[
                {"label":"Sem","value":0},{"label":"Básico","value":1},{"label":"Atualizado","value":2}
            ],
            "help":"Capacitação e reciclagem.","aplica":["bio"]
        },
        "historico_reclamacoes":{
            "type":"range","label":"Reclamações no período","min":0,"max":50,"step":1,
            "help":"Indicador de qualidade do lote/período.","aplica":["fis","qui","bio"]
        },
        "tempo_exposicao_ar":{
            "type":"range","label":"Tempo de exposição ao ar","unit":"min","min":0,"max":60,"step":1,
            "help":"Maior exposição → ↑ risco partículas/oxidação.","aplica":["fis","bio"]
        },
    },

    # ---------- ROTULAGEM ----------
    "rotulagem": {
        "rotulo_presente":{"type":"enum","label":"Rótulo presente","options":SIMNAO,
            "help":"Exigência legal.","aplica":["qui"]},
        "informacoes_completas":{"type":"enum","label":"Informações completas no rótulo","options":SIMNAO,
            "help":"Conformidade com legislação.","aplica":["qui"]},
        "data_validade_legivel":{"type":"enum","label":"Data de validade legível","options":SIMNAO,
            "help":"Sem borrões/ilegibilidade.","aplica":["qui"]},
        "lote_identificado":{"type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Rastreabilidade.","aplica":["bio","fis","qui"]},
        "aviso_nao_recomendado_menores1ano":{"type":"enum","label":"Aviso 'não recomendado <1 ano'","options":SIMNAO,
            "help":"Requisito sanitário para mel.","aplica":["bio","qui"]},
        "conformidade_legislacao":{"type":"enum","label":"Conformidade com legislação","options":SIMNAO,
            "help":"Rotulagem em conformidade normativa.","aplica":["qui"]},
        "rotulo_intacto_sem_sujos":{"type":"enum","label":"Rótulo intacto/sem sujidade","options":SIMNAO,
            "help":"Integridade física do rótulo.","aplica":["fis"]},
        "registro_lote":{"type":"enum","label":"Registro de lote (documental)","options":SIMNAO,
            "help":"Registros mantidos/arquivados.","aplica":["qui"]},
    },

    # ---------- ARMAZENAMENTO ----------
    "armazenamento": {
        "temperatura_armazenamento_c":{"type":"range","label":"Temperatura de armazenamento","unit":"°C","min":10,"max":35,"step":1,
            "help":"Condição térmica do depósito.","aplica":["bio"]},
        "umidade_relativa_ambiente_pct":{"type":"range","label":"Umidade relativa do ambiente","unit":"%","min":20,"max":100,"step":1,
            "help":"Condição do ar/umidade.","aplica":["bio"]},
        "tempo_armazenado_dias":{"type":"range","label":"Tempo armazenado","unit":"dias","min":0,"max":365,"step":1,
            "help":"Tempo total até expedição.","aplica":["bio"]},
        "bombonas_integra_limpa":{"type":"enum","label":"Bombonas íntegras/limpas","options":SIMNAO,
            "help":"Integridade e limpeza de recipientes a granel.","aplica":["fis"]},
        "lacres_integro":{"type":"enum","label":"Lacres íntegros","options":SIMNAO,
            "help":"Sem violação dos recipientes.","aplica":["fis"]},
        "segregacao_de_produtos_quimicos":{"type":"enum","label":"Segregação de produtos químicos","options":SIMNAO,
            "help":"Evitar proximidade com químicos.","aplica":["qui"]},
        "piso_limpo_seco":{"type":"enum","label":"Piso limpo e seco","options":SIMNAO,
            "help":"Condição higiênica do armazém.","aplica":["bio","fis"]},
        "PEPS_FEFO_aplicado":{"type":"enum","label":"PEPS/FEFO aplicado","options":SIMNAO,
            "help":"Gestão de estoque por validade.","aplica":["qui","bio"]},
        "lote_identificado":{"type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Rastreabilidade no estoque.","aplica":["bio","fis","qui"]},
    },

    # ---------- EXPEDIÇÃO ----------
    "expedicao": {
        "temperatura_transporte_c":{"type":"range","label":"Temperatura durante transporte","unit":"°C","min":5,"max":40,"step":1,
            "help":"Condição térmica na expedição.","aplica":["bio"]},
        "tempo_transporte_h":{"type":"range","label":"Tempo de transporte","unit":"h","min":0,"max":72,"step":1,
            "help":"Janela de entrega.","aplica":["bio"]},
        "veiculo_higienizado":{"type":"enum","label":"Veículo higienizado","options":SIMNAO,
            "help":"Condição higiênica do compartimento.","aplica":["bio","fis"]},
        "carga_compartilhada_quimicos":{"type":"enum","label":"Carga compartilhada com químicos","options":SIMNAO,
            "help":"Risco de migração/odor/contato.","aplica":["qui"]},
        "embalagem_secundaria_protecao":{"type":"enum","label":"Embalagem secundária de proteção","options":SIMNAO,
            "help":"Proteção contra poeira/impactos.","aplica":["fis"]},
        "lacres_veiculo_integridade":{"type":"enum","label":"Lacres do veículo íntegros","options":SIMNAO,
            "help":"Integridade/violação do veículo.","aplica":["fis"]},
        "registro_condicoes_transporte":{"type":"enum","label":"Registro das condições de transporte","options":SIMNAO,
            "help":"Registros de temperatura/rota etc.","aplica":["qui","bio"]},
        "lote_identificado":{"type":"enum","label":"Lote identificado","options":SIMNAO,
            "help":"Rastreabilidade na expedição.","aplica":["bio","fis","qui"]},
    },

    # ---------- ETAPA COMPOSTA ----------
    "envase_rotulagem": {
        # será a união de envase + rotulagem via helper abaixo
    },
}

# =========================
# Helpers
# =========================

def _merge_envase_rotulagem() -> Dict[str, Any]:
    env = FEATURES_SCHEMA_BY_ETAPA.get("envase", {})
    rot = FEATURES_SCHEMA_BY_ETAPA.get("rotulagem", {})
    merged = dict(env)
    # não sobrescrever campos iguais; manter labels/ajuda de envase
    for k,v in rot.items():
        merged.setdefault(k, v)
    return merged

def schema_for_etapa(etapa: str, perigo: str | None = None, only_perigo: bool = False) -> Dict[str, Any]:
    """
    Retorna o schema completo para a etapa.
    - Se perigo for informado e only_perigo=True, filtra para campos cujo 'aplica' contém o perigo.
    - Caso contrário, retorna todos os campos definidos para a etapa.
    """
    etapa = (etapa or "").strip().lower()
    if etapa == "envase_rotulagem":
        base = _merge_envase_rotulagem()
    else:
        base = FEATURES_SCHEMA_BY_ETAPA.get(etapa, {}).copy()

    if not perigo or not only_perigo:
        return base

    p = perigo.strip().lower()
    out = {}
    for k, meta in base.items():
        aplica: List[str] = meta.get("aplica", ["bio","fis","qui"])
        if p in aplica:
            out[k] = meta
    return out
