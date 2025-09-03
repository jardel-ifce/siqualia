"""
GERADOR DE GRÁFICOS E ANÁLISES VISUAIS
====================================
Módulo responsável por gerar todas as visualizações dos resultados
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from sklearn.metrics import confusion_matrix

# Classes de probabilidade
CLASSES = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']

def mostrar_graficos_resultados(modelo, X, y, X_test, y_test, nome_dataset):
    """Gera e exibe gráficos dos resultados do classificador"""
    print(f"\n📊 GRÁFICOS E ANÁLISES")
    print("=" * 30)
    
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle(f'Análise do Classificador - {nome_dataset}', fontsize=16, fontweight='bold')
    
    # 1. Importância das Features / Coeficientes
    if hasattr(modelo, 'feature_importances_'):
        # Para Random Forest, Gradient Boosting
        importances = modelo.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        # Top 10 features
        top_n = min(10, len(importances))
        top_indices = indices[:top_n]
        
        axes[0, 0].bar(range(top_n), importances[top_indices])
        axes[0, 0].set_title('Top 10 Features Mais Importantes')
        axes[0, 0].set_ylabel('Importância')
        axes[0, 0].set_xticks(range(top_n))
        axes[0, 0].set_xticklabels([X.columns[i] for i in top_indices], rotation=45, ha='right')
        
        print(f"🎯 Top 5 Features Mais Importantes:")
        for i in range(min(5, top_n)):
            idx = top_indices[i]
            print(f"  {X.columns[idx]:<25}: {importances[idx]:.4f}")
            
    elif hasattr(modelo, 'coef_'):
        # Para Regressão Logística, SVM Linear
        if len(modelo.coef_.shape) > 1:
            # Multi-class: usar média dos coeficientes absolutos
            importances = np.mean(np.abs(modelo.coef_), axis=0)
        else:
            # Binary: usar coeficientes absolutos
            importances = np.abs(modelo.coef_[0])
            
        indices = np.argsort(importances)[::-1]
        top_n = min(10, len(importances))
        top_indices = indices[:top_n]
        
        axes[0, 0].bar(range(top_n), importances[top_indices])
        axes[0, 0].set_title('Top 10 Features por Coeficientes')
        axes[0, 0].set_ylabel('|Coeficiente|')
        axes[0, 0].set_xticks(range(top_n))
        axes[0, 0].set_xticklabels([X.columns[i] for i in top_indices], rotation=45, ha='right')
        
        print(f"🎯 Top 5 Features por Coeficientes:")
        for i in range(min(5, top_n)):
            idx = top_indices[i]
            print(f"  {X.columns[idx]:<25}: {importances[idx]:.4f}")
            
    else:
        # Para modelos sem feature importance (SVM RBF, Naive Bayes, etc.)
        axes[0, 0].text(0.5, 0.5, f'Importância de Features\nnão disponível para\n{type(modelo).__name__}', 
                       ha='center', va='center', transform=axes[0, 0].transAxes,
                       fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        axes[0, 0].set_title('Importância das Features')
        axes[0, 0].set_xticks([])
        axes[0, 0].set_yticks([])
        
        print(f"ℹ️  Importância de features não disponível para {type(modelo).__name__}")
    
    # 2. Distribuição das Classes (Teste)
    y_pred = modelo.predict(X_test)
    unique, counts = np.unique(y_test, return_counts=True)
    
    axes[0, 1].bar([CLASSES[i] for i in unique], counts, alpha=0.7, color=['green', 'yellow', 'orange', 'red'])
    axes[0, 1].set_title('Distribuição Real das Classes (Teste)')
    axes[0, 1].set_ylabel('Quantidade')
    
    for i, v in enumerate(counts):
        axes[0, 1].text(i, v + 1, str(v), ha='center', fontweight='bold')
    
    # 3. Distribuição das Predições vs Real
    y_pred_plot = modelo.predict(X_test)
    
    # Contar predições por classe
    unique_pred, counts_pred = np.unique(y_pred_plot, return_counts=True)
    
    axes[1, 0].bar([CLASSES[i] for i in unique_pred], counts_pred, 
                  alpha=0.7, color=['lightgreen', 'lightyellow', 'lightcoral', 'lightblue'])
    axes[1, 0].set_title('Distribuição das Predições (Teste)')
    axes[1, 0].set_ylabel('Quantidade')
    
    for i, v in enumerate(counts_pred):
        axes[1, 0].text(i, v + 1, str(v), ha='center', fontweight='bold')
    
    # 4. Matriz de Confusão Heatmap
    cm = confusion_matrix(y_test, y_pred)
    
    axes[1, 1].imshow(cm, interpolation='nearest', cmap='Blues')
    axes[1, 1].set_title('Matriz de Confusão')
    
    tick_marks = np.arange(len(CLASSES))
    axes[1, 1].set_xticks(tick_marks)
    axes[1, 1].set_yticks(tick_marks)
    axes[1, 1].set_xticklabels(CLASSES, rotation=45)
    axes[1, 1].set_yticklabels(CLASSES)
    
    # Adicionar valores na matriz
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            axes[1, 1].text(j, i, format(cm[i, j], 'd'),
                           horizontalalignment="center",
                           color="white" if cm[i, j] > thresh else "black")
    
    axes[1, 1].set_ylabel('Classe Real')
    axes[1, 1].set_xlabel('Classe Predita')
    
    plt.tight_layout()
    
    # Determinar caminho absoluto correto
    subpasta = "envase_rotulagem"
    pasta_results = "/Users/jardelrodrigues/Desktop/siqualia-ia-main/ml/results/envase_rotulagem"
    os.makedirs(pasta_results, exist_ok=True)
    
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"classificador_resultados_{nome_dataset.lower().replace(' ', '_')}_{timestamp}.png"
    caminho_salvar = os.path.join(pasta_results, nome_arquivo)
    plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
    
    print(f"📊 Gráficos salvos: {caminho_salvar}")
    
    plt.show()
    
    return caminho_salvar

def gerar_grafico_comparativo_modelos(resultados_modelos, nome_dataset):
    """Gera gráfico comparativo entre diferentes modelos"""
    if not resultados_modelos:
        print("❌ Nenhum resultado de modelo para comparar")
        return None
    
    print(f"\n📊 GRÁFICO COMPARATIVO DE MODELOS")
    print("=" * 40)
    
    modelos = list(resultados_modelos.keys())
    accuracies = [resultados_modelos[modelo]['accuracy'] for modelo in modelos]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(modelos, accuracies, alpha=0.7, color=['skyblue', 'lightgreen', 'coral', 'gold'])
    plt.title(f'Comparativo de Acurácia - {nome_dataset}', fontsize=14, fontweight='bold')
    plt.ylabel('Acurácia (%)')
    plt.ylim(0, 1)
    
    # Adicionar valores nas barras
    for bar, acc in zip(bars, accuracies):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{acc:.1%}', ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Salvar gráfico
    subpasta = "envase_rotulagem"
    pasta_results = "/Users/jardelrodrigues/Desktop/siqualia-ia-main/ml/results/envase_rotulagem"
    os.makedirs(pasta_results, exist_ok=True)
    
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"comparativo_modelos_{nome_dataset.lower().replace(' ', '_')}_{timestamp}.png"
    caminho_salvar = os.path.join(pasta_results, nome_arquivo)
    plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
    
    print(f"📊 Gráfico comparativo salvo: {caminho_salvar}")
    
    plt.show()
    
    return caminho_salvar

def gerar_grafico_matriz_confusao_detalhada(y_test, y_pred, nome_dataset):
    """Gera matriz de confusão detalhada com métricas por classe"""
    from sklearn.metrics import classification_report, confusion_matrix
    
    print(f"\n📊 MATRIZ DE CONFUSÃO DETALHADA")
    print("=" * 35)
    
    cm = confusion_matrix(y_test, y_pred)
    
    # Criar figura com subplot maior
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle(f'Análise Detalhada - {nome_dataset}', fontsize=16, fontweight='bold')
    
    # Matriz de confusão
    im = ax1.imshow(cm, interpolation='nearest', cmap='Blues')
    ax1.set_title('Matriz de Confusão')
    
    tick_marks = np.arange(len(CLASSES))
    ax1.set_xticks(tick_marks)
    ax1.set_yticks(tick_marks)
    ax1.set_xticklabels(CLASSES, rotation=45)
    ax1.set_yticklabels(CLASSES)
    
    # Adicionar valores
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax1.text(j, i, format(cm[i, j], 'd'),
                    horizontalalignment="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontweight='bold')
    
    ax1.set_ylabel('Classe Real')
    ax1.set_xlabel('Classe Predita')
    
    # Relatório de classificação como heatmap
    report = classification_report(y_test, y_pred, target_names=CLASSES, output_dict=True)
    
    # Extrair métricas principais
    classes_metrics = []
    for classe in CLASSES:
        if classe in report:
            classes_metrics.append([
                report[classe]['precision'],
                report[classe]['recall'],
                report[classe]['f1-score']
            ])
    
    metrics_array = np.array(classes_metrics)
    
    im2 = ax2.imshow(metrics_array.T, interpolation='nearest', cmap='Greens', aspect='auto')
    ax2.set_title('Métricas por Classe')
    ax2.set_xticks(range(len(CLASSES)))
    ax2.set_yticks(range(3))
    ax2.set_xticklabels(CLASSES, rotation=45)
    ax2.set_yticklabels(['Precision', 'Recall', 'F1-Score'])
    
    # Adicionar valores nas métricas
    for i in range(3):
        for j in range(len(CLASSES)):
            ax2.text(j, i, f'{metrics_array[j, i]:.3f}',
                    ha='center', va='center', fontweight='bold')
    
    plt.tight_layout()
    
    # Salvar gráfico
    subpasta = "envase_rotulagem"
    pasta_results = "/Users/jardelrodrigues/Desktop/siqualia-ia-main/ml/results/envase_rotulagem"
    os.makedirs(pasta_results, exist_ok=True)
    
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"matriz_confusao_detalhada_{nome_dataset.lower().replace(' ', '_')}_{timestamp}.png"
    caminho_salvar = os.path.join(pasta_results, nome_arquivo)
    plt.savefig(caminho_salvar, dpi=300, bbox_inches='tight')
    
    print(f"📊 Matriz detalhada salva: {caminho_salvar}")
    
    plt.show()
    
    return caminho_salvar