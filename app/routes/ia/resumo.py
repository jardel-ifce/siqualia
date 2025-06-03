from pathlib import Path
import faiss
import pickle
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

PERGUNTAS_FORM_I = {
    "limite_critico": "Qual o limite crítico necessário para garantir que esse perigo esteja sob controle?",
    "monitoramento.oque": "O que deve ser monitorado para garantir o controle desse perigo?",
    "monitoramento.como": "Como o monitoramento deve ser realizado?",
    "monitoramento.quando": "Com que frequência o monitoramento deve ocorrer?",
    "monitoramento.quem": "Quem é o responsável por realizar o monitoramento?",
    "acao_corretiva": "Qual ação corretiva deve ser tomada se o perigo não estiver controlado?",
    "registro": "Quais registros devem ser mantidos para comprovar o controle?",
    "verificacao": "Como verificar se o controle do perigo está sendo efetivo?"
}

def gerar_prompt(ctx, pergunta):
    return (
        f"query: Produto: {ctx['produto']}. Etapa: {ctx['etapa']}. "
        f"Perigo identificado: ({ctx['tipo']}) {ctx['perigo']}. "
        f"Medida preventiva: {ctx['medida']}. Justificativa: {ctx['justificativa']}. {pergunta}"
    )

def sugerir_resumo(produto, etapa, tipo, perigo, medida, justificativa, origem="formulario_i"):
    base = Path("indexes") / produto
    index_path = base / f"{origem}.index"
    meta_path = base / f"{origem}.pkl"

    if not index_path.exists() or not meta_path.exists():
        return None

    index = faiss.read_index(str(index_path))
    with open(meta_path, "rb") as f:
        metadados = pickle.load(f)

    etapa_f = etapa.lower().strip()
    perigo_f = perigo.lower().strip()
    tipo_f = tipo.upper().strip()

    candidatos = [
        (i, m) for i, m in enumerate(metadados)
        if m.get("etapa", "").lower() == etapa_f and
           m.get("perigo", "").lower() == perigo_f and
           m.get("tipo", "").upper() == tipo_f
    ]
    if not candidatos:
        return None

    sentencas = [" - ".join(str(v) for v in m.values() if str(v).strip()) for _, m in candidatos]
    sub_emb = model.encode(sentencas, convert_to_numpy=True, normalize_embeddings=True)
    sub_index = faiss.IndexFlatIP(sub_emb.shape[1])
    sub_index.add(sub_emb)

    contexto = {"produto": produto, "etapa": etapa, "tipo": tipo, "perigo": perigo, "medida": medida, "justificativa": justificativa}

    def buscar(chave, campo):
        prompt = gerar_prompt(contexto, PERGUNTAS_FORM_I[chave])
        query_emb = model.encode([prompt], convert_to_numpy=True, normalize_embeddings=True)
        scores, ids = sub_index.search(query_emb, 3)
        for idx in ids[0]:
            _, meta = candidatos[idx]
            valor = meta.get(campo, "").strip()
            if valor:
                return valor
        return ""

    return {
        "limite_critico": buscar("limite_critico", "limite_critico"),
        "monitoramento": {
            "oque": buscar("monitoramento.oque", "monitoramento_oque"),
            "como": buscar("monitoramento.como", "monitoramento_como"),
            "quando": buscar("monitoramento.quando", "monitoramento_quando"),
            "quem": buscar("monitoramento.quem", "monitoramento_quem")
        },
        "acao_corretiva": buscar("acao_corretiva", "acao_corretiva"),
        "registro": buscar("registro", "registro"),
        "verificacao": buscar("verificacao", "verificacao")
    }