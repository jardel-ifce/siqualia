from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

router = APIRouter()

MODEL_NAME = "intfloat/e5-base-v2"
model = SentenceTransformer(MODEL_NAME)

class FormularioIRequest(BaseModel):
    etapa: str
    perigo: str
    medida: str

@router.post("/v1/{produto}/formulario-i/sugerir")
def sugerir_formulario_i(produto: str, request: FormularioIRequest):
    index_path = Path(f"../indexes/{produto}/pac.index")
    store_path = Path(f"../indexes/{produto}/pac.pkl")

    if not index_path.exists() or not store_path.exists():
        raise HTTPException(status_code=404, detail="Base vetorizada não encontrada para este produto.")

    # Carregar índice e store
    index = faiss.read_index(str(index_path))
    with open(store_path, "rb") as f:
        store = pickle.load(f)

    # Construir prompt de busca
    prompt = f"Etapa: {request.etapa}. Perigo: {request.perigo}. Medida de controle: {request.medida}."
    embedding = model.encode(prompt)

    # Buscar top 1 similar
    scores, indices = index.search(np.array([embedding]), k=1)
    resultado = store[indices[0][0]]

    # Validar se os campos essenciais existem
    campos_esperados = ["limite_critico", "monitoramento", "acao_corretiva", "registro", "verificacao"]
    if not all(campo in resultado for campo in campos_esperados):
        raise HTTPException(status_code=422, detail="Bloco retornado não possui todos os campos esperados para o formulário I.")

    return {"formulario_i": [
        {
            "limite_critico": resultado["limite_critico"],
            "monitoramento": resultado["monitoramento"],
            "acao_corretiva": resultado["acao_corretiva"],
            "registro": resultado["registro"],
            "verificacao": resultado["verificacao"],
            "fonte": resultado.get("fonte", "Desconhecida")
        }
    ]}
