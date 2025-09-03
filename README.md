# SIQUALIA – Sistema Inteligente de Qualidade Alimentar com IA

## 🧩 Visão Geral da Implementação

O SIQUALIA é um sistema completo que combina análise de segurança alimentar com inteligência artificial para produtos de mel. O sistema oferece duas funcionalidades principais:

1. **Assistente de Geração do Relatório APPCC** - Preenchimento semiautomático do Formulário I (Plano de Monitoramento de PCC) e geração do Relatório Final APPCC
2. **Sistema de Machine Learning** - Predição de riscos para processos de envase e rotulagem do mel

Atualmente implementado para o produto **mel**, integrando controle de qualidade tradicional com análise preditiva avançada.

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

## 🤖 Sistema de Machine Learning

### 📊 Modelos de Predição de Riscos

O sistema inclui modelos de machine learning para análise preditiva de riscos no processo de envase e rotulagem do mel:

#### 🎯 Atributos Analisados

O modelo utiliza **20 atributos** relacionados ao processo de envase e rotulagem:

**Qualidade da Embalagem:**
- `tipo_embalagem` - Tipo da embalagem utilizada
- `estado_embalagem` - Estado/condição da embalagem  
- `tampa_correta` - Adequação da tampa
- `vedacao_adequada` - Qualidade da vedação

**Processos e Higienização:**
- `higienizacao_previa` - Higienização prévia realizada
- `uso_epi` - Uso de equipamentos de proteção individual
- `local_envase` - Local onde ocorre o envase
- `manipulador_higiene` - Nível de higiene do manipulador

**Características do Produto:**
- `aspecto_visual` - Aspecto visual do mel
- `umidade_mel` - Nível de umidade do mel
- `temperatura_envase` - Temperatura durante o envase
- `cristalizacao` - Estado de cristalização do mel

**Controle de Qualidade:**
- `rotulo_presente` - Presença do rótulo
- `informacoes_completas` - Completude das informações
- `data_validade_legivel` - Legibilidade da data de validade
- `lote_identificado` - Identificação do lote
- `registro_lote` - Registro adequado do lote

**Gestão e Processos:**
- `treinamento_equipe` - Nível de treinamento da equipe
- `historico_reclamacoes` - Histórico de reclamações
- `tempo_exposicao_ar` - Tempo de exposição ao ar

#### 🔮 Predição de Probabilidade de Risco

O sistema prediz uma **probabilidade contínua de risco** baseada na análise dos 20 atributos, permitindo:
- Identificação proativa de possíveis problemas
- Otimização de processos de qualidade
- Redução de não-conformidades

### 📁 Estrutura do Módulo ML

```
ml/
├── dataset/mel/envase_rotulagem/          # Datasets de treinamento
├── models/envase_rotulagem/               # Modelos treinados (.pkl)
├── scripts/envase_rotulagem/              # Scripts de treinamento e predição
├── results/                               # Resultados de treinamento
├── results_trained_models/                # Resultados de predições
├── view_generators/                       # Geradores de análises e relatórios
└── RESET_README.md                        # Documentação do módulo ML
```

#### 🚀 Como Usar o Sistema ML

1. **Treinamento de Modelos:**
```bash
cd ml/scripts/envase_rotulagem/
python classificador_mel.py
```

2. **Predições:**
```bash
python predicao_mel.py
```

3. **Reset do Ambiente:**
```bash
cd ml/
./reset.sh
```

---

## ⚠️ Limitações atuais

**Sistema APPCC:**
* Não há controle contra duplicatas ou arquivos malformados
* O relatório ainda depende da integridade dos formulários G, H e I preenchidos manualmente

**Sistema ML:**
* Modelos específicos para processo de envase e rotulagem
* Requer dados históricos para melhor precisão

---

## 🛠 Melhorias planejadas

**Sistema APPCC:**
* Implementar validações mais rígidas e alertas sobre preenchimento incompleto
* Melhorar layout e navegação entre os formulários

**Sistema ML:**
* Expandir modelos para outras etapas do processo produtivo
* Implementar sistema de feedback para melhoria contínua dos modelos
* Interface web para visualização de predições em tempo real

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

## 📂 Estrutura completa de arquivos

### Sistema APPCC
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

### Sistema Machine Learning
```bash
ml/
├── dataset/
│   └── mel/
│       └── envase_rotulagem/
│           └── dataset_envase_rotulagem.csv
├── models/
│   └── envase_rotulagem/
│       ├── classificador_mel_*.pkl
│       ├── scaler_mel_*.pkl
│       └── config_classificador_*.json
├── scripts/
│   └── envase_rotulagem/
│       ├── classificador_mel.py
│       └── predicao_mel.py
├── results/
│   └── envase_rotulagem/
│       ├── classificador_resultados_*.png
│       └── resultados_treinamento_*.txt
├── results_trained_models/
│   └── envase_rotulagem/
│       └── predicao_*.txt
├── view_generators/
│   ├── analysis_generator.py
│   ├── dataset_generator.py
│   ├── graphic_results.py
│   └── report_generator.py
├── reset.py
├── reset.sh
└── RESET_README.md
```