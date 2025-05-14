import pickle
import math
from pathlib import Path

def limpar_nan(obj):
    if isinstance(obj, dict):
        return {k: limpar_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [limpar_nan(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    return obj

def consultar_perigos_por_etapa(produto: str, etapa_confirmada: str):
    indexes_dir = Path("indexes") / produto
    tipos = ["appcc", "pac", "bpf"]

    formulario_g = []

    for tipo in tipos:
        meta_path = indexes_dir / f"{tipo}.pkl"
        if not meta_path.exists():
            continue

        with open(meta_path, "rb") as f:
            metadados = pickle.load(f)

        for registro in metadados:
            etapa = registro.get("etapa", "").strip()
            if etapa.lower() == etapa_confirmada.lower():
                formulario_g.append({
                    "tipo": registro.get("tipo"),
                    "perigo": registro.get("perigo"),
                    "justificativa": registro.get("justificativa"),
                    "probabilidade": registro.get("probabilidade"),
                    "severidade": registro.get("severidade"),
                    "risco": registro.get("risco"),
                    "medida": registro.get("medida"),
                    "perigo_significativo": registro.get("perigo_significativo"),
                    "origem": tipo
                })

    if not formulario_g:
        return {"erro": f"Nenhum perigo encontrado para etapa: {etapa_confirmada}"}

    return limpar_nan({
        "produto": produto,
        "etapa": etapa_confirmada,
        "formulario_g": formulario_g
    })
