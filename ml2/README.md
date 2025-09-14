# 🤖 ML - Machine Learning para SIQUALIA

## 📂 Estrutura das Pastas

```
ml/
├── dataset/                    # Datasets organizados por produto e etapa
│   └── mel/
│       └── envase_rotulagem/
│           └── dataset_envase_rotulagem.csv
├── models/                     # Modelos treinados (.pkl) e configurações
│   └── envase_rotulagem/
│       ├── classificador_mel_*.pkl
│       ├── scaler_mel_*.pkl
│       └── config_classificador_*.json
├── scripts/                    # Scripts de ML e predição
│   └── envase_rotulagem/
│       ├── classificador_mel.py
│       └── predicao_mel.py
├── results/                    # Resultados de treinamento
│   └── envase_rotulagem/
├── results_trained_models/     # Resultados de predições
│   └── envase_rotulagem/
├── view_generators/            # Geradores de análises
│   ├── analysis_generator.py
│   ├── dataset_generator.py
│   ├── graphic_results.py
│   └── report_generator.py
├── reset.py                   # Script de reset do ambiente
├── reset.sh                   # Script de reset (shell)
└── RESET_README.md           # Documentação de reset
```

## 📊 Datasets Disponíveis

### Mel - Envase e Rotulagem
- **Arquivo**: `dataset/mel/envase_rotulagem/dataset_envase_rotulagem.csv`
- **Amostras**: ~1.400 registros
- **Features**: 20 atributos + 1 target (probabilidade)
- **Target**: Probabilidade contínua de risco (0.0 - 100.0)
- **Formato**: Dados reais de processo produtivo

#### Atributos do Dataset:

**Qualidade da Embalagem:**
1. `tipo_embalagem` - Tipo da embalagem utilizada
2. `estado_embalagem` - Estado/condição da embalagem
3. `tampa_correta` - Adequação da tampa
4. `vedacao_adequada` - Qualidade da vedação

**Processos e Higienização:**
5. `higienizacao_previa` - Higienização prévia realizada
6. `uso_epi` - Uso de equipamentos de proteção individual
7. `local_envase` - Local onde ocorre o envase
8. `manipulador_higiene` - Nível de higiene do manipulador

**Características do Produto:**
9. `aspecto_visual` - Aspecto visual do mel
10. `umidade_mel` - Nível de umidade do mel
11. `temperatura_envase` - Temperatura durante o envase
12. `cristalizacao` - Estado de cristalização do mel

**Controle de Qualidade:**
13. `rotulo_presente` - Presença do rótulo
14. `informacoes_completas` - Completude das informações
15. `data_validade_legivel` - Legibilidade da data de validade
16. `lote_identificado` - Identificação do lote
17. `registro_lote` - Registro adequado do lote

**Gestão e Processos:**
18. `treinamento_equipe` - Nível de treinamento da equipe
19. `historico_reclamacoes` - Histórico de reclamações
20. `tempo_exposicao_ar` - Tempo de exposição ao ar
21. `probabilidade` - **TARGET**: Probabilidade de risco (valor contínuo)

## 🚀 Como Usar

### 1. Carregar Dataset
```python
import pandas as pd

# Carregar dataset
df = pd.read_csv('ml/dataset/mel/envase_rotulagem/dataset_envase_rotulagem.csv')

# Separar features e target
X = df.drop('probabilidade', axis=1)
y = df['probabilidade']
```

### 2. Treinar Modelos
```bash
# Navegar para diretório
cd ml/scripts/envase_rotulagem/

# Executar treinamento
python classificador_mel.py
```

### 3. Fazer Predições
```bash
# Executar predições com modelo treinado
python predicao_mel.py
```

### 4. Reset do Ambiente
```bash
# Limpar modelos e resultados
cd ml/
./reset.sh

# Ou usar o script Python
python reset.py
```

### 5. Carregar Modelos Treinados
```python
import joblib

# Carregar modelo
modelo = joblib.load('ml/models/envase_rotulagem/classificador_mel_*.pkl')

# Carregar scaler
scaler = joblib.load('ml/models/envase_rotulagem/scaler_mel_*.pkl')
```

## 📈 Características do Dataset

- **Target Contínuo**: Probabilidade de risco de 0.0 a ~100.0
- **Distribuição**: Valores concentrados em diferentes faixas de risco
- **Tipo de Problema**: Regressão (predição de probabilidade contínua)
- **Amostras**: ~1.400 registros de processos reais

## 🔄 Expansão Futura

### Novos Produtos
```
ml/dataset/
├── mel/
│   ├── envase_rotulagem/
│   ├── armazenamento/
│   └── transporte/
├── leite/
│   ├── pasteurizacao/
│   └── homogeneizacao/
└── queijo/
    ├── coagulacao/
    └── maturacao/
```

### Novos Modelos
- Modelos específicos por etapa produtiva
- Ensemble methods para melhor precisão
- Deep Learning para casos complexos
- Modelos de series temporais para monitoramento contínuo

## 🛠️ Scripts Disponíveis

1. **`classificador_mel.py`** - Script de treinamento de modelos
2. **`predicao_mel.py`** - Script para fazer predições
3. **`reset.py`** - Limpeza do ambiente ML
4. **`reset.sh`** - Script shell de reset

## 📊 Modelos Implementados

- **Random Forest Regressor**: Ensemble de árvores de decisão
- **Gradient Boosting Regressor**: Boosting sequencial
- **Support Vector Regressor (SVR)**: Máquina de vetores de suporte
- **Gaussian Naive Bayes**: Classificador probabilístico (para classes discretas)

## 📈 Performance Esperada

- **R² Score**: ~0.70-0.85 (regressão)
- **MAE (Mean Absolute Error)**: ~5-10 pontos de probabilidade
- **RMSE**: ~8-15 pontos de probabilidade
- **Precisão na Classificação**: ~75-85% (para faixas de risco)

## 🔧 Dependências

Principais bibliotecas utilizadas:
- **pandas**: Manipulação de dados
- **numpy**: Computação numérica
- **scikit-learn**: Machine learning
- **matplotlib**: Visualizações
- **seaborn**: Visualizações estatísticas
- **joblib**: Serialização de modelos

## 📁 Arquivos Gerados

### Modelos Treinados
- `classificador_mel_[timestamp].pkl` - Modelo treinado
- `scaler_mel_[timestamp].pkl` - Normalizador de dados
- `config_classificador_[timestamp].json` - Configurações do modelo

### Resultados
- `resultados_treinamento_[timestamp].txt` - Métricas de treinamento
- `classificador_resultados_[timestamp].png` - Gráficos de performance
- `predicao_[modelo]_[timestamp].txt` - Resultados de predições

## 🎯 Casos de Uso

1. **Predição em Tempo Real**: Avaliar risco durante o processo
2. **Análise Histórica**: Identificar padrões em dados passados
3. **Otimização de Processo**: Ajustar parâmetros para reduzir riscos
4. **Controle de Qualidade**: Validação automática de lotes
5. **Auditoria**: Relatórios de conformidade e não-conformidades