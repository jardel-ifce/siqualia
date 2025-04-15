from fastapi import APIRouter
from pathlib import Path

router = APIRouter()

# Caminho relativo de /app/routes para /app/data
DATA_DIR = Path(__file__).parent.parent / "data"

@router.get("/produtos")
def listar_produtos():
    arquivos = list(DATA_DIR.glob("*.json"))
    nomes = [arquivo.stem for arquivo in arquivos]
    print("Arquivos encontrados:", nomes)
    return nomes
