from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db
from app.models.appcc import Produto
from typing import List
# from .schemas import PlanoResumoItem criar os schemas de forma separada depois
from pydantic import BaseModel
from typing import Optional

class PlanoResumoItem(BaseModel):
    etapa: str
    pcc_codigo: str
    tipo_perigo: str
    perigo: str
    medidas: str
    limite_critico: Optional[str] = None
    monitoramento: Optional[str] = None
    acao_corretiva: Optional[str] = None
    registros: Optional[str] = None
    verificacao: Optional[str] = None

router = APIRouter()

@router.get("/plano-resumo/{produto}", response_model=List[PlanoResumoItem])
def gerar_plano_resumo(produto: str, db: Session = Depends(get_db)):
    # Verifica se o produto existe
    prod = db.query(Produto).filter(Produto.nome_produto == produto).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

    # Busca dados dos PCCs confirmados
    query = text("""
                 SELECT
                    e.nome_etapa,
                    tp.codigo_perigo,
                    pe.descricao_perigo,
                    g.medida_preventiva,
                    g.id_formulario_g,
                    h.pcc
                FROM formulario_g g
                JOIN formulario_h h ON h.id_formulario_g = g.id_formulario_g
                JOIN etapas e ON g.id_etapa = e.id_etapa
                JOIN perigos pe ON g.id_perigo = pe.id_perigo
                JOIN tipo_perigo tp ON g.id_tipo_perigo = tp.id_tipo_perigo
                WHERE g.id_produto = :produto_id
                   AND h.pcc = 'É um PCC'
                ORDER BY g.id_formulario_g;
                 """)
    resultados = db.execute(query, {"produto_id": prod.id_produto}).fetchall()

    plano = []
    for idx, row in enumerate(resultados, start=1):
        plano.append(PlanoResumoItem(
            etapa=row[0],
            pcc_codigo=f"PCC {idx} ({row[1]})",
            tipo_perigo=row[1],
            perigo=row[2],
            medidas=row[3],
            limite_critico=None,
            monitoramento=None,
            acao_corretiva=None,
            registros=None,
            verificacao=None
        ))

    return plano
