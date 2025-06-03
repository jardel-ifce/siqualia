from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import json

from app.utils.utils import gerar_nome_arquivo_etapa

router = APIRouter(prefix="/crud", tags=["CRUD - Etapas"])

class EtapaModel(BaseModel):
    produto: str
    etapa: str

@router.post("/etapas/salvar")
def salvar_etapa(dados: EtapaModel):
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
    pasta = Path("avaliacoes") / "produtos" / produto
    if not pasta.exists():
        raise HTTPException(status_code=404, detail="Produto não encontrado.")

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
