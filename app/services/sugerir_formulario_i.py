# app/services/sugerir_formulario_i.py
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/e5-base-v2")

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

def sugerir_formulario_i_dados(produto, etapa, tipo, perigo, medida, justificativa, origem="appcc"):
    base_path = Path("indexes") / produto
    index_path = base_path / f"{origem}.index"
    meta_path = base_path / f"{origem}.pkl"

    if not index_path.exists() or not meta_path.exists():
        return None

    index = faiss.read_index(str(index_path))
    with open(meta_path, "rb") as f:
        metadados = pickle.load(f)

    contexto = {
        "produto": produto,
        "etapa": etapa,
        "tipo": tipo,
        "perigo": perigo,
        "medida": medida,
        "justificativa": justificativa
    }

    def buscar_resposta(chave):
        prompt = gerar_prompt(contexto, PERGUNTAS_FORMULARIO_I[chave])
        query_emb = model.encode([prompt], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = index.search(query_emb, 3)
        for idx in ids[0]:
            if 0 <= idx < len(metadados):
                texto = metadados[idx]["page_content"]
                frase = texto.split(".")[0].strip()
                if frase:
                    return frase + "."
        return ""

    return {
        "limite_critico": buscar_resposta("limite_critico"),
        "monitoramento": {
            "oque": buscar_resposta("monitoramento.oque"),
            "como": buscar_resposta("monitoramento.como"),
            "quando": buscar_resposta("monitoramento.quando"),
            "quem": buscar_resposta("monitoramento.quem")
        },
        "acao_corretiva": buscar_resposta("acao_corretiva"),
        "registro": buscar_resposta("registro"),
        "verificacao": buscar_resposta("verificacao")
    }
