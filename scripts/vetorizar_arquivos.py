import os
import json
import pickle
import pandas as pd
import faiss
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Caminhos
ROOT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = ROOT_DIR / "produtos"
INDEX_DIR = ROOT_DIR / "indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)
JSON_PATH = INDEX_DIR / "documentos_recebidos.json"

# Cria arquivo JSON vazio se não existir
if not JSON_PATH.exists():
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

MODEL_NAME = "intfloat/e5-base-v2"

model = SentenceTransformer(MODEL_NAME)

renomear_colunas = {
    "perigos": "perigo",
    "medidas preventivas": "medida",
    "justificativa": "justificativa",
    "o perigo é significativo?": "perigo_significativo",
    "etapa": "etapa",
    "probabilidade": "probabilidade",
    "severidade": "severidade",
    "risco": "risco",
    "codigo": "tipo"
}

# Carrega a lista de documentos a processar
with open(JSON_PATH, "r", encoding="utf-8") as f:
    documentos = json.load(f)

# Detecta novos arquivos ainda não registrados no JSON
documentos_paths = {Path(doc["caminho"]) for doc in documentos}
novos = []

for path in BASE_DIR.glob("*/*.*"):
    if path.suffix.lower() not in [".csv", ".txt"]:
        continue
    rel = path.relative_to(BASE_DIR)
    if rel not in documentos_paths:
        produto = rel.parts[0]
        nome = rel.name
        tipo = nome.replace(f"_{produto}{path.suffix}", "").lower()
        novos.append({
            "produto": produto,
            "arquivo": nome,
            "caminho": str(rel),
            "tipo": tipo,
            "vetorizado": False
        })

if novos:
    print(f"[NOVOS] {len(novos)} novos documentos detectados.")
    documentos.extend(novos)

# Processa documentos
for doc in documentos:
    if doc.get("vetorizado") is True:
        print(f"[PULADO] Já vetorizado: {doc['arquivo']}")
        continue

    caminho = BASE_DIR / doc["caminho"]
    produto = doc["produto"]
    nome_arquivo = doc["arquivo"]
    ext = caminho.suffix.lower()
    tipo = doc["tipo"]

    index_dir = INDEX_DIR / produto
    index_dir.mkdir(parents=True, exist_ok=True)

    index_path = index_dir / f"{tipo}.index"
    meta_path = index_dir / f"{tipo}.pkl"

    print(f"[PROCESSANDO] {produto}/{tipo} → {nome_arquivo}")

    try:
        if ext == ".csv":
            df = pd.read_csv(caminho)
            df.columns = [col.lower().strip() for col in df.columns]
            df.rename(columns=renomear_colunas, inplace=True)
            df = df.fillna("")

            if "etapa" not in df.columns or "perigo" not in df.columns:
                print(f"[ERRO] CSV inválido: {nome_arquivo}")
                continue

            sentencas = df.apply(lambda row: " - ".join(str(v) for v in row.values if str(v).strip()), axis=1).tolist()
            metadados = df.to_dict(orient="records")

        elif ext == ".txt":
            with open(caminho, "r", encoding="utf-8") as f:
                linhas = [linha.strip() for linha in f if linha.strip()]
            sentencas = linhas
            metadados = [{"linha": i+1, "conteudo": s} for i, s in enumerate(linhas)]

        else:
            print(f"[IGNORADO] Extensão não suportada: {ext}")
            continue

        embeddings = model.encode(sentencas, convert_to_numpy=True, normalize_embeddings=True)
        index = faiss.IndexFlatIP(embeddings.shape[1])
        index.add(embeddings)

        faiss.write_index(index, str(index_path))
        with open(meta_path, "wb") as f:
            pickle.dump(metadados, f)

        doc["vetorizado"] = True
        doc["ultima_execucao"] = datetime.now().isoformat()
        print(f"[OK] Índice salvo: {index_path}")

    except Exception as e:
        print(f"[ERRO] {nome_arquivo}: {e}")

# Carrega os documentos registrados
with open(JSON_PATH, "r", encoding="utf-8") as f:
    documentos = json.load(f)

print("[FINALIZADO] Vetorização concluída.")