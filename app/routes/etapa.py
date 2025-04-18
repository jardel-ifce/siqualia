from fastapi import APIRouter
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from app.utils.dados import carregar_documentos

router = APIRouter(prefix="/etapa", tags=["Etapas"])

model = SentenceTransformer("all-MiniLM-L6-v2")
SIMILARIDADE_LIMITE = 0.4

class EtapaRequest(BaseModel):
    produto: str
    etapa: str

@router.post("/pesquisar")
def pesquisar_etapa(request: EtapaRequest):
    documentos = carregar_documentos(request.produto)
    query_embedding = model.encode(request.etapa, convert_to_tensor=True)
    doc_embeddings = {
        doc["id"]: model.encode(doc["etapa"], convert_to_tensor=True)
        for doc in documentos
    }

    similarities = {
        doc_id: util.pytorch_cos_sim(query_embedding, emb)[0].item()
        for doc_id, emb in doc_embeddings.items()
    }

    best_id = max(similarities, key=similarities.get)
    best_sim = similarities[best_id]

    if best_sim < SIMILARIDADE_LIMITE:
        return {
            "etapa": request.etapa,
            "contexto_valido": False,
            "similaridade": best_sim,
            "mensagem": "Etapa não corresponde ao contexto do produto."
        }

    etapa_encontrada = next(doc for doc in documentos if doc["id"] == best_id)
    return {
        "contexto_valido": True,
        "dados": etapa_encontrada,
        "similaridade": best_sim
    }