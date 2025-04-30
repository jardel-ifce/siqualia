import os
import glob
import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer

# Caminhos
BASE_DIR = "produtos"
INDEX_DIR = "indexes"
model = SentenceTransformer("all-MiniLM-L6-v2")

print("[INÍCIO] Iniciando varredura de arquivos CSV...")

csvs = glob.glob(f"{BASE_DIR}/*/*.csv")
print(f"[DEBUG] Encontrados {len(csvs)} arquivos:")
for c in csvs:
    print(" →", c)

# Mapeamento de colunas para padronização
renomear_colunas = {
    "perigos": "perigo",
    "medidas preventivas": "medida",
    "justificativa": "justificativa",
    "o perigo é significativo?": "perigo_significativo",
    "etapa": "etapa",
    "probabilidade": "probabilidade",
    "severidade": "severidade",
    "risco": "risco",
    "codigo": "tipo",
    "tipo": "tipo"  # se não existir, pode ser inferido futuramente
}

# Verifica e vetoriza todos os CSVs encontrados
for csv_path in glob.glob(f"{BASE_DIR}/*/*.csv"):
    produto = os.path.basename(os.path.dirname(csv_path))
    nome_arquivo = os.path.basename(csv_path)
    tipo = nome_arquivo.replace(f"_{produto}.csv", "").lower()

    # Define os caminhos de saída
    index_dir = os.path.join(INDEX_DIR, produto)
    os.makedirs(index_dir, exist_ok=True)

    index_path = os.path.join(index_dir, f"{tipo}.index")
    meta_path = os.path.join(index_dir, f"{tipo}.pkl")

    # Se os arquivos já existem, pula
    if os.path.exists(index_path) and os.path.exists(meta_path):
        print(f"Índice já existe para: {produto}/{tipo}")
        continue

    print(f"Vetorizando: {csv_path}")
    df = pd.read_csv(csv_path)

    # Padronizar colunas
    df.columns = [col.lower().strip() for col in df.columns]
    df.rename(columns=renomear_colunas, inplace=True)

    if "etapa" not in df.columns or "perigo" not in df.columns:
        print(f"CSV inválido: faltando coluna 'etapa' ou 'perigo'")
        continue

    # Gera sentenças combinando colunas úteis
    sentencas = df.apply(lambda row: " - ".join(str(v) for v in row.values if pd.notna(v)), axis=1).tolist()
    embeddings = model.encode(sentencas, convert_to_numpy=True, normalize_embeddings=True)

    # Cria e salva índice FAISS
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, index_path)

    # Salva metadados padronizados
    metadados = df.to_dict(orient="records")
    with open(meta_path, "wb") as f:
        pickle.dump(metadados, f)

    print(f"Índice salvo em: {index_path}")
