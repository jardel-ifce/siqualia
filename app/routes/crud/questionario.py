# routes/crud/questionario.py
from pathlib import Path
import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/crud/questionario", tags=["Formulário H"])

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

@router.post("/avaliar")
def avaliar_questionario_fluxo(respostas: QuestionarioForm):
    q1 = respostas.questao_1
    q1a = respostas.questao_1a
    q2 = respostas.questao_2
    q3 = respostas.questao_3
    q4 = respostas.questao_4

    if q1 == "Não":
        if q1a == "Sim":
            return {"resultado": "Modificar o processo"}
        elif q1a == "Não":
            return {"resultado": "Não é um PCC"}
        else:
            return {"proxima": "questao_1a"}

    if q1 == "Sim":
        if q2 == "Sim":
            return {"resultado": "É um PCC"}
        elif q2 == "Não":
            if q3 == "Não":
                return {"resultado": "Não é um PCC"}
            elif q3 == "Sim":
                if q4 == "Sim":
                    return {"resultado": "Não é um PCC"}
                elif q4 == "Não":
                    return {"resultado": "É um PCC"}
                else:
                    return {"proxima": "questao_4"}
            else:
                return {"proxima": "questao_3"}
        else:
            return {"proxima": "questao_2"}

    return {"proxima": "questao_1"}


@router.post("/salvar")
def salvar_questionario(dados: QuestionarioForm):
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

    questionario_item = {
        "questao_1": dados.questao_1,
        "questao_1a": dados.questao_1a,
        "questao_2": dados.questao_2,
        "questao_3": dados.questao_3,
        "questao_4": dados.questao_4,
        "resultado": dados.resultado,
    }

    # perigo["questionario"].append(questionario_item)
    perigo["questionario"] = [questionario_item]

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(etapa_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar o arquivo: {e}")

    return {"mensagem": "Questionário salvo com sucesso."}
