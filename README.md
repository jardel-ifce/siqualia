# SIQUALIA – Formulário I e Geração do Relatório APPCC

## 🧩 Visão Geral da Implementação

Esta versão do sistema SIQUALIA implementa o preenchimento semiautomático do **Formulário I** (Plano de Monitoramento de PCC) e a geração do **Relatório Final APPCC** para produtos alimentícios.

Atualmente, o fluxo está disponível para o produto **mel**, com base nos perigos classificados como **Pontos Críticos de Controle (PCC)** no Formulário H.

## 🧪 Preenchimento do Formulário I

O preenchimento do Formulário I segue a lógica:

- O botão **“I”** é exibido sempre que a etapa conter um perigo classificado como **PCC**.
- Ao clicar no botão “I”, o sistema:
  - Verifica se já há sugestão salva em `sessionStorage` para evitar repetição de chamada ao backend.
  - Caso **não haja sugestão anterior**, o sistema consulta o endpoint `/v1/formulario-i/sugerir`.
  - Este endpoint utiliza **busca semântica com FAISS + SentenceTransformer** para sugerir o preenchimento com base em documentos do produto.

> ⚠️ Importante: **A edição direta dos dados do Formulário I ainda não está implementada.** Apenas a exibição da sugestão gerada é possível nesta etapa do projeto.

## 📄 Geração do Relatório Final APPCC

- O botão **“Relatório”** é exibido apenas quando:
  - O perigo da etapa foi classificado como **PCC** no Formulário H;
  - O Formulário I está **preenchido** (todos os campos obrigatórios).
- O relatório consolida dados dos Formulários G, H e I, compondo o plano final de controle para a etapa.

## ⚠️ Limitações atuais

- A base de dados para sugestão automática do Formulário I está restrita ao produto **mel**.
- Ainda não há controle contra arquivos duplicados, inválidos ou incompletos.
- A verificação de integridade entre Formulários G, H e I será aprimorada em etapas futuras.
- O Formulário I **não pode ser editado** no frontend ainda — apenas visualizado e salvo (atualizando o json presente).

## 🛠 Melhorias planejadas

- Implementar edição interativa e salvamento do Formulário I via frontend.
- Expandir suporte para outros produtos além do mel (ex: queijo).
- Adicionar filtros de validação ao carregar arquivos e preencher formulários.
- Aprimorar a estrutura e layout do relatório final APPCC.

## ▶️ Como executar

1. Instale as dependências:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Execute o backend com FastAPI
```bash
uvicorn main:app --reload
```
3. Acesse a aplicação no navegador:
```bash
http://localhost:8000
```

## 📂 Estrutura relevante de arquivos
```pgsql
avaliacoes/
├── produtos/
    └── mel/
        └── [etapa_abc123.json]
indexes/
├── mel/
    ├── pac.index
    └── pac.pkl
```
