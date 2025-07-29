# SIQUALIA – Assitente para Geração de Relatório APPCC

## 🧩 Visão Geral da Implementação

Esta versão do sistema **SIQUALIA** implementa o preenchimento semiautomático do **Formulário I** (Plano de Monitoramento de PCC) e a geração do **Relatório Final APPCC** para produtos alimentícios, com base nos dados dos Formulários G e H.

O sistema utiliza **busca semântica baseada em vetores FAISS + SentenceTransformer** para sugerir o preenchimento do Formulário I, além de permitir **edição manual, salvamento e geração de relatório**.

## 🧪 Preenchimento do Formulário I

* O botão **“I”** é exibido quando a etapa contém um perigo classificado como **PCC** (via Formulário H).
* Ao clicar no botão, o sistema:

  * Verifica se há sugestão armazenada localmente para evitar redundância.
  * Caso não haja, consulta o endpoint `/crud/resumo/sugerir`.
  * O backend utiliza embeddings vetoriais FAISS para sugerir o conteúdo do Formulário I.

## ✏️ Edição e Salvamento

* A sugestão gerada pode ser **editada diretamente pelo usuário** em um modal.
* O conteúdo editado é salvo via `PUT` no endpoint `/crud/resumo/atualizar`, atualizando o JSON da etapa.

## 📄 Geração do Relatório Final APPCC

* O botão **“Relatório”** é exibido apenas se:

  * O perigo foi classificado como **PCC**;
  * O Formulário I está **preenchido**.
* O relatório exibe dados consolidados dos Formulários G, H e I.

## ✅ Funcionalidades Implementadas

* Sugestão automática do Formulário I baseada em embeddings vetoriais.
* Edição completa e salvamento do Formulário I no frontend.
* Relatório final consolidado por etapa e perigo.
* Estrutura de arquivos organizada por produto e etapa com hash.

## ⚠️ Limitações atuais

* O sistema ainda está em fase de testes com o produto **mel**.
* A verificação entre formulários G, H e I ainda é parcial.
* Não há tratamento de erros para arquivos JSON inconsistentes.

## 🛠 Melhorias planejadas

* Suporte a múltiplos produtos com base vetorial própria.
* Detecção automática de campos não preenchidos nos formulários.
* Exportação do relatório APPCC em formato PDF.
* Validação e backup das edições realizadas.

---

## ▶️ Como executar

1. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o backend com FastAPI:

```bash
uvicorn app.main:app --reload
```

4. Acesse a aplicação no navegador:

```
http://localhost:8000
```

---

## 📂 Estrutura relevante de arquivos

```
avaliacoes/
└── produtos/
    └── mel/
        └── [etapa_nome_hash.json]

indexes/
└── mel/
    ├── pac_contexto.index
    ├── pac_contexto.pkl
    ├── bpf_etapa.index
    └── bpf_etapa.pkl
```