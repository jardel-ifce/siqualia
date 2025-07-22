import json
import pickle
import pandas as pd
import faiss
from pathlib import Path
from datetime import datetime
from sentence_transformers import SentenceTransformer

# Configurações de caminhos
ROOT_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = ROOT_DIR / "produtos"
INDEX_DIR = ROOT_DIR / "indexes"
INDEX_DIR.mkdir(parents=True, exist_ok=True)
JSON_PATH = INDEX_DIR / "documentos_recebidos.json"

# Cria arquivo JSON vazio se não existir
if not JSON_PATH.exists():
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump([], f)

# Modelo de embeddings
MODEL_NAME = "msmarco-distilbert-base-v4"
model = SentenceTransformer(MODEL_NAME)

# Renomeação das colunas
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

# Carrega a lista de documentos já processados
with open(JSON_PATH, "r", encoding="utf-8") as f:
    documentos = json.load(f)

# Detecta novos arquivos
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

# Processa os arquivos
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

            # Vetorização para ETAPA SIMPLES
            sentencas_etapa = df['etapa'].tolist()
            metadados_etapa = df.to_dict(orient="records")

            embeddings_etapa = model.encode(sentencas_etapa, convert_to_numpy=True, normalize_embeddings=True)
            index_etapa = faiss.IndexFlatIP(embeddings_etapa.shape[1])
            index_etapa.add(embeddings_etapa)

            index_path_etapa = index_dir / f"{tipo}_etapa.index"
            meta_path_etapa = index_dir / f"{tipo}_etapa.pkl"

            faiss.write_index(index_etapa, str(index_path_etapa))
            with open(meta_path_etapa, "wb") as f:
                pickle.dump(metadados_etapa, f)

            print(f"[OK] Índice de ETAPA SIMPLES salvo: {index_path_etapa}")

            # Vetorização para CONTEXTO COMPLETO
            sentencas_contexto = df.apply(lambda row: " - ".join(str(v) for v in row.values if str(v).strip()), axis=1).tolist()
            metadados_contexto = df.to_dict(orient="records")

            embeddings_contexto = model.encode(sentencas_contexto, convert_to_numpy=True, normalize_embeddings=True)
            index_contexto = faiss.IndexFlatIP(embeddings_contexto.shape[1])
            index_contexto.add(embeddings_contexto)

            index_path_contexto = index_dir / f"{tipo}_contexto.index"
            meta_path_contexto = index_dir / f"{tipo}_contexto.pkl"

            faiss.write_index(index_contexto, str(index_path_contexto))
            with open(meta_path_contexto, "wb") as f:
                pickle.dump(metadados_contexto, f)

            print(f"[OK] Índice de CONTEXTO COMPLETO salvo: {index_path_contexto}")

        else:
            print(f"[IGNORADO] Extensão não suportada: {ext}")
            continue

        doc["vetorizado"] = True
        doc["ultima_execucao"] = datetime.now().isoformat()

    except Exception as e:
        print(f"[ERRO] {nome_arquivo}: {e}")

# Atualiza o JSON de rastreamento
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(documentos, f, indent=4, ensure_ascii=False)

print("[FINALIZADO] Vetorização concluída.")
