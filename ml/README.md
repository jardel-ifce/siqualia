# 🤖 ML - Machine Learning para SIQUALIA

## 📂 Estrutura das Pastas

```
ml/
├── dataset/           # Datasets organizados por produto e etapa
│   └── mel/
│       └── filtragem_e_clarificacao/
│           └── dataset_filtragem_mel.csv
├── models/            # Modelos treinados (.pkl, .joblib)
└── scripts/           # Scripts de ML e notebooks
    ├── classificador_risco_mel.py
    ├── classificador_risco_mel.md
    └── classificador_risco_mel.ipynb
```

## 📊 Datasets Disponíveis

### Mel - Filtragem e Clarificação
- **Arquivo**: `dataset/mel/filtragem_e_clarificacao/dataset_filtragem_mel.csv`
- **Amostras**: 1.500 registros
- **Features**: 18 atributos + 1 target (risco)
- **Classes**: 0=BAIXO, 1=MÉDIO, 2=ALTO
- **Formato**: Similar ao dataset Iris

#### Atributos do Dataset:
1. `temperatura_processo` - Temperatura durante processamento (°C)
2. `umidade_relativa` - Umidade do ambiente (%)
3. `pH_mel` - Acidez do mel
4. `tempo_exposicao` - Tempo de exposição ao ar (min)
5. `temperatura_armazenamento` - Temperatura de estocagem (°C)
6. `contagem_microbiana` - UFC inicial estimada (UFC/g)
7. `atividade_agua` - Água disponível (aw)
8. `hidroximetilfurfural` - HMF, indicador de aquecimento (mg/kg)
9. `tipo_embalagem` - Tipo de embalagem (1=Metal, 2=Plástico, 3=Vidro)
10. `higiene_manipulador` - Nível de higiene (1-4)
11. `condicao_equipamento` - Condição dos equipamentos (1-4)
12. `controle_pragas` - Nível de controle de pragas (1-4)
13. `fonte_agua` - Tipo de água utilizada (1-3)
14. `filtrado` - Mel foi filtrado (0/1)
15. `pasteurizado` - Passou por pasteurização (0/1)
16. `certificacao_organica` - Possui certificação (0/1)
17. `uso_antibioticos` - Uso de antibióticos nas colmeias (0/1)
18. `rastreabilidade` - Sistema de rastreamento (0/1)
19. `risco` - **TARGET**: Classe de risco (0/1/2)

## 🚀 Como Usar

### 1. Carregar Dataset
```python
import pandas as pd

# Carregar dataset
df = pd.read_csv('ml/dataset/mel/filtragem_e_clarificacao/dataset_filtragem_mel.csv')

# Separar features e target
X = df.drop('risco', axis=1)
y = df['risco']
```

### 2. Executar Classificador
```bash
# Ativar ambiente
source .venv/bin/activate

# Executar script
python ml/scripts/classificador_risco_mel.py

# Ou abrir notebook
jupyter notebook ml/scripts/classificador_risco_mel.ipynb
```

### 3. Salvar Modelos Treinados
```python
import joblib

# Salvar modelo
joblib.dump(modelo, 'ml/models/modelo_filtragem_mel.pkl')

# Carregar modelo
modelo = joblib.load('ml/models/modelo_filtragem_mel.pkl')
```

## 📈 Distribuição das Classes

- **BAIXO (0)**: 432 amostras (28.8%)
- **MÉDIO (1)**: 544 amostras (36.3%)
- **ALTO (2)**: 524 amostras (34.9%)

## 🔄 Expansão Futura

### Novos Produtos
```
ml/dataset/
├── mel/
│   ├── filtragem_e_clarificacao/
│   ├── envase_rotulagem/
│   └── armazenamento/
├── leite/
│   ├── pasteurizacao/
│   └── homogeneizacao/
└── queijo/
    ├── coagulacao/
    └── maturacao/
```

### Novos Modelos
- Modelos específicos por etapa
- Ensemble methods
- Deep Learning para casos complexos
- Modelos de series temporais

## 🛠️ Scripts Disponíveis

1. **`classificador_risco_mel.py`** - Script completo de classificação
2. **`classificador_risco_mel.md`** - Documentação técnica detalhada
3. **`classificador_risco_mel.ipynb`** - Notebook interativo para exploração

## 📊 Métricas Esperadas

- **Acurácia**: ~67-75%
- **Precisão**: ~70% (classe ALTO)
- **Recall**: ~75% (importante para segurança alimentar)
- **F1-Score**: ~70%

## 🔧 Dependências

Todas as dependências já estão instaladas no ambiente virtual:
- pandas
- numpy  
- scikit-learn
- matplotlib
- seaborn