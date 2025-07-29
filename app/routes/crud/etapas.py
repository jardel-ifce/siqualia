# 📁 app/routes/crud/etapas.py

# 📦 Importações padrão
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 📁 Serviços internos
from app.utils.utils import gerar_nome_arquivo_etapa

# 🔧 Configuração do roteador
router = APIRouter(prefix="/crud", tags=["CRUD - Etapas"])

# 📦 Modelos de Dados
class EtapaModel(BaseModel):
    produto: str
    etapa: str

# 📌 Endpoints

@router.post("/etapas/salvar")
def salvar_etapa(dados: EtapaModel):
    """
    Cria e salva um novo arquivo de etapa vazia (sem perigos).
    """
    path = gerar_nome_arquivo_etapa(dados.produto, dados.etapa)
    path.parent.mkdir(parents=True, exist_ok=True)

    conteudo = {
        "produto": dados.produto,
        "etapa": dados.etapa,
        "perigos": []
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(conteudo, f, ensure_ascii=False, indent=2)

    return {"mensagem": "Etapa salva com sucesso", "arquivo": str(path)}


@router.get("/etapas")
def listar_etapas(produto: str):
    """
    Retorna a lista de etapas cadastradas para um produto.
    """
    pasta = Path("avaliacoes") / "produtos" / produto
    if not pasta.exists():
        return []

    etapas = set()
    for arquivo in pasta.glob("*.json"):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                conteudo = json.load(f)
                etapa = conteudo.get("etapa")
                if etapa:
                    etapas.add(etapa)
        except Exception:
            continue

    return sorted(etapas)
