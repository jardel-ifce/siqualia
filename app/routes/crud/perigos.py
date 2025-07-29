# 📁 app/routes/crud/perigos.py

# 📦 Importações padrão
import json
from pathlib import Path
from typing import Literal, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 📁 Serviços internos
from app.utils.utils import proximo_id_perigo

# 🔧 Configuração do roteador
router = APIRouter(prefix="/crud", tags=["CRUD - Perigos"])

# 📦 Modelos de Dados
class PerigoForm(BaseModel):
    produto: str
    etapa: str
    arquivo: str
    tipo: str
    perigo: str
    justificativa: str
    probabilidade: Literal["Desprezível", "Baixa", "Média", "Alta"]
    severidade: Literal["Baixa", "Média", "Alta"]
    risco: Literal["Desprezível", "Baixa", "Média", "Alta"]
    medida: str
    perigo_significativo: Optional[str] = ""
    origem: str

class PerigoNovo(PerigoForm):
    pass

class PerigoExistente(PerigoForm):
    id: int

# 📌 Endpoints

@router.post("/perigos/salvar")
def salvar_perigo(perigo_data: PerigoNovo):
    """
    Salva um novo perigo associado a uma etapa.
    """
    path = Path(perigo_data.arquivo)

    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Arquivo de etapa não encontrado: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except json.JSONDecodeError:
        dados = {"perigos": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo: {str(e)}")

    perigos_lista = dados.setdefault("perigos", [])

    novo_perigo_obj_detalhes = {
        "tipo": perigo_data.tipo,
        "perigo": perigo_data.perigo,
        "justificativa": perigo_data.justificativa,
        "probabilidade": perigo_data.probabilidade,
        "severidade": perigo_data.severidade,
        "risco": perigo_data.risco,
        "medida": perigo_data.medida,
        "perigo_significativo": perigo_data.perigo_significativo,
        "origem": perigo_data.origem
    }

    novo_id = proximo_id_perigo(perigos_lista)

    perigos_lista.append({
        "id": novo_id,
        "perigo": [novo_perigo_obj_detalhes],
        "questionario": [],
        "resumo": []
    })

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar o arquivo: {str(e)}")

    return {"mensagem": "Perigo salvo com sucesso.", "id": novo_id, "arquivo": str(path)}


@router.put("/perigos/atualizar")
def atualizar_perigo(perigo: PerigoExistente):
    """
    Atualiza os dados de um perigo existente.
    """
    path = Path(perigo.arquivo)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler arquivo: {e}")

    perigos_lista = dados.get("perigos", [])
    atualizado = False

    for p in perigos_lista:
        if p.get("id") == perigo.id:
            p["perigo"] = [{
                "tipo": perigo.tipo,
                "perigo": perigo.perigo,
                "justificativa": perigo.justificativa,
                "probabilidade": perigo.probabilidade,
                "severidade": perigo.severidade,
                "risco": perigo.risco,
                "medida": perigo.medida,
                "perigo_significativo": perigo.perigo_significativo,
                "origem": perigo.origem
            }]
            atualizado = True
            break

    if not atualizado:
        raise HTTPException(status_code=404, detail="Perigo não encontrado.")

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar arquivo: {e}")

    return {"mensagem": "Perigo atualizado com sucesso.", "id": perigo.id}
