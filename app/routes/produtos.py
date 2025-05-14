from fastapi import APIRouter
from pathlib import Path

router = APIRouter(prefix="/v1", tags=["Produtos"])

@router.get("/produtos")
def listar_produtos():
    produtos_dir = Path("produtos")
    produtos = [p.name for p in produtos_dir.iterdir() if p.is_dir()]
    return produtos
