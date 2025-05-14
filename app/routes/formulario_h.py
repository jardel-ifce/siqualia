from fastapi import APIRouter, Query
from app.services.formulario_h_service import inicializar_formulario_h_em_arquivo

router = APIRouter(prefix="/v1/formulario-h", tags=["Formulário H"])

@router.post("/inicializar")
def inicializar_formulario_h(produto: str = Query(...)):
    inicializar_formulario_h_em_arquivo(produto)
    return {"mensagem": f"Formulários H inicializados para o produto: {produto}"}
