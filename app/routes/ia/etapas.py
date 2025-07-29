# app/routes/ia/etapas.py

# 📦 Bibliotecas externas
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# 📁 Serviços internos
from app.services.ia.consultar_etapas_similares import consultar_etapas_similares
from app.services.ia.consultar_perigos_por_etapa import consultar_perigos_por_etapa

# 🔧 Configuração da rota
router = APIRouter(prefix="/ia", tags=["IA - Sugestões"])

# 📦 Modelo de entrada para busca de etapas semelhantes
class EtapaSimilarRequest(BaseModel):
    produto: str
    etapa: str
    top_n: Optional[int] = 3

# 🔍 Rota para encontrar etapas similares via busca vetorial
@router.post("/etapas/similar")
def encontrar_etapas_semelhantes(req: EtapaSimilarRequest):
    resultados = consultar_etapas_similares(req.produto, req.etapa, req.top_n)
    if not resultados:
        raise HTTPException(status_code=404, detail="Nenhuma etapa semelhante encontrada.")
    return resultados

# 🛡️ Rota para sugerir perigos com base em etapa confirmada
@router.get("/perigos/sugerir")
def sugerir_perigos(produto: str, etapa: str):
    resposta = consultar_perigos_por_etapa(produto, etapa)
    if "erro" in resposta:
        raise HTTPException(status_code=404, detail=resposta["erro"])
    return resposta
