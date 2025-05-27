from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from pydantic import BaseModel
from typing import List, Dict

from app.services.sugerir_formulario_i import sugerir_formulario_i_dados

router = APIRouter(prefix="/v1/formulario-i", tags=["Formulário I"])

@router.get("/sugerir")
def sugerir_formulario_i(
    produto: str = Query(...),
    etapa: str = Query(...),
    tipo: str = Query(...),
    perigo: str = Query(...),
    medida: str = Query(""),
    justificativa: str = Query("")
):
    sugestao = sugerir_formulario_i_dados(
        produto=produto,
        etapa=etapa,
        tipo=tipo,
        perigo=perigo,
        medida=medida,
        justificativa=justificativa
    )

    return {
        "formulario_i": sugestao or {
            "limite_critico": "",
            "monitoramento": {"oque": "", "como": "", "quando": "", "quem": ""},
            "acao_corretiva": "",
            "registro": "",
            "verificacao": ""
        }
    }

class AtualizarFormularioIRequest(BaseModel):
    produto: str
    etapa: str
    tipo: str
    perigo: str
    formulario_i: Dict

@router.put("/salvar")
def salvar_formulario_i(req: AtualizarFormularioIRequest):
    base = Path("avaliacoes/produtos") / req.produto
    if not base.exists():
        return {"erro": f"Pasta para o produto '{req.produto}' não encontrada."}

    for arquivo in base.glob("*.json"):
        with open(arquivo, "r+", encoding="utf-8") as f:
            dados = json.load(f)
            if dados.get("etapa", "").strip().lower() != req.etapa.strip().lower():
                continue

            g_lista = dados.get("formulario_g", [])
            i_lista = dados.get("formulario_i", [{} for _ in g_lista])

            atualizou = False
            for i, g in enumerate(g_lista):
                if g.get("tipo") == req.tipo and g.get("perigo") == req.perigo:
                    i_lista[i] = req.formulario_i
                    atualizou = True
                    break

            if atualizou:
                dados["formulario_i"] = i_lista
                f.seek(0)
                json.dump(dados, f, ensure_ascii=False, indent=2)
                f.truncate()
                return {"mensagem": "Formulário I salvo com sucesso."}

    return {"erro": "Registro não encontrado para a etapa, tipo e perigo especificados."}

@router.get("/relatorio")
def gerar_relatorio(arquivo: str = Query(...), indice: int = Query(...)):
    caminho = Path(arquivo)
    if not caminho.exists():
        return JSONResponse(status_code=404, content={"erro": "Arquivo não encontrado"})

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    g = dados["formulario_g"][indice]
    i = dados.get("formulario_i", [{}])[indice] or {}

    return {
        "produto": dados.get("produto"),
        "etapa": dados.get("etapa"),
        "tipo": g["tipo"],
        "perigo": g["perigo"],
        "justificativa": g.get("justificativa", ""),
        "medida": g.get("medida", ""),
        "formulario_i": i
    }

