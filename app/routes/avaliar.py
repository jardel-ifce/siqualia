from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

from app.utils.dados import carregar_documentos, buscar_etapa_por_nome

router = APIRouter(prefix="/etapa", tags=["Etapas"])

documents = carregar_documentos()

class AvaliarRequest(BaseModel):
    etapa: str
    respostas: Dict[str, Dict[str, str]]

@router.post("/avaliar")
def avaliar_pcc(request: AvaliarRequest):
    etapa_match = buscar_etapa_por_nome(request.etapa, documents)

    if not etapa_match:
        raise HTTPException(status_code=404, detail="Etapa não encontrada na base de dados.")

    etapa = etapa_match["etapa"]
    perigos = etapa_match["perigo"]
    medidas = etapa_match["medida_controle"]

    resultado_tabela = []

    for tipo in ["biologico", "quimico", "fisico"]:
        tipo_letra = {"biologico": "B", "quimico": "Q", "fisico": "F"}[tipo]
        desc_perigo = perigos[tipo]
        medida = medidas[tipo]

        if tipo_letra not in request.respostas:
            continue

        r = request.respostas[tipo_letra]
        q1 = r.get("Q1", "-")
        q1a = r.get("Q1a", "-")
        q2 = r.get("Q2", "-")
        q3 = r.get("Q3", "-")
        q4 = r.get("Q4", "-")

        # Árvore de decisão
        if q1 == "Não":
            pcc = "Modificar processo" if q1a == "Sim" else "Não"
        elif q1 == "Sim":
            if q2 == "Sim":
                pcc = "1"
            elif q2 == "Não":
                if q3 == "Sim":
                    pcc = "Não" if q4 == "Sim" else "2" if q4 == "Não" else "-"
                elif q3 == "Não":
                    pcc = "Não"
                else:
                    pcc = "-"
            else:
                pcc = "-"
        else:
            pcc = "-"

        resultado_tabela.append({
            "etapa": etapa,
            "perigo": tipo_letra,
            "descricao_perigo": desc_perigo,
            "Q1": q1,
            "Q2": q2,
            "Q3": q3,
            "Q4": q4,
            "PCC": pcc,
            "medida_controle": medida
        })

    return {
        "etapa": etapa,
        "tabela": resultado_tabela
    }
