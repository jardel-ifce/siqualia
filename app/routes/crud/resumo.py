# app/routes/crud/resumo.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict
from fastapi.responses import JSONResponse
from pathlib import Path
import json

from app.utils.utils import atualizar_resumo_do_perigo, substituir_resumo_do_perigo
from app.services.ia.consultar_resumo import sugerir_formulario_i_dados

router = APIRouter(prefix="/crud", tags=["CRUD - Formulário I"])

# MODELO PARA SUGESTÃO (mantido)
class ResumoRequest(BaseModel):
    produto: str
    etapa: str
    id_perigo: int
    tipo: str
    perigo: str
    justificativa: str
    medida: str


@router.post("/resumo/sugerir")
def sugerir_resumo(req: ResumoRequest):
    dados = sugerir_formulario_i_dados(
        req.produto, req.etapa, req.tipo,
        req.perigo, req.medida, req.justificativa
    )
    if not dados:
        raise HTTPException(status_code=404, detail="Não foi possível sugerir os dados do Formulário I.")
    return {"mensagem": "Sugestão gerada com sucesso", "resumo": dados}


# MODELOS ANINHADOS
class Monitoramento(BaseModel):
    oque: str
    como: str
    quando: str
    quem: str


class ResumoBase(BaseModel):
    produto: str
    etapa: str
    id_perigo: int
    resumo: dict


class ResumoExistente(BaseModel):
    produto: str
    etapa: str
    id_perigo: int
    limite_critico: str
    monitoramento: Dict[str, str]
    acao_corretiva: str
    registro: str
    verificacao: str

class SalvarResumoRequest(BaseModel):
    produto: str
    etapa: str
    id_perigo: int
    resumo: dict

@router.post("/resumo/salvar")
def salvar_resumo(req: ResumoBase):
    sucesso = atualizar_resumo_do_perigo(req.produto, req.etapa, req.id_perigo, req.resumo)
    if not sucesso:
        raise HTTPException(status_code=500, detail="Erro ao salvar o resumo informado.")
    return {"mensagem": "Resumo salvo com sucesso."}


@router.put("/resumo/atualizar")
def atualizar_resumo(req: ResumoExistente):
    resumo = {
        "limite_critico": req.limite_critico,
        "monitoramento": req.monitoramento,
        "acao_corretiva": req.acao_corretiva,
        "registro": req.registro,
        "verificacao": req.verificacao,
    }

    sucesso = substituir_resumo_do_perigo(req.produto, req.etapa, req.id_perigo, resumo)
    if not sucesso:
        raise HTTPException(status_code=500, detail="Erro ao atualizar o resumo informado.")
    return {"mensagem": "Resumo atualizado com sucesso."}


@router.get("/relatorio")
def gerar_relatorio(arquivo: str = Query(...), indice: int = Query(...)):
    caminho = Path(arquivo)
    if not caminho.exists():
        return JSONResponse(status_code=404, content={"erro": "Arquivo não encontrado"})

    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    perigos = dados.get("perigos", [])
    perigo = next((p for p in perigos if p.get("id") == indice), None)

    if not perigo:
        return JSONResponse(status_code=404, content={"erro": f"Perigo com id {indice} não encontrado."})

    perigo_detalhe = perigo.get("perigo", [{}])[0]
    resumo = perigo.get("resumo", [{}])[0] or {}

    return {
        "produto": dados.get("produto"),
        "etapa": dados.get("etapa"),
        "tipo": perigo_detalhe.get("tipo", ""),
        "perigo": perigo_detalhe.get("perigo", ""),
        "justificativa": perigo_detalhe.get("justificativa", ""),
        "medida": perigo_detalhe.get("medida", ""),
        "formulario_i": resumo
    }

