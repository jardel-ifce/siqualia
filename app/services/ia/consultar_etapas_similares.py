# app/services/consultar_etapas_similares.py

# 📦 Bibliotecas externas
import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 🔧 Inicialização do modelo de embeddings
model = SentenceTransformer("msmarco-distilbert-base-v4")

# 🔍 Função principal para busca de etapas similares
def consultar_etapas_similares(
    produto: str,
    etapa: str,
    top_n: int = 3,
    tipo_consulta: str = "etapa"
):
    """
    Consulta etapas similares usando FAISS e embeddings.

    Parâmetros:
    - produto: nome da pasta de índice (ex: 'mel', 'queijo')
    - etapa_digitada: texto da etapa informado pelo usuário
    - top_n: número máximo de resultados retornados
    - tipo_consulta: 'etapa' (nome da etapa) ou 'contexto' (linha completa)

    Retorna:
    - Lista de etapas similares com origem e pontuação de similaridade
    """
    if tipo_consulta not in ["etapa", "contexto"]:
        raise ValueError("tipo_consulta deve ser 'etapa' ou 'contexto'.")

    indexes_dir = Path("indexes") / produto
    etapa_emb = model.encode([etapa], convert_to_numpy=True, normalize_embeddings=True)
    resultados = []

    for tipo in ["appcc", "pac", "bpf"]:
        index_path = indexes_dir / f"{tipo}_{tipo_consulta}.index"
        meta_path = indexes_dir / f"{tipo}_{tipo_consulta}.pkl"

        if not index_path.exists() or not meta_path.exists():
            continue

        index = faiss.read_index(str(index_path))
        with open(meta_path, "rb") as f:
            metadados = pickle.load(f)

        scores, ids = index.search(etapa_emb, 20)

        for score, idx in zip(scores[0], ids[0]):
            if idx < 0 or idx >= len(metadados):
                continue
            etapa = metadados[idx].get("etapa")
            if etapa:
                resultados.append({
                    "etapa": etapa.strip(),
                    "origem": tipo,
                    "similaridade": round(float(score), 4)
                })

    if not resultados:
        return []

    # Agrupa por etapa mantendo apenas a com maior similaridade
    etapa_unicas = {}
    for r in resultados:
        chave = r["etapa"].lower()
        if chave not in etapa_unicas or r["similaridade"] > etapa_unicas[chave]["similaridade"]:
            etapa_unicas[chave] = r

    return sorted(etapa_unicas.values(), key=lambda r: r["similaridade"], reverse=True)[:top_n]