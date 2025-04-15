# Siqualia - Sistema Inteligente de Qualidade em Alimentos

Este repositório contém a API e o frontend do projeto **Siqualia**, um sistema para consulta e análise de perigos em diferentes etapas de processos produtivos na indústria de alimentos. A API é construída com **FastAPI** e utiliza embeddings para identificação semântica de etapas. O frontend é uma interface HTML+JavaScript para interação com os dados.

---

## Tecnologias Utilizadas

- **Backend**: FastAPI
- **Frontend**: HTML + JavaScript
- **Modelo de Embeddings**: `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Servidor de desenvolvimento**: Uvicorn

---

## Funcionalidades

### 🔍 Consulta de Etapas
- O usuário informa uma etapa do processo.
- A API encontra a etapa mais similar na base de dados do produto selecionado, com base em embeddings.
- São exibidos os perigos (biológico, químico e físico) e suas respectivas medidas de controle.

### 📋 Questionário de PCC
- Após a consulta, o usuário responde a um questionário para cada tipo de perigo identificado.
- A lógica implementa uma árvore de decisão baseada no Codex Alimentarius para determinar se a etapa é um Ponto Crítico de Controle (PCC).
- O sistema exibe uma tabela com a decisão final para cada perigo (PCC ou não).

### 📁 Suporte a múltiplos produtos
- Os dados são separados por produto em arquivos JSON (ex: `mel.json`, `queijo.json`).
- O usuário seleciona o produto via `<select>` no frontend.
- A API carrega dinamicamente os dados do produto no momento da requisição.

### 🌐 Interface Web
- Interface simples com campos para seleção de produto e entrada da etapa.
- Resultado exibido com tabela de perigos e questionário dinâmico.

---

## Estrutura do Projeto

```
siqualia/
├── app/
│   ├── main.py                # Inicialização da aplicação FastAPI
│   ├── routes/               # Endpoints (etapa, questionario, avaliar, produtos)
│   ├── utils/dados.py        # Funções de carregamento e busca de etapas
│   └── static/               # Arquivos HTML e CSS
│       ├── index.html
│       └── style.css
├── data/                     # Arquivos JSON por produto (mel.json, queijo.json...)
├── requirements.txt
└── README.md
```

---

## Como Usar

### 🔧 Backend (API FastAPI)

#### 1. Instale as dependências:
```bash
pip install -r requirements.txt
```

#### 2. Execute a API com Uvicorn:
```bash
uvicorn app.main:app --reload
```

A API ficará disponível em `http://127.0.0.1:8000`

### 🌍 Frontend (Interface Web)

Acesse `http://127.0.0.1:8000/` diretamente após iniciar o backend. O arquivo `index.html` é servido automaticamente pela API.

---

## Endpoints da API

### `GET /produtos`
Retorna a lista de produtos disponíveis (com base nos arquivos `.json` na pasta `data/`).

### `POST /etapa/pesquisar`
Consulta uma etapa com base no produto e retorna a mais similar, incluindo perigos e medidas de controle.
```json
{
  "produto": "mel",
  "etapa": "armazenamento do produto"
}
```

### `POST /etapa/questionario`
Retorna as perguntas do fluxograma de decisão para uma etapa válida.

### `POST /etapa/avaliar`
Recebe as respostas do questionário e retorna a decisão para cada perigo.
```json
{
  "produto": "mel",
  "etapa": "armazenamento do produto",
  "respostas": {
    "B": { "Q1": "Sim", "Q2": "Não", "Q3": "Sim", "Q4": "Não" },
    "Q": { "Q1": "Não", "Q1a": "Não" },
    "F": { "Q1": "Sim", "Q2": "Sim" }
  }
}
```

---

## Exemplo de Arquivo de Dados (mel.json)

```json
[
  {
    "id": 1,
    "etapa": "Recepção",
    "perigo": {
      "biologico": "Presença de esporos de fungos e bactérias",
      "quimico": "Resíduos de defensivos agrícolas",
      "fisico": "Partículas de sujeira e detritos"
    },
    "medida_controle": {
      "biologico": "Lavagem e desinfecção das melgueiras",
      "quimico": "Controle de fornecedores e análise de resíduos de defensivos",
      "fisico": "Inspeção visual e remoção de sujidades"
    }
  },
  ...
]
```

---

## Notas

- O sistema não utiliza banco de dados; os dados estão organizados em arquivos JSON por produto.
- A lógica de identificação de PCCs segue o fluxograma oficial da metodologia APPCC.
- O frontend reinicializa os campos dinamicamente para garantir que apenas respostas visíveis sejam consideradas.

---

## Futuras Expansões
- Classificação da probabilidade e da severidade
- Geração automática do plano APPCC final
