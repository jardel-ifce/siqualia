# 📁 app/routes/crud/uploads.py

from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import json
import shutil
import os

# Reuso da slugificação do projeto
from app.utils.utils import slugify

router = APIRouter(prefix="/crud/uploads", tags=["CRUD - Uploads"])

# Tipos aceitos (expansível)
ALLOWED_TYPES = [
    "appcc", "pac", "bpf", "resumo", "formulario_i",        # já usados no projeto / vetorização
    "manual", "procedimento", "relatorio",   # exemplos extras
]

# aliases -> mapeia para o slug canônico do tipo
TIPO_ALIASES = {
    "formulario i": "formulario_i",
    "formulario-i": "formulario_i",
    "form_i": "formulario_i",
    "resumo": "formulario_i",
}

# Extensões aceitas por agora (para a vetorização: .csv e .txt)
# Obs: você pode aceitar PDF/DOCX para arquivamento, mas a vetorização atual ignora (para modelos futuros).
ALLOWED_EXTS_VETORIZACAO = {".csv", ".txt"}
ALLOWED_EXTS_ARQUIVO = {".pdf", ".docx", ".doc"}  # opcionais para acervo
ALLOWED_EXTS = ALLOWED_EXTS_VETORIZACAO | ALLOWED_EXTS_ARQUIVO

# Catálogo de produtos (metadados de classificação)
CATALOGO_PATH = Path("produtos/_catalogo.json")
CATALOGO_PATH.parent.mkdir(parents=True, exist_ok=True)
if not CATALOGO_PATH.exists():
    CATALOGO_PATH.write_text("[]", encoding="utf-8")


def _ler_catalogo() -> list[dict]:
    try:
        return json.loads(CATALOGO_PATH.read_text(encoding="utf-8"))
    except Exception:
        return []


def _salvar_catalogo(itens: list[dict]) -> None:
    CATALOGO_PATH.write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding="utf-8")


def _atualizar_catalogo(nome_produto: str, grupo: str, subgrupo: str) -> dict:
    """Garante entrada no catálogo com classificação (grupo/subgrupo)."""
    catalogo = _ler_catalogo()
    slug = slugify(nome_produto)
    now = datetime.now().isoformat()

    # Atualiza ou insere
    for item in catalogo:
        if item.get("slug") == slug:
            item.update({
                "nome": nome_produto,
                "grupo": grupo,
                "subgrupo": subgrupo,
                "atualizado_em": now,
            })
            _salvar_catalogo(catalogo)
            return item

    novo = {
        "slug": slug,
        "nome": nome_produto,
        "grupo": grupo,
        "subgrupo": subgrupo,
        "criado_em": now,
        "atualizado_em": now,
    }
    catalogo.append(novo)
    _salvar_catalogo(catalogo)
    return novo


@router.get("/tipos")
def listar_tipos():
    """Lista os tipos de documentos aceitos (para o front montar os selects)."""
    return {"tipos": ALLOWED_TYPES}


@router.post("")
async def upload_multi(
    produto_nome: str = Form(..., description="Nome do produto (ex: 'Queijo Minas Frescal')"),
    grupo: str = Form(..., description="Grupo (ex: 'Pescados e Frutos do Mar')"),
    subgrupo: str = Form(..., description="Subgrupo (ex: 'Peixes')"),

    # Listas paralelas: cada arquivo tem um tipo correspondente
    tipos: List[str] = Form(..., description="Lista de tipos, na mesma ordem dos arquivos"),
    arquivos: List[UploadFile] = File(..., description="Arquivos a serem enviados (múltiplos)"),
):
    """
    Recebe N arquivos + um tipo por arquivo, valida, padroniza nomes e salva em:
      produtos/<slug_produto>/{tipo}_{slug_produto}.<ext>

    Observações:
    - Mantemos a estrutura esperada pelo vetorazer.py (direto por produto).
    - Registramos/atualizamos a classificação no catálogo (_catalogo.json).
    - Para vetorização, priorize .csv e .txt (demais ficam arquivados para consulta).
    """
    if len(tipos) != len(arquivos):
        raise HTTPException(status_code=400, detail="A quantidade de 'tipos' deve ser igual à de 'arquivos'.")

    # Validação dos tipos
    tipos_norm = []
    for t in tipos:
        tnorm = slugify(t)  # ex: "Formulário I" -> "formulario_i"
        tnorm = TIPO_ALIASES.get(tnorm, tnorm)
        if tnorm not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo não suportado: '{t}'. Permitidos: {', '.join(ALLOWED_TYPES)}"
            )
        tipos_norm.append(tnorm)

    # Normaliza produto e cria pasta
    produto_slug = slugify(produto_nome)
    destino_dir = Path("produtos") / produto_slug
    destino_dir.mkdir(parents=True, exist_ok=True)

    # Atualiza catálogo
    meta = _atualizar_catalogo(produto_nome, grupo, subgrupo)

    salvos = []
    erros = []

    for idx, up in enumerate(arquivos):
        tipo_doc = tipos_norm[idx]
        nome_orig = up.filename or f"arquivo_{idx}"
        ext = Path(nome_orig).suffix.lower().strip()

        if ext not in ALLOWED_EXTS:
            erros.append({
                "arquivo": nome_orig,
                "motivo": f"Extensão não suportada '{ext}'. Aceitas: {sorted(ALLOWED_EXTS)}"
            })
            continue

        # Nome final: <tipo>_<produto-slug>.<ext>  (compatível com vetorazer)
        # Se já existir, adiciona sufixo incremental
        base_name = f"{tipo_doc}_{produto_slug}{ext}"
        destino_path = destino_dir / base_name

        if destino_path.exists():
            # Evita overwrite: acrescenta contador incremental
            c = 2
            while True:
                candidato = destino_dir / f"{tipo_doc}_{produto_slug}_{c}{ext}"
                if not candidato.exists():
                    destino_path = candidato
                    break
                c += 1

        # (Opcional) Limite de tamanho: 20 MB
        MAX_MB = 20
        size = 0
        with open(destino_path, "wb") as fout:
            while True:
                chunk = await up.read(1024 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_MB * 1024 * 1024:
                    fout.close()
                    destino_path.unlink(missing_ok=True)
                    erros.append({
                        "arquivo": nome_orig,
                        "motivo": f"Arquivo excede {MAX_MB} MB"
                    })
                    # esvazia restante do stream
                    while await up.read(1024 * 1024):
                        pass
                    break
                fout.write(chunk)

        if not destino_path.exists():
            continue  # já foi registrado como erro acima

        salvos.append({
            "arquivo_original": nome_orig,
            "arquivo_salvo": str(destino_path),
            "tipo": tipo_doc,
            "ext": ext,
        })

    # Monta resposta
    status = 207 if erros and salvos else (400 if erros and not salvos else 200)
    payload = {
        "produto": {"slug": produto_slug, "nome": produto_nome, "grupo": meta["grupo"], "subgrupo": meta["subgrupo"]},
        "arquivos_salvos": salvos,
        "erros": erros,
        "observacoes": [
            "Para indexação automática pelo vetorazer, priorize .csv ou .txt.",
            "A vetorização infere o tipo pelo prefixo do nome do arquivo (ex.: appcc_, pac_, bpf_, ...).",
            "Arquivos duplicados recebem sufixo incremental (_2, _3, ...).",
        ],
    }
    return JSONResponse(status_code=status, content=payload)
