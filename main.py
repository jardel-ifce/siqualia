# main.ipynb
from carregar_arquivos import carregar_riscos
from modelo import criar_embeddings, criar_indice_faiss
from buscar_riscos import encontrar_riscos

# 🔹 Carregar riscos da planilha
riscos_data = carregar_riscos("riscos.csv")

# 🔹 Criar embeddings dos riscos
riscos_embeddings = criar_embeddings(riscos_data)

# 🔹 Criar um índice FAISS para buscas eficientes
index = criar_indice_faiss(riscos_embeddings)

# 🔹 Solicitar entrada do usuário
entrada_usuario = input("Digite a situação para análise: ")

# 🔹 Encontrar riscos semelhantes
resultados = encontrar_riscos(entrada_usuario, riscos_data, riscos_embeddings, index)

# 🔹 Exibir resultados
print("Riscos associados:")
for risco, score in resultados:
    print(f"- {risco} (Similaridade: {score:.4f})")
