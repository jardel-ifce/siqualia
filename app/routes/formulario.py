from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.appcc import FormularioG
from app.services.formulario import verificar_ou_criar_ids

router = APIRouter()

class FormularioGEntrada(BaseModel):
    produto: str
    etapa: str
    tipo_perigo: str
    perigo: str
    justificativa: str
    medida_preventiva: str

class FormularioGCompleto(BaseModel):
    produto: str
    etapa: str
    tipo_perigo: str
    perigo: str
    justificativa: str
    probabilidade: str
    severidade: str
    risco: str
    medida_preventiva: str
    perigo_significativo: str

@router.post("/formulario/checar-ids")
def checar_ids(payload: FormularioGEntrada, db: Session = Depends(get_db)):
    try:
        return verificar_ou_criar_ids(
            db,
            produto_nome=payload.produto,
            etapa_nome=payload.etapa,
            tipo_perigo_nome=payload.tipo_perigo,
            perigo_nome=payload.perigo,
            justificativa_texto=payload.justificativa,
            medida_texto=payload.medida_preventiva
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/formulario-g")
def salvar_formulario_g(payload: FormularioGCompleto, db: Session = Depends(get_db)):
    try:
        ids = verificar_ou_criar_ids(
            db,
            produto_nome=payload.produto,
            etapa_nome=payload.etapa,
            tipo_perigo_nome=payload.tipo_perigo,
            perigo_nome=payload.perigo,
            justificativa_texto=payload.justificativa,
            medida_texto=payload.medida_preventiva
        )

        # Verifica se já existe formulário G igual
        existe = db.query(FormularioG).filter_by(
            id_produto=ids["produto"]["id"],
            id_etapa=ids["etapa"]["id"],
            id_perigo=ids["perigo"]["id"],
            id_tipo_perigo=ids["tipo_perigo"]["id"],
            justificativa=payload.justificativa,
            probabilidade=payload.probabilidade,
            severidade=payload.severidade,
            risco=payload.risco,
            medida_preventiva=payload.medida_preventiva,
            perigo_significativo=payload.perigo_significativo
        ).first()

        if existe:
            return {"message": "Formulário já cadastrado.", "id": existe.id_formulario_g}

        novo = FormularioG(
            id_produto=ids["produto"]["id"],
            id_etapa=ids["etapa"]["id"],
            id_perigo=ids["perigo"]["id"],
            id_tipo_perigo=ids["tipo_perigo"]["id"],
            justificativa=payload.justificativa,
            probabilidade=payload.probabilidade,
            severidade=payload.severidade,
            risco=payload.risco,
            medida_preventiva=payload.medida_preventiva,
            perigo_significativo=payload.perigo_significativo
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)

        return {"message": "Formulário salvo com sucesso.", "id": novo.id_formulario_g}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))