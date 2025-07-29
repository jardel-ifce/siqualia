import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("msmarco-distilbert-base-v4")

PERGUNTAS_FORMULARIO_I = {
    "limite_critico": "Qual o limite crítico necessário para garantir que esse perigo esteja sob controle?",
    "monitoramento.oque": "O que deve ser monitorado para garantir o controle desse perigo?",
    "monitoramento.como": "Como o monitoramento deve ser realizado?",
    "monitoramento.quando": "Com que frequência o monitoramento deve ocorrer?",
    "monitoramento.quem": "Quem é o responsável por realizar o monitoramento?",
    "acao_corretiva": "Qual ação corretiva deve ser tomada se o perigo não estiver controlado?",
    "registro": "Quais registros devem ser mantidos para comprovar o controle?",
    "verificacao": "Como verificar se o controle do perigo está sendo efetivo?"
}

def gerar_prompt(contexto, pergunta):
    return (
        f"query: Produto: {contexto['produto']}. Etapa: {contexto['etapa']}. "
        f"Perigo identificado: ({contexto['tipo']}) {contexto['perigo']}. "
        f"Medida preventiva: {contexto['medida']}. Justificativa: {contexto['justificativa']}. {pergunta}"
    )

def sugerir_resumo_dados(produto, etapa, tipo, perigo, medida, justificativa, origem="formulario_i"):
    base_path = Path("indexes") / produto
    index_path = base_path / f"{origem}_contexto.index"
    meta_path = base_path / f"{origem}_contexto.pkl"

    if not index_path.exists() or not meta_path.exists():
        print(f"[AVISO] Índices não encontrados para {produto}/{origem}")
        return resposta_vazia()

    try:
        index = faiss.read_index(str(index_path))
        with open(meta_path, "rb") as f:
            metadados = pickle.load(f)
    except Exception as e:
        print(f"[ERRO] Falha ao carregar índice ou metadados: {e}")
        return resposta_vazia()

    etapa_f = etapa.strip().lower()
    perigo_f = perigo.strip().lower()
    tipo_f = tipo.strip().upper()

    candidatos = [
        (i, m) for i, m in enumerate(metadados)
        if m.get("etapa", "").strip().lower() == etapa_f
        and m.get("perigo", "").strip().lower() == perigo_f
        and m.get("tipo", "").strip().upper() == tipo_f
    ]

    if not candidatos:
        print(f"[AVISO] Nenhum candidato compatível encontrado para etapa/perigo/tipo.")
        return resposta_vazia()

    sentencas = [
        " - ".join(str(v) for v in m.values() if str(v).strip()) for _, m in candidatos
    ]
    sub_emb = model.encode(sentencas, convert_to_numpy=True, normalize_embeddings=True)
    sub_index = faiss.IndexFlatIP(sub_emb.shape[1])
    sub_index.add(sub_emb)

    contexto = {
        "produto": produto,
        "etapa": etapa,
        "tipo": tipo,
        "perigo": perigo,
        "medida": medida,
        "justificativa": justificativa
    }

    def buscar_resposta(chave, campo_csv):
        prompt = gerar_prompt(contexto, PERGUNTAS_FORMULARIO_I[chave])
        query_emb = model.encode([prompt], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = sub_index.search(query_emb, 3)

        for idx in ids[0]:
            i_real, meta = candidatos[idx]
            valor = meta.get(campo_csv, "").strip()
            if valor:
                return valor
        return ""

    return {
        "limite_critico": buscar_resposta("limite_critico", "limite_critico"),
        "monitoramento": {
            "oque": buscar_resposta("monitoramento.oque", "monitoramento_oque"),
            "como": buscar_resposta("monitoramento.como", "monitoramento_como"),
            "quando": buscar_resposta("monitoramento.quando", "monitoramento_quando"),
            "quem": buscar_resposta("monitoramento.quem", "monitoramento_quem")
        },
        "acao_corretiva": buscar_resposta("acao_corretiva", "acao_corretiva"),
        "registro": buscar_resposta("registro", "registro"),
        "verificacao": buscar_resposta("verificacao", "verificacao")
    }

def resposta_vazia():
    return {
        "limite_critico": "",
        "monitoramento": {
            "oque": "",
            "como": "",
            "quando": "",
            "quem": ""
        },
        "acao_corretiva": "",
        "registro": "",
        "verificacao": ""
    }
