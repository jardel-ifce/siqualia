import torch
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
import json

# Inicializa o FastAPI
app = FastAPI()

# Configuração do CORS para permitir chamadas do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega o modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Carregar os dados de etapas e perigos a partir do arquivo JSON
try:
    with open("dados.json", 'r', encoding='utf-8') as f:
        documents = json.load(f)
except FileNotFoundError as e:
    print(f"Erro ao carregar o arquivo: {e}")
    raise Exception("Arquivo 'dados.json' não encontrado no caminho especificado.")

# Gera os embeddings das etapas para busca semântica
doc_embeddings = {doc["id"]: model.encode(doc["etapa"], convert_to_tensor=True) for doc in documents}


class QueryRequest(BaseModel):
    etapa: str


# Definir um limite de similaridade
SIMILARIDADE_LIMITE = 0.6  # Defina esse valor conforme necessário


@app.post("/query")
def query_pcc(request: QueryRequest):
    query_embedding = model.encode(request.etapa, convert_to_tensor=True)

    # Calcula a similaridade entre a query e as etapas cadastradas
    similarities = {}
    for doc_id, emb in doc_embeddings.items():
        if isinstance(emb, torch.Tensor):  # Verifica se é um tensor antes de calcular
            similarities[doc_id] = util.pytorch_cos_sim(query_embedding, emb)[0].item()
        else:
            print(f"Erro: emb para {doc_id} não é um tensor válido.")

    # Identifica a etapa mais similar
    best_match_id = max(similarities, key=similarities.get)
    best_match_similarity = similarities[best_match_id]

    # Verifica se a similaridade está acima do limite
    if best_match_similarity < SIMILARIDADE_LIMITE:
        raise HTTPException(status_code=400, detail="A etapa informada não corresponde ao contexto do Produto.")

    best_match = next(doc for doc in documents if doc["id"] == best_match_id)

    return {
        "etapa": best_match["etapa"],
        "perigos": best_match["perigo"],
        "medida_controle": best_match["medida_controle"],
        "similaridade": best_match_similarity
    }
