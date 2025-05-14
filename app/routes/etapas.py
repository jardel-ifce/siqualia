from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict

class FormularioGRequest(BaseModel):
    produto: str
    etapa: str
    formulario_g: List[Dict]

from app.services.consultar_etapas_similares import consultar_etapas_similares
from app.services.consultar_perigos_por_etapa import consultar_perigos_por_etapa

router = APIRouter(prefix="/v1", tags=["Etapas"])

# ----------------------
# MODELOS DE REQUISIÇÃO
# ----------------------

class EtapaSimilarRequest(BaseModel):
    produto: str
    etapa: str
    top_n: Optional[int] = 3

# ----------------------
# ENDPOINTS
# ----------------------

@router.post("/etapas/similar")
def encontrar_etapas_semelhantes(req: EtapaSimilarRequest):
    resultados = consultar_etapas_similares(req.produto, req.etapa, req.top_n)
    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhuma etapa semelhante encontrada.")
    return resultados


@router.get("/etapas/perigos")
def obter_perigos_da_etapa(produto: str, etapa: str):
    resposta = consultar_perigos_por_etapa(produto, etapa)
    if "erro" in resposta:
        raise HTTPException(status_code=404, detail=resposta["erro"])
    return resposta


@router.get("/avaliacao")
def formulario_g_automatico(produto: str = Query(...), etapa: str = Query(...)):
    resposta = consultar_perigos_por_etapa(produto, etapa)
    if "erro" in resposta:
        raise HTTPException(status_code=404, detail=resposta["erro"])
    return {
        "produto": produto,
        "etapa": etapa,
        "formulario_g": resposta["formulario_g"]
    }
