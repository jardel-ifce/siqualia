# 🍯 Classificador de Riscos - Produção de Mel

## 📊 Atributos Propostos para Classificação

### 1. **Atributos Numéricos Contínuos**
Similar ao Iris (sepal_length, petal_width, etc.), mas para produção de mel:

| Atributo | Descrição | Range | Unidade |
|----------|-----------|-------|---------|
| `temperatura_processo` | Temperatura durante processamento | 15-85 | °C |
| `umidade_relativa` | Umidade do ambiente | 30-90 | % |
| `pH_mel` | Acidez do mel | 3.2-6.5 | - |
| `tempo_exposicao` | Tempo de exposição ao ar | 0-240 | minutos |
| `temperatura_armazenamento` | Temperatura de estocagem | 10-40 | °C |
| `contagem_microbiana` | UFC inicial estimada | 0-10000 | UFC/g |
| `atividade_agua` | Água disponível (aw) | 0.4-0.8 | - |
| `hidroximetilfurfural` | HMF (indicador de aquecimento) | 0-100 | mg/kg |

### 2. **Atributos Categóricos Ordinais**
Convertidos para valores numéricos:

| Atributo | Valores | Codificação |
|----------|---------|-------------|
| `tipo_embalagem` | Vidro/Plástico/Metal | 3/2/1 |
| `higiene_manipulador` | Ótima/Boa/Regular/Ruim | 4/3/2/1 |
| `condicao_equipamento` | Nova/Boa/Usada/Antiga | 4/3/2/1 |
| `controle_pragas` | Completo/Parcial/Mínimo/Ausente | 4/3/2/1 |
| `fonte_agua` | Tratada/Poço/Natural | 3/2/1 |

### 3. **Atributos Binários**
| Atributo | Descrição | Valores |
|----------|-----------|---------|
| `filtrado` | Mel foi filtrado | 0/1 |
| `pasteurizado` | Passou por pasteurização | 0/1 |
| `certificacao_organica` | Possui certificação | 0/1 |
| `uso_antibioticos` | Antibióticos nas colmeias | 0/1 |
| `rastreabilidade` | Sistema de rastreamento | 0/1 |

## 🎯 Classes de Risco (Target)

```python
RISCO = {
    0: "BAIXO",   # Produto seguro, dentro dos padrões
    1: "MÉDIO",   # Requer atenção, alguns pontos de melhoria
    2: "ALTO"     # Crítico, fora dos padrões de segurança
}
```

## 📈 Regras de Negócio para Classificação

### RISCO ALTO
- `temperatura_processo` > 70°C OU < 20°C
- `pH_mel` < 3.5 OU > 6.0
- `contagem_microbiana` > 5000
- `higiene_manipulador` <= 2
- `hidroximetilfurfural` > 60

### RISCO MÉDIO
- `temperatura_processo` entre 60-70°C OU 20-30°C
- `umidade_relativa` > 70%
- `tempo_exposicao` > 120 min
- `atividade_agua` > 0.65
- `controle_pragas` <= 2

### RISCO BAIXO
- Todos os parâmetros dentro dos ranges ideais
- `certificacao_organica` = 1
- `rastreabilidade` = 1
- `higiene_manipulador` >= 3

## 🔬 Dataset Sintético - Exemplo

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Gerar dados mockados
np.random.seed(42)
n_samples = 1000

# Função para gerar dataset
def gerar_dataset_mel(n_samples=1000):
    data = []
    
    for i in range(n_samples):
        # Gerar features aleatórias com correlação ao risco
        temp_proc = np.random.uniform(15, 85)
        umidade = np.random.uniform(30, 90)
        pH = np.random.uniform(3.2, 6.5)
        tempo_exp = np.random.uniform(0, 240)
        temp_armaz = np.random.uniform(10, 40)
        contagem_micro = np.random.uniform(0, 10000)
        atividade_agua = np.random.uniform(0.4, 0.8)
        hmf = np.random.uniform(0, 100)
        
        # Categóricas
        tipo_embalagem = np.random.choice([1, 2, 3])
        higiene = np.random.choice([1, 2, 3, 4])
        cond_equip = np.random.choice([1, 2, 3, 4])
        controle_pragas = np.random.choice([1, 2, 3, 4])
        fonte_agua = np.random.choice([1, 2, 3])
        
        # Binárias
        filtrado = np.random.choice([0, 1])
        pasteurizado = np.random.choice([0, 1])
        cert_organica = np.random.choice([0, 1])
        uso_antibio = np.random.choice([0, 1])
        rastreabilidade = np.random.choice([0, 1])
        
        # Calcular risco baseado em regras
        risco_score = 0
        
        # Regras para risco alto
        if temp_proc > 70 or temp_proc < 20:
            risco_score += 3
        if pH < 3.5 or pH > 6.0:
            risco_score += 3
        if contagem_micro > 5000:
            risco_score += 4
        if higiene <= 2:
            risco_score += 3
        if hmf > 60:
            risco_score += 3
            
        # Regras para risco médio
        if 60 <= temp_proc <= 70 or 20 <= temp_proc <= 30:
            risco_score += 1
        if umidade > 70:
            risco_score += 1
        if tempo_exp > 120:
            risco_score += 1
        if atividade_agua > 0.65:
            risco_score += 2
        if controle_pragas <= 2:
            risco_score += 1
            
        # Benefícios (reduz risco)
        if cert_organica == 1:
            risco_score -= 1
        if rastreabilidade == 1:
            risco_score -= 1
        if pasteurizado == 1:
            risco_score -= 2
        if higiene >= 3:
            risco_score -= 1
            
        # Classificar risco
        if risco_score >= 8:
            risco = 2  # ALTO
        elif risco_score >= 4:
            risco = 1  # MÉDIO
        else:
            risco = 0  # BAIXO
            
        # Adicionar ruído para tornar mais realista
        if np.random.random() < 0.1:  # 10% de ruído
            risco = np.random.choice([0, 1, 2])
            
        sample = {
            'temperatura_processo': temp_proc,
            'umidade_relativa': umidade,
            'pH_mel': pH,
            'tempo_exposicao': tempo_exp,
            'temperatura_armazenamento': temp_armaz,
            'contagem_microbiana': contagem_micro,
            'atividade_agua': atividade_agua,
            'hidroximetilfurfural': hmf,
            'tipo_embalagem': tipo_embalagem,
            'higiene_manipulador': higiene,
            'condicao_equipamento': cond_equip,
            'controle_pragas': controle_pragas,
            'fonte_agua': fonte_agua,
            'filtrado': filtrado,
            'pasteurizado': pasteurizado,
            'certificacao_organica': cert_organica,
            'uso_antibioticos': uso_antibio,
            'rastreabilidade': rastreabilidade,
            'risco': risco
        }
        
        data.append(sample)
    
    return pd.DataFrame(data)

# Criar dataset
df_mel = gerar_dataset_mel(1000)
```

## 🤖 Modelos de Classificação Sugeridos

### 1. **Random Forest** (Recomendado)
- Lida bem com features mistas
- Fornece importância das features
- Robusto a outliers

### 2. **XGBoost**
- Alta performance
- Bom para datasets desbalanceados
- Feature importance nativa

### 3. **SVM com RBF Kernel**
- Bom para separação não-linear
- Requer normalização

### 4. **Rede Neural Simples**
- Para padrões complexos
- Requer mais dados

## 📊 Exemplo de Implementação

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

# Preparar dados
X = df_mel.drop('risco', axis=1)
y = df_mel['risco']

# Dividir dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Normalizar features numéricas
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Treinar modelo
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    random_state=42
)
rf_model.fit(X_train_scaled, y_train)

# Avaliar
y_pred = rf_model.predict(X_test_scaled)
print(classification_report(y_test, y_pred, 
      target_names=['BAIXO', 'MÉDIO', 'ALTO']))

# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nTop 5 Features Mais Importantes:")
print(feature_importance.head())
```

## 🎯 Métricas de Avaliação

1. **Accuracy**: Overall correctness
2. **Precision**: Evitar falsos positivos (crítico para RISCO ALTO)
3. **Recall**: Detectar todos os casos de risco (segurança alimentar)
4. **F1-Score**: Balanço entre precision e recall
5. **Confusion Matrix**: Visualizar erros de classificação

## 📈 Estratégias de Melhoria

1. **Feature Engineering**
   - Criar features compostas (ex: índice_higiene_total)
   - Ratios entre variáveis

2. **Balanceamento de Classes**
   - SMOTE para oversampling
   - Class weights no modelo

3. **Ensemble Methods**
   - Voting classifier
   - Stacking com múltiplos modelos

4. **Validação Cruzada**
   - K-fold stratificado
   - Time series split se houver temporalidade

5. **Otimização de Hiperparâmetros**
   - GridSearchCV
   - RandomizedSearchCV
   - Optuna para busca bayesiana

## 🔄 Pipeline Completo

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Definir colunas por tipo
numeric_features = ['temperatura_processo', 'umidade_relativa', 'pH_mel', 
                   'tempo_exposicao', 'temperatura_armazenamento',
                   'contagem_microbiana', 'atividade_agua', 'hidroximetilfurfural']

categorical_features = ['tipo_embalagem', 'higiene_manipulador', 
                       'condicao_equipamento', 'controle_pragas', 'fonte_agua']

binary_features = ['filtrado', 'pasteurizado', 'certificacao_organica',
                  'uso_antibioticos', 'rastreabilidade']

# Preprocessador
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features),
        ('bin', 'passthrough', binary_features)
    ])

# Pipeline completo
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Treinar
pipeline.fit(X_train, y_train)

# Prever
y_pred = pipeline.predict(X_test)
```

## 📊 Visualizações Importantes

1. **Matriz de Correlação**: Identificar relações entre features
2. **Box plots**: Distribuição por classe de risco
3. **Feature Importance Plot**: Quais atributos mais influenciam
4. **Confusion Matrix Heatmap**: Erros de classificação
5. **ROC Curves**: Para cada classe (multiclass)
6. **Learning Curves**: Diagnóstico de overfitting/underfitting