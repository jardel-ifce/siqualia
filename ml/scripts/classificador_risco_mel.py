import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

def gerar_dataset_mel(n_samples=1000):
    """
    Gera dataset sintético para classificação de riscos na produção de mel
    Similar ao dataset Iris mas com atributos específicos de produção alimentar
    """
    np.random.seed(42)
    data = []
    
    for i in range(n_samples):
        # Features numéricas contínuas
        temp_proc = np.random.uniform(15, 85)
        umidade = np.random.uniform(30, 90)
        pH = np.random.uniform(3.2, 6.5)
        tempo_exp = np.random.uniform(0, 240)
        temp_armaz = np.random.uniform(10, 40)
        contagem_micro = np.random.uniform(0, 10000)
        atividade_agua = np.random.uniform(0.4, 0.8)
        hmf = np.random.uniform(0, 100)
        
        # Features categóricas (já codificadas)
        tipo_embalagem = np.random.choice([1, 2, 3])
        higiene = np.random.choice([1, 2, 3, 4])
        cond_equip = np.random.choice([1, 2, 3, 4])
        controle_pragas = np.random.choice([1, 2, 3, 4])
        fonte_agua = np.random.choice([1, 2, 3])
        
        # Features binárias
        filtrado = np.random.choice([0, 1])
        pasteurizado = np.random.choice([0, 1])
        cert_organica = np.random.choice([0, 1])
        uso_antibio = np.random.choice([0, 1])
        rastreabilidade = np.random.choice([0, 1])
        
        # Calcular risco baseado em regras de negócio
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
            
        # Adicionar 10% de ruído para tornar mais realista
        if np.random.random() < 0.1:
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


def treinar_classificador(df):
    """
    Treina um classificador Random Forest para prever riscos
    """
    # Separar features e target
    X = df.drop('risco', axis=1)
    y = df['risco']
    
    # Dividir em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalizar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Criar e treinar modelo
    modelo = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    modelo.fit(X_train_scaled, y_train)
    
    # Fazer predições
    y_pred = modelo.predict(X_test_scaled)
    
    # Calcular métricas
    print("=" * 60)
    print("RELATÓRIO DE CLASSIFICAÇÃO - RISCOS NA PRODUÇÃO DE MEL")
    print("=" * 60)
    print("\n📊 Métricas por Classe:\n")
    print(classification_report(y_test, y_pred, 
          target_names=['BAIXO', 'MÉDIO', 'ALTO']))
    
    # Matriz de confusão
    print("\n🔍 Matriz de Confusão:")
    print("    Predito →")
    print("Real ↓  BAIXO  MÉDIO  ALTO")
    cm = confusion_matrix(y_test, y_pred)
    labels = ['BAIXO', 'MÉDIO', 'ALTO']
    for i, row in enumerate(cm):
        print(f"{labels[i]:6}", end="")
        for val in row:
            print(f"{val:7}", end="")
        print()
    
    # Cross-validation
    cv_scores = cross_val_score(modelo, X_train_scaled, y_train, cv=5)
    print(f"\n✅ Cross-validation Score (5-fold): {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': modelo.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🎯 Top 10 Features Mais Importantes:")
    print("-" * 40)
    for idx, row in feature_importance.head(10).iterrows():
        print(f"{row['feature']:30} {row['importance']:.4f}")
    
    return modelo, scaler, feature_importance


def prever_risco(modelo, scaler, amostra):
    """
    Faz predição para uma nova amostra
    """
    # Normalizar amostra
    amostra_scaled = scaler.transform([amostra])
    
    # Prever classe e probabilidades
    predicao = modelo.predict(amostra_scaled)[0]
    probabilidades = modelo.predict_proba(amostra_scaled)[0]
    
    classes = ['BAIXO', 'MÉDIO', 'ALTO']
    
    print("\n🔮 PREDIÇÃO PARA NOVA AMOSTRA:")
    print("-" * 40)
    print(f"Classe Predita: {classes[predicao]}")
    print("\nProbabilidades:")
    for i, classe in enumerate(classes):
        print(f"  {classe}: {probabilidades[i]:.2%}")
    
    return predicao, probabilidades


def analisar_distribuicao(df):
    """
    Analisa a distribuição do dataset
    """
    print("\n📈 ANÁLISE DO DATASET")
    print("=" * 60)
    print(f"Total de amostras: {len(df)}")
    print("\nDistribuição das classes de risco:")
    
    dist = df['risco'].value_counts().sort_index()
    labels = {0: 'BAIXO', 1: 'MÉDIO', 2: 'ALTO'}
    
    for risco, count in dist.items():
        pct = (count / len(df)) * 100
        print(f"  {labels[risco]:6}: {count:4} amostras ({pct:.1f}%)")
    
    print("\n📊 Estatísticas das Features Numéricas:")
    print("-" * 60)
    
    numeric_cols = ['temperatura_processo', 'pH_mel', 'contagem_microbiana', 
                   'atividade_agua', 'hidroximetilfurfural']
    
    for col in numeric_cols:
        print(f"\n{col}:")
        print(f"  Média: {df[col].mean():.2f}")
        print(f"  Desvio: {df[col].std():.2f}")
        print(f"  Min: {df[col].min():.2f}")
        print(f"  Max: {df[col].max():.2f}")


def main():
    """
    Função principal - executa todo o pipeline
    """
    print("\n" * 2)
    print("🍯 CLASSIFICADOR DE RISCOS - PRODUÇÃO DE MEL")
    print("=" * 60)
    print("Sistema de classificação similar ao dataset Iris")
    print("mas adaptado para segurança alimentar\n")
    
    # Gerar dataset
    print("📦 Gerando dataset sintético...")
    df = gerar_dataset_mel(1000)
    print(f"✓ Dataset criado com {len(df)} amostras e {len(df.columns)-1} features\n")
    
    # Analisar distribuição
    analisar_distribuicao(df)
    
    # Treinar classificador
    print("\n🤖 Treinando classificador Random Forest...")
    modelo, scaler, feature_importance = treinar_classificador(df)
    
    # Exemplo de predição para nova amostra
    print("\n" * 2)
    print("=" * 60)
    print("EXEMPLO DE PREDIÇÃO")
    print("=" * 60)
    
    # Criar uma amostra de teste (cenário de risco médio)
    nova_amostra = [
        45,    # temperatura_processo
        65,    # umidade_relativa
        4.2,   # pH_mel
        90,    # tempo_exposicao
        25,    # temperatura_armazenamento
        2500,  # contagem_microbiana
        0.55,  # atividade_agua
        35,    # hidroximetilfurfural
        2,     # tipo_embalagem
        3,     # higiene_manipulador
        3,     # condicao_equipamento
        3,     # controle_pragas
        2,     # fonte_agua
        1,     # filtrado
        0,     # pasteurizado
        1,     # certificacao_organica
        0,     # uso_antibioticos
        1      # rastreabilidade
    ]
    
    prever_risco(modelo, scaler, nova_amostra)
    
    print("\n" * 2)
    print("✅ Pipeline de classificação concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()