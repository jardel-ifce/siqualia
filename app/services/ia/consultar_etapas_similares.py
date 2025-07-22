# app/services/consultar_etapas_similares.py

import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import spacy

model = SentenceTransformer("msmarco-distilbert-base-v4")

def consultar_etapas_similares(produto: str, etapa_digitada: str, top_n: int = 3, tipo_consulta: str = "etapa"):
    """
    Consulta etapas similares usando índices separados para etapas ou contexto completo.

    :param produto: Nome do produto (pasta do índice)
    :param etapa_digitada: Texto de entrada do usuário
    :param top_n: Número de resultados a retornar
    :param tipo_consulta: 'etapa' para nome da etapa ou 'contexto' para a linha completa
    :return: Lista dos resultados com similaridade
    """
    if tipo_consulta not in ["etapa", "contexto"]:
        raise ValueError("tipo_consulta deve ser 'etapa' ou 'contexto'.")

    indexes_dir = Path("indexes") / produto
    etapa_emb = model.encode([etapa_digitada], convert_to_numpy=True, normalize_embeddings=True)
    resultados = []

    for tipo in ["appcc", "pac", "bpf"]:
        index_path = indexes_dir / f"{tipo}_{tipo_consulta}.index"
        meta_path = indexes_dir / f"{tipo}_{tipo_consulta}.pkl"

        if not index_path.exists() or not meta_path.exists():
            continue

        index = faiss.read_index(str(index_path))
        with open(meta_path, "rb") as f:
            metadados = pickle.load(f)

        scores, ids = index.search(etapa_emb, 20)  # Busca top 15 para garantir resultados variados

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

    # Agrupa por etapa (mantendo maior similaridade por etapa)
    etapa_unicas = {}
    for r in resultados:
        chave = r["etapa"].lower()
        if chave not in etapa_unicas or r["similaridade"] > etapa_unicas[chave]["similaridade"]:
            etapa_unicas[chave] = r

    # Retorna top N resultados ordenados
    return sorted(etapa_unicas.values(), key=lambda r: r["similaridade"], reverse=True)[:top_n]
