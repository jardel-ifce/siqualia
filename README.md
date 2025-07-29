# SIQUALIA – Assistente de Geração do Relatório APPCC

## 🧩 Visão Geral da Implementação

Esta versão do sistema SIQUALIA implementa o preenchimento semiautomático do **Formulário I** (Plano de Monitoramento de PCC) e a geração do **Relatório Final APPCC** para produtos alimentícios.

Atualmente, o fluxo está disponível para o produto **mel**, com base nos perigos classificados como **Pontos Críticos de Controle (PCC)** no Formulário H.

---

## 🧪 Preenchimento do Formulário I

O preenchimento do Formulário I segue a lógica:

* O botão **“I”** é exibido sempre que a etapa conter um perigo classificado como **PCC**.
* Ao clicar no botão “I”, o sistema:

  * Verifica se já há sugestão salva em `sessionStorage` para evitar repetição de chamada ao backend.
  * Caso **não haja sugestão anterior**, o sistema consulta o endpoint:

    ```
    POST /crud/resumo/sugerir
    ```
  * Este endpoint utiliza **busca semântica com FAISS + SentenceTransformer** para sugerir o preenchimento com base nos documentos técnicos do produto.

---

## 📄 Geração do Relatório Final APPCC

* O botão **“Relatório”** é exibido apenas quando:

  * O perigo da etapa foi classificado como **PCC** no Formulário H;
  * O Formulário I está **preenchido** (todos os campos obrigatórios).
* O relatório consolida dados dos Formulários G, H e I, compondo o plano final de controle para a etapa.

---

## 🧠 Vetorização e Sistema de Sugestões com IA

### 📥 Vetorização de Arquivos CSV

O SIQUALIA utiliza documentos técnicos como **PAC**, **BPF** e **APPCC** em formato `.csv` para alimentar sua base de conhecimento. Estes arquivos são processados da seguinte forma:

1. **Leitura e pré-processamento**:

   * Cada linha do `.csv` é tratada como uma entrada contendo etapa, tipo de perigo, justificativa, medidas, monitoramento, etc.

2. **Geração de embeddings**:
   
   * O modelo `SentenceTransformer` (`msmarco-distilbert-base-v4`) transforma os textos em vetores semânticos.

3. **Indexação com FAISS**:

   * Os vetores são armazenados em índices `.index`.
   * Os metadados originais são salvos em arquivos `.pkl`.

```
indexes/
└── mel/
    ├── pac_etapa.index
    ├── pac_etapa.pkl
    ├── pac_contexto.index
    ├── pac_contexto.pkl
    ├── bpf_contexto.index
    └── ...
```

---

### 🔍 Consulta Semântica por Etapa

Quando o usuário digita uma **etapa de produção**, o sistema:

1. Transforma a etapa em vetor usando o modelo `SentenceTransformer`.
2. Realiza uma busca nos índices vetoriais FAISS.
3. Retorna as etapas mais semelhantes com base na **similaridade de embeddings**.

---

### 🤖 Sugestão Automática de Formulários

#### 🧪 Formulário G – Perigos

* Após confirmar uma etapa, o sistema consulta os índices por etapa e retorna automaticamente os perigos conhecidos.
* Inclui:

  * Código e tipo (B, F, Q)
  * Justificativa
  * Probabilidade, Severidade, Risco
  * Medidas preventivas
* O usuário pode editar os dados e salvá-los.

#### 📋 Formulário H – Questionário

* Ao finalizar o Formulário G, o sistema permite avaliar o perigo com base em uma árvore de decisão (fluxo de perguntas).
* A resposta final pode ser:

  * **É um PCC**
  * **Não é um PCC**
  * **Modificar o processo**
* Os dados são salvos por perigo no campo `questionario`.

#### 📄 Formulário I – Resumo APPCC

* Quando o perigo é classificado como PCC, o botão **“I”** fica disponível.
* O sistema envia os dados ao backend e retorna uma **sugestão automática** com:

  * Limite crítico
  * Monitoramento (o quê, como, quando, quem)
  * Ação corretiva
  * Registro
  * Verificação
* O conteúdo pode ser editado e salvo diretamente no JSON.

---

## ⚠️ Limitações atuais

* Não há controle contra duplicatas ou arquivos malformados.
* O relatório ainda depende da integridade dos formulários G, H e I preenchidos manualmente.

---

## 🛠 Melhorias planejadas

* Implementar validações mais rígidas e alertas sobre preenchimento incompleto.
* Melhorar layout e navegação entre os formulários.

---

## ▶️ Como executar o sistema

1. Instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Execute o backend:

```bash
uvicorn app.main:app --reload
```

3. Acesse no navegador:

```bash
http://localhost:8000
```

---

## 📂 Estrutura relevante de arquivos

```bash
avaliacoes/
└── produtos/
    └── mel/
        └── filtragem_c9a7d6.json

indexes/
└── mel/
    ├── pac_etapa.index
    ├── pac_etapa.pkl
    ├── bpf_contexto.index
    └── ...
```