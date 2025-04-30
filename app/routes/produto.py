from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.db.database import get_db
from app.models.appcc import Produto, Etapa, Perigo, TipoPerigo, Justificativa, MedidaControle
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# ----------------------
# Schemas Pydantic
# ----------------------
class PerigoOut(BaseModel):
    nome_etapa: str
    tipo_perigo: Optional[str]
    descricao_perigo: str
    justificativa: Optional[str]
    medida_controle: Optional[str]

class EtapaOut(BaseModel):
    id_etapa: int
    nome_etapa: str
    descricao_etapa: Optional[str]

class ProdutoContextoOut(BaseModel):
    id_produto: int
    nome_produto: str
    descricao_produto: Optional[str]
    etapas: List[EtapaOut]
    perigos: List[PerigoOut]

# ----------------------
# Endpoint: Listar Produtos
# ----------------------
@router.get("/produtos")
def listar_produtos(db: Session = Depends(get_db)):
    produtos = db.query(Produto).all()
    return [
        {"id_produto": p.id_produto, "nome_produto": p.nome_produto}
        for p in produtos
    ]

# ----------------------
# Endpoint: Contexto Completo de Produto
# ----------------------
@router.get("/contexto/{id_produto}", response_model=ProdutoContextoOut)
def contexto_produto(id_produto: int, db: Session = Depends(get_db)):
    # Carregar produto com etapas e perigos de forma eficiente
    produto = (
        db.query(Produto)
        .options(
            selectinload(Produto.etapas)
            .selectinload(Etapa.perigos)
            .selectinload(Perigo.tipo_perigo),

            selectinload(Produto.etapas)
            .selectinload(Etapa.perigos)
            .selectinload(Perigo.justificativas),

            selectinload(Produto.etapas)
            .selectinload(Etapa.perigos)
            .selectinload(Perigo.medidas_controle)
        )
        .filter(Produto.id_produto == id_produto)
        .first()
    )

    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    etapas_data = [
        EtapaOut(
            id_etapa=etapa.id_etapa,
            nome_etapa=etapa.nome_etapa,
            descricao_etapa=etapa.descricao_etapa,
        ) for etapa in produto.etapas
    ]

    perigos_data = []
    for etapa in produto.etapas:
        for perigo in etapa.perigos:
            perigos_data.append(
                PerigoOut(
                    nome_etapa=etapa.nome_etapa,
                    tipo_perigo=perigo.tipo_perigo.nome_tipo_perigo if perigo.tipo_perigo else None,
                    descricao_perigo=perigo.descricao_perigo,
                    justificativa=perigo.justificativas[0].texto_justificativa if perigo.justificativas else None,
                    medida_controle=perigo.medidas_controle[0].texto_medida if perigo.medidas_controle else None,
                )
            )

    return ProdutoContextoOut(
        id_produto=produto.id_produto,
        nome_produto=produto.nome_produto,
        descricao_produto=produto.descricao_produto,
        etapas=etapas_data,
        perigos=perigos_data
    )
