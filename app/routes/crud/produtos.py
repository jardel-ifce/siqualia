# 📁 app/routes/crud/produtos.py

from pathlib import Path
from fastapi import APIRouter, Query
from typing import Dict, List
import json

router = APIRouter(prefix="/crud", tags=["CRUD - Produtos"])


# -----------------------
# Lista plana (legado)
# -----------------------
@router.get("/produtos")
def listar_produtos():
    """
    Lista slugs de produtos com base nas pastas dentro de 'produtos'.
    (Mantido para compatibilidade; a UI nova usa /crud/produtos/agrupados)
    """
    produtos_dir = Path("produtos")
    if not produtos_dir.exists():
        return []
    return [p.name for p in produtos_dir.iterdir() if p.is_dir() and not p.name.startswith("_")]


# -----------------------
# Lista agrupada (novo)
# -----------------------

PRODUTOS_DIR = Path("produtos")
INDEX_DIR = Path("indexes")
CATALOGO_PATH = PRODUTOS_DIR / "_catalogo.json"  # criado pelo uploads.py (opcional)
META_FILENAME = "_meta.json"  # metadados locais por produto (opcional)


def _title_from_slug(slug: str) -> str:
    return slug.replace("_", " ").title()


def _carregar_catalogo() -> List[dict]:
    if CATALOGO_PATH.exists():
        try:
            return json.loads(CATALOGO_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def _produto_vetorizado(slug: str) -> bool:
    """Verdadeiro se houver ao menos um índice FAISS em indexes/<slug>/*.index"""
    pasta = INDEX_DIR / slug
    return pasta.exists() and any(p.suffix == ".index" for p in pasta.glob("*.index"))


def _inferir_meta_por_produto(slug: str) -> dict:
    """
    Retorna: { slug, nome, grupo, subgrupo }
    Preferências:
      1) catálogo global (produtos/_catalogo.json)
      2) meta local por produto (produtos/<slug>/_meta.json)
      3) fallback pelo slug
    """
    # 1) catálogo global
    for item in _carregar_catalogo():
        if item.get("slug") == slug:
            return {
                "slug": slug,
                "nome": item.get("nome") or _title_from_slug(slug),
                "grupo": item.get("grupo") or "Outros",
                "subgrupo": item.get("subgrupo") or "Geral",
            }

    # 2) meta local
    meta_path = PRODUTOS_DIR / slug / META_FILENAME
    if meta_path.exists():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            return {
                "slug": slug,
                "nome": _title_from_slug(slug),
                "grupo": (meta.get("grupo") or "Outros") or "Outros",
                "subgrupo": (meta.get("subgrupo") or "Geral") or "Geral",
            }
        except Exception:
            pass

    # 3) fallback
    return {
        "slug": slug,
        "nome": _title_from_slug(slug),
        "grupo": "Outros",
        "subgrupo": "Geral",
    }


@router.get("/produtos/agrupados")
def listar_produtos_agrupados(
        somente_vetorizados: bool = Query(True, description="Se True, retorna apenas produtos com índices FAISS.")
):
    """
    Estrutura de saída:
    {
      "grupos": [
        { "grupo": "Laticínios",
          "subgrupos": [
            { "subgrupo": "Queijos",
              "produtos": [ { "slug": "...", "nome": "...", "vetorizado": true } ]
            }
          ]
        }
      ]
    }
    """
    if not PRODUTOS_DIR.exists():
        return {"grupos": []}

    # slugs candidatos = pastas de produtos (ignora nomes iniciados com "_")
    slugs = sorted([p.name for p in PRODUTOS_DIR.iterdir() if p.is_dir() and not p.name.startswith("_")])

    grupos: Dict[str, Dict[str, List[dict]]] = {}

    for slug in slugs:
        vet = _produto_vetorizado(slug)
        if somente_vetorizados and not vet:
            continue

        meta = _inferir_meta_por_produto(slug)
        g, sg = meta["grupo"], meta["subgrupo"]

        if g not in grupos:
            grupos[g] = {}
        if sg not in grupos[g]:
            grupos[g][sg] = []

        grupos[g][sg].append({
            "slug": slug,
            "nome": meta["nome"],
            "vetorizado": vet
        })

    # Ordena grupos, subgrupos e produtos alfabeticamente
    saida = {"grupos": []}
    for g in sorted(grupos.keys(), key=lambda s: s.lower()):
        sub_saida = []
        for sg in sorted(grupos[g].keys(), key=lambda s: s.lower()):
            produtos_ordenados = sorted(grupos[g][sg], key=lambda p: p["nome"].lower())
            sub_saida.append({"subgrupo": sg, "produtos": produtos_ordenados})
        saida["grupos"].append({"grupo": g, "subgrupos": sub_saida})

    return saida
