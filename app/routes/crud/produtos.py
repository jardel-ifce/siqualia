# 📁 app/routes/crud/produtos.py

# 📦 Importações padrão
from pathlib import Path
from fastapi import APIRouter

# 🔧 Configuração do roteador
router = APIRouter(prefix="/crud", tags=["CRUD - Produtos"])

# 📌 Endpoints

@router.get("/produtos")
def listar_produtos():
    """
    Lista os produtos disponíveis com base nas pastas dentro do diretório 'produtos'.
    """
    produtos_dir = Path("produtos")
    if not produtos_dir.exists():
        return []
    produtos = [p.name for p in produtos_dir.iterdir() if p.is_dir()]
    return produtos
