# carregar_arquivos.py
import pandas as pd

def carregar_riscos(caminho_arquivo):
    """
    Função para carregar os riscos a partir de um arquivo CSV.
    
    Parâmetros:
    - caminho_arquivo: Caminho do arquivo CSV contendo os riscos.
    
    Retorna:
    - Lista com os textos dos riscos.
    """
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        return df["Texto"].tolist()
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return []
