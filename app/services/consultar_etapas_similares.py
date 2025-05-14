import faiss
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import spacy

model = SentenceTransformer("all-MiniLM-L6-v2")
nlp = spacy.load("pt_core_news_sm")

def lematizar(texto: str) -> str:
    doc = nlp(texto)
    return " ".join([t.lemma_ for t in doc if not t.is_stop and t.is_alpha])

def consultar_etapas_similares(prodto: str, etapa_digitada: str, top_n: int = 3):
    indexes_dir = Path("indexes") / produto
    etapa_emb = model.encode([lematizar(etapa_digitada)], convert_to_numpy=True, normalize_embeddings=True)

    resultados = []

    for tipo in ["appcc", "pac", "bpf"]:
        index_path = indexes_dir / f"{tipo}.index"
        meta_path = indexes_dir / f"{tipo}.pkl"

        if not index_path.exists() or not meta_path.exists():
            continue

        index = faiss.read_index(str(index_path))
        with open(meta_path, "rb") as f:
            metadados = pickle.load(f)

        scores, ids = index.search(etapa_emb, 10)

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

    # Agrupa por etapa (mantendo maior similaridade)
    etapa_unicas = {}
    for r in resultados:
        chave = r["etapa"].lower()
        if chave not in etapa_unicas or r["similaridade"] > etapa_unicas[chave]["similaridade"]:
            etapa_unicas[chave] = r

    return sorted(etapa_unicas.values(), key=lambda r: r["similaridade"], reverse=True)[:top_n]
