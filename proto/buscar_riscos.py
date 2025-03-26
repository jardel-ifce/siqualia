# buscar_riscos.py 
from modelo import model, criar_embeddings, criar_indice_faiss
import numpy as np
from sentence_transformers import util

def encontrar_riscos(entrada_usuario, riscos_data, riscos_embeddings, index, top_n=3):
    """
    Função para encontrar os riscos mais semelhantes com base na entrada do usuário.
    
    Parâmetros:
    - entrada_usuario: Texto digitado pelo usuário.
    - riscos_data: Lista de textos de riscos.
    - riscos_embeddings: Lista de embeddings dos riscos.
    - index: Índice FAISS para busca eficiente.
    - top_n: Número de resultados a serem retornados (padrão: 3).
    
    Retorna:
    - Lista de resultados com riscos mais semelhantes, ordenados por similaridade.
    """
    emb_entrada = model.encode(entrada_usuario, convert_to_tensor=False).reshape(1, -1)
    _, indices = index.search(np.array(emb_entrada, dtype=np.float32), top_n)
    
    resultados = [(riscos_data[i], util.cos_sim(emb_entrada, riscos_embeddings[i]).item()) for i in indices[0]]
    return sorted(resultados, key=lambda x: x[1], reverse=True)
