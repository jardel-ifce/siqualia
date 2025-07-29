# 📁 app/routes/crud/questionario.py

# 📦 Importações padrão
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# 🔧 Configuração do roteador
router = APIRouter(prefix="/crud/questionario", tags=["Formulário H"])

# 📦 Modelo de Dados
class QuestionarioForm(BaseModel):
    produto: str
    etapa: str
    id: int
    arquivo: str
    questao_1: str
    questao_1a: Optional[str] = ""
    questao_2: Optional[str] = ""
    questao_3: Optional[str] = ""
    questao_4: Optional[str] = ""
    resultado: str

# 📌 Endpoints

@router.post("/avaliar")
def avaliar_questionario_fluxo(respostas: QuestionarioForm):
    """
    Lógica de decisão para avaliar se o perigo analisado é um PCC,
    com base nas respostas do Formulário H (árvore de decisão).
    """
    q1, q1a, q2, q3, q4 = respostas.questao_1, respostas.questao_1a, respostas.questao_2, respostas.questao_3, respostas.questao_4

    if q1 == "Não":
        return {"resultado": "Modificar o processo"} if q1a == "Sim" else {"resultado": "Não é um PCC"} if q1a == "Não" else {"proxima": "questao_1a"}
    if q1 == "Sim":
        if q2 == "Sim":
            return {"resultado": "É um PCC"}
        if q2 == "Não":
            if q3 == "Não":
                return {"resultado": "Não é um PCC"}
            if q3 == "Sim":
                return {"resultado": "Não é um PCC"} if q4 == "Sim" else {"resultado": "É um PCC"} if q4 == "Não" else {"proxima": "questao_4"}
            return {"proxima": "questao_3"}
        return {"proxima": "questao_2"}
    return {"proxima": "questao_1"}


@router.post("/salvar")
def salvar_questionario(dados: QuestionarioForm):
    """
    Salva as respostas do Formulário H (questionário de PCC) no JSON da etapa correspondente.
    """
    path = Path(dados.arquivo)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo de etapa não encontrado.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            etapa_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler o arquivo: {e}")

    perigos = etapa_data.get("perigos", [])
    perigo = next((p for p in perigos if p.get("id") == dados.id), None)
    if not perigo:
        raise HTTPException(status_code=404, detail=f"Perigo com ID {dados.id} não encontrado.")

    # Substitui o conteúdo atual do campo 'questionario' pelo novo
    perigo["questionario"] = [{
        "questao_1": dados.questao_1,
        "questao_1a": dados.questao_1a,
        "questao_2": dados.questao_2,
        "questao_3": dados.questao_3,
        "questao_4": dados.questao_4,
        "resultado": dados.resultado,
    }]

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(etapa_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar o arquivo: {e}")

    return {"mensagem": "Questionário salvo com sucesso."}
