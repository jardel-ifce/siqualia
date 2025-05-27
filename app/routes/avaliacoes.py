from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
from pathlib import Path
import uuid
import unicodedata
import re
import json

router = APIRouter(prefix="/v1/avaliacoes", tags=["Avaliações"])


def normalizar_etapa(etapa: str) -> str:
    etapa = etapa.lower()
    etapa = unicodedata.normalize("NFKD", etapa).encode("ascii", "ignore").decode("utf-8")
    etapa = re.sub(r"\\", "", etapa)  # remove barras invertidas se houver
    etapa = re.sub(r"[\s/]+", "_", etapa)  # substitui espaços e barras por _
    etapa = re.sub(r"[^a-z0-9_]+", "", etapa)  # remove outros caracteres especiais
    return etapa


# Modelo da requisição
class AvaliacaoRequest(BaseModel):
    produto: str
    etapa: str
    formulario_g: List[Dict]
    formulario_h: Optional[List[Dict]] = None  # opcional
    formulario_i: Optional[List[Dict]] = None  # opcional


@router.post("/salvar")
@router.post("/salvar")
def salvar_avaliacoes(dados: AvaliacaoRequest):
    base_dir = Path("avaliacoes/produtos") / dados.produto
    base_dir.mkdir(parents=True, exist_ok=True)

    etapa_formatada = normalizar_etapa(dados.etapa)

    # Garantir estrutura de formulário I vazia para cada G
    formulario_i_completo = dados.formulario_i or [{} for _ in dados.formulario_g]

    def estrutura_formulario_i(dados=None):
        return {
            "limite_critico": dados.get("limite_critico", "") if dados else "",
            "monitoramento": {
                "oque": dados.get("monitoramento", {}).get("oque", "") if dados else "",
                "como": dados.get("monitoramento", {}).get("como", "") if dados else "",
                "quando": dados.get("monitoramento", {}).get("quando", "") if dados else "",
                "quem": dados.get("monitoramento", {}).get("quem", "") if dados else ""
            },
            "acao_corretiva": dados.get("acao_corretiva", "") if dados else "",
            "registro": dados.get("registro", "") if dados else "",
            "verificacao": dados.get("verificacao", "") if dados else ""
        }

    for i, (g, h, i_data) in enumerate(zip(
        dados.formulario_g,
        dados.formulario_h or [{} for _ in dados.formulario_g],
        formulario_i_completo
    )):
        id_arquivo = uuid.uuid4().hex[:8]
        nome_arquivo = f"{etapa_formatada}_{id_arquivo}.json"
        caminho = base_dir / nome_arquivo

        registro = {
            "produto": dados.produto,
            "etapa": dados.etapa,
            "formulario_g": [g],
            "formulario_h": [h],
            "formulario_i": [estrutura_formulario_i(i_data)],
        }

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(registro, f, ensure_ascii=False, indent=2)

    return {
        "mensagem": f"{len(dados.formulario_g)} registros salvos com sucesso para o produto '{dados.produto}'"
    }


@router.get("/etapas")
def listar_etapas_salvas(produto: str = Query(...)):
    pasta = Path("avaliacoes/produtos") / produto
    arquivos = list(pasta.glob("*.json"))

    etapas = []

    for arquivo in arquivos:
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)

            formulario_g = dados.get("formulario_g", [])
            formulario_h = dados.get("formulario_h", [])
            formulario_i = dados.get("formulario_i", [])
            perigos_resumo = []

            for i, item in enumerate(formulario_g):
                tipo = item.get("tipo", "").strip()
                perigo = item.get("perigo", "").strip()
                significativo = str(item.get("perigo_significativo", "")).strip().lower() == "sim"
                resultado = formulario_h[i].get("resultado") if i < len(formulario_h) else None

                perigos_resumo.append({
                    "descricao": f"({tipo}) {perigo}",
                    "significativo": significativo,
                    "resultado": resultado
                })

            etapas.append({
                "produto": dados.get("produto"),
                "etapa": dados.get("etapa"),
                "arquivo": str(arquivo),
                "formulario_g": formulario_g,
                "formulario_h": formulario_h,
                "resumo": perigos_resumo
            })

        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")
            continue

    return etapas
