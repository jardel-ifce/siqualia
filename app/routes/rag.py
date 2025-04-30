from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal
import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer

router = APIRouter()
model = SentenceTransformer("all-MiniLM-L6-v2")

INDEXES_DIR = "indexes"

class ConsultaEtapaRequest(BaseModel):
    produto: str
    etapa: str

class FormularioGResponse(BaseModel):
    justificativa: str
    probabilidade: str
    severidade: str
    risco: str
    medida_preventiva: str
    perigo_significativo: Literal["Sim", "Não"]

@router.post("/contexto-etapa-rag", response_model=FormularioGResponse)
def contexto_etapa_rag(payload: ConsultaEtapaRequest):
    produto = payload.produto.lower()
    etapa = payload.etapa.strip().lower()

    index_path = f"{INDEXES_DIR}/{produto}/appcc.index"
    meta_path = f"{INDEXES_DIR}/{produto}/appcc.pkl"

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="Produto não vetorizado ou inexistente")

    # Carrega índice e metadados
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        metadados = pickle.load(f)

    # Codifica a etapa
    consulta = model.encode([etapa])
    D, I = index.search(consulta, k=1)

    if I[0][0] == -1:
        raise HTTPException(status_code=404, detail="Etapa não encontrada no índice")

    resultado = metadados[I[0][0]]

    return {
        "justificativa": resultado.get("justificativa", ""),
        "probabilidade": resultado.get("probabilidade", ""),
        "severidade": resultado.get("severidade", ""),
        "risco": resultado.get("risco", ""),
        "medida_preventiva": resultado.get("medida", ""),
        "perigo_significativo": resultado.get("perigo_significativo", "Não")
    }
