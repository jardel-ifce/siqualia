"""
CLASSIFICADOR DE PROBABILIDADE DE FALHAS - PRODUÇÃO DE MEL
===========================================================
Script principal focado nas 5 responsabilidades essenciais:
1. Escolha e carregamento da base de dados
2. Treinamento/Validação  
3. Teste
4. Exibição de Resultados
5. Mostrar gráficos/superfície de decisão
"""

import pandas as pd
import joblib
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import warnings
warnings.filterwarnings('ignore')

# Classes de probabilidade
CLASSES = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']

def carregar_dataset():
    """1. CARREGAMENTO DA BASE DE DADOS - ENVASE E ROTULAGEM"""
    print("🍯 CLASSIFICADOR DE MEL - Envase e Rotulagem")
    print("=" * 60)
    
    # Determinar caminho absoluto baseado na localização do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    caminho = os.path.join(ml_dir, "dataset", "mel", "envase_rotulagem", "dataset_envase_rotulagem.csv")
    nome = "Envase e Rotulagem"
    
    # Verificar se arquivo existe
    if not os.path.exists(caminho):
        print(f"❌ Dataset não encontrado: {caminho}")
        print("\n🔧 Gerando dataset...")
        try:
            # Adicionar view_generators ao path
            view_generators_path = os.path.join(ml_dir, "view_generators")
            if view_generators_path not in sys.path:
                sys.path.insert(0, view_generators_path)
            
            from view_generators.dataset_generator import gerar_dataset_por_tipo
            caminho, _ = gerar_dataset_por_tipo('envase_rotulagem', 1500)
            nome = "Envase e Rotulagem (Gerado)"
        except Exception as e:
            print(f"❌ Erro ao gerar dataset: {e}")
            return None, None
    
    # Carregar dataset
    try:
        df = pd.read_csv(caminho)
        print(f"✅ Dataset carregado: {nome}")
        print(f"📊 {len(df)} amostras, {len(df.columns)-1} atributos")
        
        # Verificar se tem coluna target
        if 'probabilidade' not in df.columns:
            print("❌ Coluna 'probabilidade' não encontrada no dataset")
            return None, None
            
        return df, nome
        
    except Exception as e:
        print(f"❌ Erro ao carregar dataset: {e}")
        return None, None


def escolher_algoritmo():
    """Permite ao usuário escolher o algoritmo de ML"""
    print("\n🤖 ESCOLHA DO ALGORITMO DE MACHINE LEARNING")
    print("=" * 50)
    
    algoritmos = {
        '1': {
            'nome': 'Random Forest',
            'modelo': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            ),
            'descricao': 'Ensemble de árvores de decisão (Recomendado)'
        },
        '2': {
            'nome': 'Gradient Boosting',
            'modelo': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            ),
            'descricao': 'Boosting sequencial de modelos fracos'
        },
        '3': {
            'nome': 'SVM',
            'modelo': SVC(
                C=1.0,
                kernel='linear',
                random_state=42,
                probability=True
            ),
            'descricao': 'Support Vector Machine com kernel Linear'
        },
        '4': {
            'nome': 'Regressão Logística',
            'modelo': LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class='ovr'
            ),
            'descricao': 'Modelo linear para classificação'
        },
        '5': {
            'nome': 'Naive Bayes',
            'modelo': GaussianNB(),
            'descricao': 'Classificador probabilístico baseado em Bayes'
        }
    }
    
    print("Algoritmos disponíveis:")
    for key, info in algoritmos.items():
        print(f"{key}. {info['nome']:<20} - {info['descricao']}")
    
    while True:
        escolha = input(f"\nEscolha um algoritmo (1-5): ").strip()
        
        if escolha in algoritmos:
            algoritmo_info = algoritmos[escolha]
            print(f"\n✅ Algoritmo selecionado: {algoritmo_info['nome']}")
            return algoritmo_info['modelo'], algoritmo_info['nome']
        else:
            print("❌ Opção inválida! Digite um número de 1 a 5.")

def treinar_validar_modelo(X_train, y_train, modelo, nome_algoritmo):
    """2. TREINAMENTO/VALIDAÇÃO"""
    print("\n🤖 TREINAMENTO DO MODELO")
    print("=" * 30)
    
    print(f"🔧 Treinando {nome_algoritmo}...")
    modelo.fit(X_train, y_train)
    
    # Validação cruzada simples
    from sklearn.model_selection import cross_val_score
    cv_scores = cross_val_score(modelo, X_train, y_train, cv=5)
    
    print(f"✅ Modelo treinado")
    print(f"📊 Validação cruzada: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    return modelo


def testar_modelo(modelo, X_test, y_test):
    """3. TESTE"""
    print("\n🎯 TESTE DO MODELO")
    print("=" * 20)
    
    # Fazer predições
    y_pred = modelo.predict(X_test)
    
    # Calcular métricas
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"🎯 Acurácia: {accuracy:.3f}")
    
    return y_pred, accuracy


def exibir_resultados(y_test, y_pred, accuracy, modelo, nome_algoritmo):
    """4. EXIBIÇÃO DE RESULTADOS"""
    print("\n📋 RESULTADOS DETALHADOS")
    print("=" * 40)
    
    print(f"\n🤖 Classificador: {nome_algoritmo}")
    
    # Mostrar parâmetros específicos do modelo
    if isinstance(modelo, RandomForestClassifier):
        print(f"   - Estimadores: {modelo.n_estimators}")
        print(f"   - Max Depth: {modelo.max_depth}")
        print(f"   - Min Samples Split: {modelo.min_samples_split}")
    elif isinstance(modelo, GradientBoostingClassifier):
        print(f"   - Estimadores: {modelo.n_estimators}")
        print(f"   - Max Depth: {modelo.max_depth}")
        print(f"   - Learning Rate: {modelo.learning_rate}")
    elif isinstance(modelo, SVC):
        print(f"   - Kernel: {modelo.kernel}")
        print(f"   - C: {modelo.C}")
        print(f"   - Gamma: {modelo.gamma}")
    elif isinstance(modelo, LogisticRegression):
        print(f"   - Max Iterations: {modelo.max_iter}")
        print(f"   - Multi Class: {modelo.multi_class}")
    elif isinstance(modelo, GaussianNB):
        print(f"   - Var Smoothing: {modelo.var_smoothing}")
    
    print(f"\n🎯 Acurácia Geral: {accuracy:.1%}")
    
    # Relatório de classificação
    print(f"\n📊 Métricas por Classe:")
    print(classification_report(y_test, y_pred, target_names=CLASSES))
    
    # Matriz de confusão
    print(f"\n🔍 Matriz de Confusão:")
    cm = confusion_matrix(y_test, y_pred)
    
    print("       Predito →")
    print("Real ↓  ", end="")
    for classe in ['DESP', 'BAIX', 'MED', 'ALTA']:
        print(f"{classe:>6}", end="")
    print()
    
    class_labels = ['DESP', 'BAIX', 'MED', 'ALTA']
    for i, row in enumerate(cm):
        print(f"{class_labels[i]:<6} ", end="")
        for val in row:
            print(f"{val:>6}", end="")
        print()




def salvar_resultados_treinamento(y_test, y_pred, accuracy, nome_dataset):
    """Salva os resultados do treinamento em arquivo texto"""
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    
    # Determinar subpasta baseada no nome do dataset
    subpasta = "envase_rotulagem"
    
    # Criar pasta se não existir (caminho absoluto)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    pasta_results = os.path.join(ml_dir, "results", subpasta)
    os.makedirs(pasta_results, exist_ok=True)
    
    # Criar relatório de resultados
    nome_arquivo = f"resultados_treinamento_{nome_dataset.lower().replace(' ', '_')}_{timestamp}.txt"
    caminho_arquivo = os.path.join(pasta_results, nome_arquivo)
    
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"RESULTADOS DO TREINAMENTO - {nome_dataset.upper()}\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Dataset: {nome_dataset}\n\n")
        f.write(f"CLASSIFICADOR UTILIZADO:\n")
        f.write(f"- Algoritmo: Random Forest\n")
        f.write(f"- Estimadores: 100\n")
        f.write(f"- Max Depth: 10\n")
        f.write(f"- Min Samples Split: 5\n")
        f.write(f"- Random State: 42\n\n")
        f.write(f"RESULTADOS:\n")
        f.write(f"Acurácia: {accuracy:.1%}\n\n")
        
        # Relatório de classificação
        f.write("MÉTRICAS POR CLASSE:\n")
        f.write("-" * 30 + "\n")
        from sklearn.metrics import classification_report
        report = classification_report(y_test, y_pred, target_names=CLASSES)
        f.write(report + "\n\n")
        
        # Matriz de confusão
        f.write("MATRIZ DE CONFUSÃO:\n")
        f.write("-" * 20 + "\n")
        from sklearn.metrics import confusion_matrix
        cm = confusion_matrix(y_test, y_pred)
        
        f.write("       Predito →\n")
        f.write("Real ↓  ")
        for classe in ['DESP', 'BAIX', 'MED', 'ALTA']:
            f.write(f"{classe:>6}")
        f.write("\n")
        
        class_labels = ['DESP', 'BAIX', 'MED', 'ALTA']
        for i, row in enumerate(cm):
            f.write(f"{class_labels[i]:<6} ")
            for val in row:
                f.write(f"{val:>6}")
            f.write("\n")
    
    print(f"📋 Resultados salvos: {caminho_arquivo}")
    return caminho_arquivo


def salvar_modelo_final(modelo, scaler, nome_dataset):
    """Salva o modelo treinado na subpasta apropriada"""
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    
    # Determinar subpasta baseada no nome do dataset
    subpasta = "envase_rotulagem"
    
    # Criar pasta se não existir (caminho absoluto)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    pasta_modelo = os.path.join(ml_dir, "models", subpasta)
    os.makedirs(pasta_modelo, exist_ok=True)
    
    # Salvar modelo
    modelo_path = f"{pasta_modelo}/classificador_mel_{timestamp}.pkl"
    joblib.dump(modelo, modelo_path)
    
    # Salvar scaler
    scaler_path = f"{pasta_modelo}/scaler_mel_{timestamp}.pkl"
    joblib.dump(scaler, scaler_path)
    
    # Salvar configuração
    config = {
        'dataset_usado': nome_dataset,
        'timestamp': timestamp,
        'classes': CLASSES,
        'modelo_path': modelo_path,
        'scaler_path': scaler_path,
        'etapa': subpasta
    }
    
    import json
    config_path = f"{pasta_modelo}/config_classificador_{timestamp}.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 MODELO SALVO em {subpasta}:")
    print(f"  📁 Modelo: {modelo_path}")
    print(f"  📁 Scaler: {scaler_path}")
    print(f"  📁 Config: {config_path}")
    
    return modelo_path, scaler_path, config_path


def main():
    """Função principal - Pipeline das 5 responsabilidades"""
    print("🍯 CLASSIFICADOR DE PROBABILIDADE DE FALHAS - MEL")
    print("=" * 60)
    print("Sistema focado nas 5 responsabilidades essenciais\n")
    
    # 1. CARREGAMENTO DA BASE DE DADOS
    df, nome_dataset = carregar_dataset()
    
    if df is None:
        return
    
    # Preparar dados
    X = df.drop('probabilidade', axis=1)
    y = df['probabilidade']
    
    print(f"\n🔧 Preparando dados...")
    print(f"📊 Features: {list(X.columns)}")
    print(f"🎯 Classes: {CLASSES}")
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Normalizar
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"✅ Divisão: {len(X_train)} treino, {len(X_test)} teste")
    
    # 1.5. ESCOLHA DO ALGORITMO
    modelo, nome_algoritmo = escolher_algoritmo()
    
    # 2. TREINAMENTO/VALIDAÇÃO
    modelo = treinar_validar_modelo(X_train_scaled, y_train, modelo, nome_algoritmo)
    
    # 3. TESTE
    y_pred, accuracy = testar_modelo(modelo, X_test_scaled, y_test)
    
    # 4. EXIBIÇÃO DE RESULTADOS
    exibir_resultados(y_test, y_pred, accuracy, modelo, nome_algoritmo)
    
    # 5. MOSTRAR GRÁFICOS E ANÁLISES
    try:
        import sys
        # Adicionar view_generators ao path
        ml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        view_generators_path = os.path.join(ml_dir, "view_generators")
        if view_generators_path not in sys.path:
            sys.path.insert(0, view_generators_path)
        
        from graphic_results import mostrar_graficos_resultados
        caminho_graficos = mostrar_graficos_resultados(modelo, X, y, X_test_scaled, y_test, nome_dataset)
    except ImportError as e:
        print(f"❌ Erro ao importar graphic_results: {e}")
        caminho_graficos = "Gráficos não disponíveis"
    except Exception as e:
        print(f"❌ Erro ao gerar gráficos: {e}")
        caminho_graficos = "Erro na geração de gráficos"
    
    # Salvar resultados do treinamento
    caminho_resultados = salvar_resultados_treinamento(y_test, y_pred, accuracy, nome_dataset)
    
    # Salvar modelo
    salvar_modelo_final(modelo, scaler, nome_dataset)
    
    print(f"\n✅ CLASSIFICAÇÃO CONCLUÍDA COM SUCESSO!")
    print(f"🎯 Acurácia final: {accuracy:.1%}")
    print(f"📊 Gráficos: {caminho_graficos}")
    print(f"📋 Resultados: {caminho_resultados}")
    
    print(f"\n👋 Sistema finalizado com sucesso!")


if __name__ == "__main__":
    main()