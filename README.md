# Siqualia - Consulta de Perigos em Etapas de Processos

Este repositório contém uma API construída com **FastAPI** para consulta de perigos em diferentes etapas de processos, como parte do projeto Siqualia. A API utiliza um modelo de embeddings para realizar buscas semânticas entre etapas e perigos. O frontend é um simples HTML que se comunica com a API para exibir os resultados.

## Tecnologias Utilizadas

- **Backend**: FastAPI
- **Modelo de Embeddings**: `sentence-transformers` (para encontrar similaridade semântica entre etapas)
- **Frontend**: HTML, JavaScript

## Estrutura do Projeto

1. **API (FastAPI)**: A API expõe um endpoint `/query`, onde o usuário pode enviar uma etapa de processo e receber informações sobre perigos, medidas de controle e similaridade.
2. **Frontend (HTML)**: A página HTML permite que o usuário insira uma etapa de processo e visualize os perigos associados a ela.

## Como Usar

### 1. Inicializando a API (Backend)

Para rodar o backend da aplicação, você precisa ter o Python e as dependências do projeto instaladas.

#### Passo 1: Instalar as dependências

Se você ainda não tem as dependências, instale-as com o comando abaixo (preferencialmente em um ambiente virtual):

```bash
pip install -r requirements.txt
```

O arquivo `requirements.txt` deve conter as bibliotecas necessárias para rodar o backend. Aqui está um exemplo de conteúdo para o `requirements.txt`:

```
torch
fastapi
pydantic
sentence-transformers
uvicorn
```

#### Passo 2: Executar o servidor da API

Para iniciar o servidor backend, execute o seguinte comando:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8001
```

Isso irá rodar o servidor na URL `http://127.0.0.1:8001`. A API estará escutando as requisições POST no endpoint `/query`.

### 2. Usando o Frontend (HTML)

O frontend é uma página HTML simples que permite ao usuário inserir a etapa do processo e consultar os perigos associados.

#### Passo 1: Executar um servidor Python para servir o arquivo HTML

Se você estiver utilizando uma porta diferente, como a porta `8001`, para o servidor API, você pode usar um servidor HTTP simples para servir o arquivo HTML. No diretório onde o arquivo `index.html` está localizado, execute o seguinte comando:

```bash
python -m http.server 8000
```

Isso irá rodar um servidor HTTP na URL `http://127.0.0.1:8000`, e você poderá acessar o arquivo HTML diretamente.

#### Passo 2: Realizar a consulta

Na interface da página, digite a **etapa do processo** (por exemplo, "Armazenamento") no campo de entrada e clique em **Buscar**.

A página enviará uma requisição POST para a API, e o resultado será exibido abaixo do botão, com os seguintes detalhes:

- **Etapa**: Nome da etapa do processo.
- **Perigos**: Os perigos associados à etapa.
- **Medida de Controle**: A medida de controle recomendada para o perigo.
- **Similaridade**: A similaridade entre a etapa informada e as etapas cadastradas no modelo.

### Arquivo de Dados (dados.json)

Os dados utilizados pela API são carregados de um arquivo JSON chamado `dados.json`. O arquivo deve ter o seguinte formato:

```json
[
    {
        "id": 1,
        "etapa": "Armazenamento",
        "perigo": {
            "físico": "Contaminação por corpos estranhos.",
            "químico": "Presença de pesticidas.",
            "biológico": "Contaminação por fungos."
        },
        "medida_controle": "Armazenar em local seco e arejado."
    },
    {
        "id": 2,
        "etapa": "Processamento",
        "perigo": {
            "físico": "Contaminação por metais.",
            "químico": "Decomposição devido ao calor.",
            "biológico": "Presença de bactérias patogênicas."
        },
        "medida_controle": "Utilizar equipamentos de segurança e controle de temperatura."
    }
]
```

Se o arquivo `dados.json` não for encontrado ou estiver mal formatado, a API gerará um erro.

## Notas

- Certifique-se de que o arquivo `dados.json` esteja no mesmo diretório que o backend, ou ajuste o caminho no código da API.
- A similaridade entre a etapa informada e as etapas cadastradas é calculada com um modelo de embeddings, e a resposta será fornecida apenas se a similaridade for superior a um limite predefinido.
