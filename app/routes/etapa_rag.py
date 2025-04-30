from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import os
import faiss
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer

router = APIRouter()
model = SentenceTransformer("all-MiniLM-L6-v2")
INDEX_DIR = "indexes"

# ----------- Schemas ----------
class EtapaVerificarRequest(BaseModel):
    produto: str
    etapa: str

class EtapaVerificarResponse(BaseModel):
    etapa_sugerida: str

class EtapaPerigoRequest(BaseModel):
    produto: str
    etapa: str

class PerigoOut(BaseModel):
    tipo: str
    perigo: str
    justificativa: str
    probabilidade: str
    severidade: str
    risco: str
    medida_preventiva: str
    perigo_significativo: str

class EtapaPerigoResponse(BaseModel):
    perigos: List[PerigoOut]

# ----------- Funções utilitárias ----------
def carregar_index(produto: str):
    produto = produto.lower()
    index_path = f"{INDEX_DIR}/{produto}/appcc.index"
    meta_path = f"{INDEX_DIR}/{produto}/appcc.pkl"

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise HTTPException(status_code=404, detail="Produto não vetorizado ou ausente.")

    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        metadados = pickle.load(f)

    return index, metadados

# ----------- Endpoint: verificar etapa ----------
@router.post("/etapa-rag-verificar", response_model=EtapaVerificarResponse)
def verificar_etapa(payload: EtapaVerificarRequest):
    index, metadados = carregar_index(payload.produto)
    consulta = model.encode([payload.etapa.strip().lower()])
    D, I = index.search(consulta, k=1)

    if I[0][0] == -1:
        raise HTTPException(status_code=404, detail="Etapa não encontrada no índice.")

    etapa_sugerida = metadados[I[0][0]].get("etapa", "")
    return {"etapa_sugerida": etapa_sugerida}

# ----------- Endpoint: retornar perigos ----------
@router.post("/etapa-rag-perigos", response_model=EtapaPerigoResponse)
def consultar_perigos(payload: EtapaPerigoRequest):
    index, metadados = carregar_index(payload.produto)

    # Vetorizar e localizar a etapa mais próxima
    consulta = model.encode([payload.etapa.strip().lower()])
    D, I = index.search(consulta, k=1)

    if I[0][0] == -1:
        raise HTTPException(status_code=404, detail="Etapa não encontrada no índice.")

    etapa_sugerida = metadados[I[0][0]].get("etapa", "").strip().lower()

    # Filtrar todos os perigos com mesma etapa (case-insensitive)
    perigos_filtrados = []

    def limpar(val, padrao=""):
        return str(val).strip() if pd.notna(val) else padrao

    for m in metadados:
        if m.get("etapa", "").strip().lower() == etapa_sugerida:
            perigos_filtrados.append({
                "tipo": limpar(m.get("tipo"), "Outro"),
                "perigo": limpar(m.get("perigo"), "Desconhecido"),
                "justificativa": limpar(m.get("justificativa")),
                "probabilidade": limpar(m.get("probabilidade")),
                "severidade": limpar(m.get("severidade")),
                "risco": limpar(m.get("risco")),
                "medida_preventiva": limpar(m.get("medida")),
                "perigo_significativo": limpar(m.get("perigo_significativo"), "Não")
            })

    return {"perigos": perigos_filtrados}

