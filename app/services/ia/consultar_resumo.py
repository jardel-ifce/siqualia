# 📁 app/services/ia/consultar_resumo.py

# 📦 Bibliotecas padrão
import faiss
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 🤖 Modelo de embeddings
model = SentenceTransformer("msmarco-distilbert-base-v4")

# ❓ Perguntas do Formulário I
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

# 🧰 Função auxiliar: prompt de consulta baseado no contexto
def gerar_prompt(contexto, pergunta):
    return (
        f"query: Produto: {contexto['produto']}. Etapa: {contexto['etapa']}. "
        f"Perigo identificado: ({contexto['tipo']}) {contexto['perigo']}. "
        f"Medida preventiva: {contexto['medida']}. Justificativa: {contexto['justificativa']}. {pergunta}"
    )

# 🧰 Função auxiliar: estrutura padrão de retorno vazio
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

# 🔍 Função principal: sugestão de respostas do Formulário I
def sugerir_resumo_dados(produto, etapa, tipo, perigo, medida, justificativa, origem="formulario_i"):
    base_path = Path("indexes") / produto
    index_path = base_path / f"{origem}_contexto.index"
    meta_path = base_path / f"{origem}_contexto.pkl"

    # Verifica se os arquivos existem
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

    # 🔎 Busca vetorial inicial baseada em etapa + tipo + perigo
    query_texto = f"{etapa.strip().lower()} - {tipo.strip().upper()} - {perigo.strip().lower()}"
    query_vector = model.encode(query_texto, convert_to_numpy=True, normalize_embeddings=True)

    vetores_meta = []
    indices_validos = []
    textos_candidatos = []

    for i, m in enumerate(metadados):
        etapa_m = m.get("etapa", "").strip().lower()
        tipo_m = m.get("tipo", "").strip().upper()
        perigo_m = m.get("perigo", "").strip().lower()

        if not etapa_m or not tipo_m or not perigo_m:
            continue

        texto_candidato = f"{etapa_m} - {tipo_m} - {perigo_m}"
        emb = model.encode(texto_candidato, convert_to_numpy=True, normalize_embeddings=True)
        vetores_meta.append(emb)
        textos_candidatos.append(texto_candidato)
        indices_validos.append(i)

    if not vetores_meta:
        print("[AVISO] Nenhum vetor de metadado válido encontrado.")
        return resposta_vazia()

    temp_index = faiss.IndexFlatIP(vetores_meta[0].shape[0])
    temp_index.add(np.array(vetores_meta))

    scores, idxs = temp_index.search(np.array([query_vector]), k=5)

    print(f"\n[DEBUG] Consulta: {query_texto}")
    for rank, idx in enumerate(idxs[0]):
        score = scores[0][rank]
        texto = textos_candidatos[idx]
        print(f" Rank {rank + 1}: Score={score:.4f} | Etapa-Tipo-Perigo: {texto}")

    candidatos = []
    for rank, i in enumerate(idxs[0]):
        score = scores[0][rank]
        if score > 0.7:
            candidatos.append((indices_validos[i], metadados[indices_validos[i]]))

    if not candidatos:
        print("[AVISO] Nenhum candidato suficientemente semelhante encontrado.")
        return resposta_vazia()

    # Cria subíndice vetorial só com os candidatos relevantes
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
