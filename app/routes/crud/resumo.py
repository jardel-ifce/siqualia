# 📁 app/routes/crud/resumo.py

# 📦 Importações padrão
from pathlib import Path
import json
from typing import Dict
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# 📁 Serviços internos
from app.utils.utils import atualizar_resumo_do_perigo, substituir_resumo_do_perigo


# 🔧 Configuração do roteador
router = APIRouter(prefix="/crud/resumo", tags=["CRUD - Resumo"])


# 📦 Modelos de Dados
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


# 📌 Endpoints

@router.post("/salvar")
def salvar_resumo(req: ResumoBase):
    """
    Salva um novo conjunto de dados do Formulário I (resumo) para o perigo informado.
    """
    sucesso = atualizar_resumo_do_perigo(req.produto, req.etapa, req.id_perigo, req.resumo)
    if not sucesso:
        raise HTTPException(status_code=500, detail="Erro ao salvar o resumo informado.")
    return {"mensagem": "Resumo salvo com sucesso."}


@router.put("/atualizar")
def atualizar_resumo(req: ResumoExistente):
    """
    Atualiza os dados do resumo (Formulário I) para um perigo já existente.
    """
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
    """
    Gera o relatório do Formulário I com base no arquivo salvo e ID do perigo.
    """
    base_dir = Path("avaliacoes")

    try:
        caminho = base_dir / Path(arquivo).relative_to("avaliacoes")
    except Exception:
        return JSONResponse(status_code=400, content={"erro": "Caminho de arquivo inválido."})

    if not caminho.exists():
        return JSONResponse(status_code=404, content={"erro": f"Arquivo não encontrado: {arquivo}"})

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": f"Erro ao ler o arquivo: {str(e)}"})

    perigos = dados.get("perigos", [])
    perigo = next((p for p in perigos if str(p.get("id")) == str(indice)), None)

    if not perigo:
        ids_disponiveis = [p.get("id") for p in perigos]
        return JSONResponse(
            status_code=404,
            content={"erro": f"Perigo com id {indice} não encontrado.", "ids_disponiveis": ids_disponiveis}
        )

    perigo_detalhe = perigo.get("perigo", [{}])[0] if perigo.get("perigo") else {}
    resumo = perigo.get("resumo", [{}])[0] if perigo.get("resumo") else {}

    return {
        "produto": dados.get("produto"),
        "etapa": dados.get("etapa"),
        "tipo": perigo_detalhe.get("tipo", ""),
        "perigo": perigo_detalhe.get("perigo", ""),
        "justificativa": perigo_detalhe.get("justificativa", ""),
        "medida": perigo_detalhe.get("medida", ""),
        "formulario_i": resumo
    }
