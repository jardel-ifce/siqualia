import json
from pathlib import Path
import unicodedata

DATA_PATH = Path(__file__).parent.parent / "data" / "etapas_completas_com_medidas.json"

def carregar_documentos():
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar dados: {e}")

def normalizar(texto: str):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").strip().lower()

def buscar_etapa_por_nome(etapa_nome: str, documentos):
    etapa_norm = normalizar(etapa_nome)
    return next((doc for doc in documentos if normalizar(doc["etapa"]) == etapa_norm), None)
