# app/routes/crud/produtos.py

from fastapi import APIRouter
from pathlib import Path

router = APIRouter(prefix="/crud", tags=["CRUD - Produtos"])

@router.get("/produtos")
def listar_produtos():
    produtos_dir = Path("produtos")
    if not produtos_dir.exists():
        return []
    produtos = [p.name for p in produtos_dir.iterdir() if p.is_dir()]
    return produtos
