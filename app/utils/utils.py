import json
from pathlib import Path
import hashlib
import unicodedata
import re

BASE_DIR = Path("avaliacoes/produtos")

def slugify(texto: str) -> str:
    """
    Remove acentos e caracteres especiais, substitui espaços e barras por underscores
    e remove qualquer outro caractere que não seja alfanumérico, hífen ou underline.
    """
    # Remove acentos (ex: ç -> c, ã -> a, é -> e)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    texto = texto.strip().lower()
    texto = texto.replace(" ", "_")
    texto = texto.replace("/", "_")
    return re.sub(r'[^a-z0-9_-]', '', texto)


def gerar_nome_arquivo_etapa(produto: str, etapa: str) -> Path:
    """
    Gera o caminho completo para o arquivo da etapa usando produto e etapa,
    com nome padronizado e hash para garantir unicidade.
    """
    pasta = Path("avaliacoes") / "produtos" / produto.lower()
    nome_etapa_seguro = slugify(etapa.lower())  # remove caracteres inválidos como "/"
    hash_id = hashlib.md5(etapa.strip().encode()).hexdigest()
    return pasta / f"{nome_etapa_seguro}_{hash_id}.json"

def gerar_nome_arquivo(produto: str, etapa: str) -> str:
    etapa_normalizada = slugify(etapa)
    hash_val = hashlib.md5(etapa.strip().encode()).hexdigest()
    return f"{etapa_normalizada}_{hash_val}.json"

def obter_caminho_arquivo(produto: str, etapa: str) -> Path:
    nome_arquivo = gerar_nome_arquivo(produto, etapa)
    return BASE_DIR / produto.lower() / nome_arquivo

def carregar_dados_etapa(produto: str, etapa: str) -> tuple[dict, Path]:
    """
    Carrega os dados do arquivo JSON da etapa, retornando o conteúdo e o caminho.
    """
    caminho = gerar_nome_arquivo_etapa(produto, etapa)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    return dados, caminho


def proximo_id_perigo(lista_perigos: list) -> int:
    """
    Recebe diretamente a lista de perigos e retorna o próximo ID disponível.
    """
    ids = [p.get("id", 0) for p in lista_perigos if isinstance(p, dict)]
    return max(ids, default=0) + 1

def atualizar_resumo_do_perigo(produto: str, etapa: str, id_perigo: int, resumo: dict) -> bool:
    try:
        dados, caminho = carregar_dados_etapa(produto, etapa)
        for p in dados.get("perigos", []):
            if p.get("id") == id_perigo:
                p.setdefault("resumo", []).clear()
                p["resumo"].append(resumo)
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
                return True

        print("[ERRO] Perigo não encontrado com id:", id_perigo)
        return False
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar resumo: {e}")
        return False

def substituir_resumo_do_perigo(produto: str, etapa: str, id_perigo: int, resumo: dict) -> bool:
    try:
        dados, caminho = carregar_dados_etapa(produto, etapa)

        for p in dados.get("perigos", []):
            if p.get("id") == id_perigo:
                # Substitui completamente o conteúdo do resumo
                p["resumo"] = [resumo]
                with open(caminho, "w", encoding="utf-8") as f:
                    json.dump(dados, f, ensure_ascii=False, indent=2)
                return True

        print("[ERRO] Perigo não encontrado com id:", id_perigo)
        return False
    except Exception as e:
        print(f"[ERRO AO SUBSTITUIR RESUMO]: {e}")
        return False


