from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.appcc import PerguntaFormularioH, OpcaoPerguntaH, FormularioH
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class OpcaoOut(BaseModel):
    texto_opcao: str
    proxima_codigo: Optional[str]
    resultado_final: Optional[str]

class PerguntaOut(BaseModel):
    codigo: str
    texto_pergunta: str
    tipo: str
    opcoes: List[OpcaoOut]

class FormularioHCompleto(BaseModel):
    id_formulario_g: int
    controlado_por_prerequisito: Optional[str] = None
    q1_medidas_preventivas: Optional[str] = None
    q2_reducao_perigo: Optional[str] = None
    q3_aumento_perigo: Optional[str] = None
    q4_eliminacao_posterior: Optional[str] = None
    pcc: str

@router.get("/formulario-h/questionario/{codigo}", response_model=PerguntaOut)
def carregar_pergunta(codigo: str, db: Session = Depends(get_db)):
    pergunta = db.query(PerguntaFormularioH).filter_by(codigo=codigo).first()
    if not pergunta:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")

    return PerguntaOut(
        codigo=pergunta.codigo,
        texto_pergunta=pergunta.texto_pergunta,
        tipo=pergunta.tipo,
        opcoes=[
            OpcaoOut(
                texto_opcao=op.texto_opcao,
                proxima_codigo=op.proxima_codigo,
                resultado_final=op.resultado_final
            ) for op in pergunta.opcoes
        ]
    )

class FormularioHResposta(BaseModel):
    id_formulario_g: int
    resultado: str  # Ex: "É um PCC", "Não é um PCC", "Modificar o Processo"

@router.post("/formulario-h/responder")
def salvar_resposta_h(payload: FormularioHCompleto, db: Session = Depends(get_db)):
    existente = db.query(FormularioH).filter_by(id_formulario_g=payload.id_formulario_g).first()
    if existente:
        for campo, valor in payload.dict().items():
            setattr(existente, campo, valor)
        db.commit()
        return {"message": "Resposta atualizada com sucesso."}

    novo = FormularioH(**payload.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"message": "Resposta salva com sucesso.", "id": novo.id_formulario_h}
