import json
from pathlib import Path
import unicodedata

DATA_DIR = Path(__file__).parent.parent / "data"

def normalizar(texto: str):
    return unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("ASCII").strip().lower()

def carregar_documentos(produto: str):
    try:
        nome_arquivo = f"{normalizar(produto)}.json"
        caminho = DATA_DIR / nome_arquivo
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f"Arquivo de dados para o produto '{produto}' não encontrado.")
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar dados: {e}")

def buscar_etapa_por_nome(etapa_nome: str, documentos):
    etapa_norm = normalizar(etapa_nome)
    return next((doc for doc in documentos if normalizar(doc["etapa"]) == etapa_norm), None)