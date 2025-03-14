# modelo.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 🔹 Inicialização do modelo para embeddings de frases
model = SentenceTransformer('all-MiniLM-L6-v2')

def criar_embeddings(textos):
    """
    Função para criar os embeddings dos textos utilizando o modelo SentenceTransformer.
    
    Parâmetros:
    - textos: Lista de textos para os quais os embeddings serão criados.
    
    Retorna:
    - Lista de embeddings.
    """
    return model.encode(textos, convert_to_tensor=False)

def criar_indice_faiss(embeddings):
    """
    Função para criar um índice FAISS para buscas eficientes.
    
    Parâmetros:
    - embeddings: Lista de embeddings a serem indexados.
    
    Retorna:
    - Índice FAISS.
    """
    d = embeddings.shape[1]  # Dimensão dos embeddings
    index = faiss.IndexFlatL2(d)
    index.add(np.array(embeddings, dtype=np.float32))  # Adicionar os vetores ao índice
    return index
