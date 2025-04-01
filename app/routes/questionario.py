from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.utils.dados import carregar_documentos, buscar_etapa_por_nome

router = APIRouter(prefix="/etapa", tags=["Etapas"])
documents = carregar_documentos()

class EtapaQuestionarioRequest(BaseModel):
    etapa: str

@router.post("/questionario")
def iniciar_questionario(request: EtapaQuestionarioRequest):
    etapa_match = buscar_etapa_por_nome(request.etapa, documents)

    if not etapa_match:
        raise HTTPException(status_code=404, detail="Etapa não encontrada na base de dados.")

    perguntas = {
        "Q1": "Existem medidas preventivas para o controle dos perigos?",
        "Q1a": "O controle desta fase é necessário à segurança do produto?",
        "Q2": "Esta fase foi especialmente desenvolvida para eliminar ou reduzir o perigo?",
        "Q3": "O perigo poderia ocorrer em níveis inaceitáveis ou aumentar para níveis inaceitáveis?",
        "Q4": "Existe uma etapa posterior que poderia eliminar ou reduzir o perigo a níveis aceitáveis?"
    }

    return {
        "etapa": etapa_match["etapa"],
        "perguntas": perguntas
    }
