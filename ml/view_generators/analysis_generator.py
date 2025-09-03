"""
GERADOR DE ANÁLISES - PRODUÇÃO DE MEL
====================================
Responsável por análises exploratórias detalhadas dos datasets
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analisar_distribuicoes(df, titulo="Dataset"):
    """Análise detalhada das distribuições dos dados"""
    print(f"\n📈 ANÁLISE DE DISTRIBUIÇÕES - {titulo.upper()}")
    print("=" * 60)
    
    # Informações básicas
    print(f"Shape: {df.shape}")
    print(f"Valores nulos: {df.isnull().sum().sum()}")
    print(f"Duplicados: {df.duplicated().sum()}")
    
    # Distribuição do target
    if 'probabilidade' in df.columns:
        print(f"\n🎯 Distribuição do Target (Probabilidade):")
        dist = df['probabilidade'].value_counts().sort_index()
        classes = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']
        
        for i, count in enumerate(dist.values):
            pct = (count / len(df)) * 100
            print(f"  {classes[i]:11}: {count:4} ({pct:.1f}%)")
    
    # Atributos categóricos
    categoricos = df.select_dtypes(include=['int64', 'object']).columns
    categoricos = [col for col in categoricos if col != 'probabilidade']
    
    if len(categoricos) > 0:
        print(f"\n📊 Análise de Atributos Categóricos:")
        for col in categoricos[:5]:  # Top 5 para não poluir
            valores_unicos = df[col].nunique()
            print(f"  {col}: {valores_unicos} valores únicos")
            if valores_unicos <= 5:
                dist = df[col].value_counts()
                for val, count in dist.items():
                    print(f"    {val}: {count} ({count/len(df)*100:.1f}%)")
    
    # Atributos numéricos
    numericos = df.select_dtypes(include=['float64']).columns
    
    if len(numericos) > 0:
        print(f"\n🔢 Análise de Atributos Numéricos:")
        for col in numericos:
            print(f"  {col}:")
            print(f"    Média: {df[col].mean():.2f}")
            print(f"    Desvio: {df[col].std():.2f}")
            print(f"    Min/Max: {df[col].min():.2f} / {df[col].max():.2f}")


def analisar_correlacoes(df, titulo="Dataset"):
    """Análise de correlações entre variáveis"""
    print(f"\n🔗 ANÁLISE DE CORRELAÇÕES - {titulo.upper()}")
    print("=" * 60)
    
    # Correlação com o target
    if 'probabilidade' in df.columns:
        correlacoes = df.corr()['probabilidade'].sort_values(key=abs, ascending=False)
        correlacoes = correlacoes.drop('probabilidade')  # Remove auto-correlação
        
        print(f"\n🎯 Correlação com Probabilidade (Top 10):")
        for var, corr in correlacoes.head(10).items():
            print(f"  {var:25}: {corr:>6.3f}")
    
    # Correlações altas entre features
    corr_matrix = df.corr()
    high_corr = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            var1 = corr_matrix.columns[i]
            var2 = corr_matrix.columns[j]
            corr_val = corr_matrix.iloc[i, j]
            
            if abs(corr_val) > 0.7:  # Correlação alta
                high_corr.append((var1, var2, corr_val))
    
    if high_corr:
        print(f"\n⚠️ Correlações Altas entre Features (|r| > 0.7):")
        for var1, var2, corr in high_corr:
            print(f"  {var1} ↔ {var2}: {corr:.3f}")
    else:
        print(f"\n✅ Sem correlações altas entre features (|r| > 0.7)")


def analisar_impactos_criticos(df, titulo="Dataset"):
    """Análise do impacto de atributos críticos no resultado"""
    print(f"\n⚡ ANÁLISE DE IMPACTOS CRÍTICOS - {titulo.upper()}")
    print("=" * 60)
    
    if 'probabilidade' not in df.columns:
        print("❌ Coluna 'probabilidade' não encontrada")
        return
    
    atributos_criticos = [
        'higienizacao_previa',
        'uso_epi', 
        'vedacao_adequada',
        'aspecto_visual',
        'rotulo_presente'
    ]
    
    # Filtrar apenas atributos que existem no dataset
    criticos_existentes = [attr for attr in atributos_criticos if attr in df.columns]
    
    for attr in criticos_existentes:
        print(f"\n🎯 Impacto de {attr}:")
        
        # Calcular probabilidade média por categoria
        impacto = df.groupby(attr)['probabilidade'].agg(['count', 'mean', 'std']).round(3)
        
        for categoria, stats in impacto.iterrows():
            count, mean, std = stats['count'], stats['mean'], stats['std']
            print(f"  Categoria {categoria}: n={count:4}, prob_média={mean:.3f}, std={std:.3f}")
    
    # Tempo de exposição (numérico)
    if 'tempo_exposicao_ar' in df.columns:
        print(f"\n⏱️ Impacto do Tempo de Exposição:")
        
        # Categorizar tempo
        df_temp = df.copy()
        df_temp['tempo_categoria'] = pd.cut(
            df_temp['tempo_exposicao_ar'], 
            bins=[0, 15, 30, 45, 100], 
            labels=['Baixo(≤15min)', 'Médio(15-30min)', 'Alto(30-45min)', 'Crítico(>45min)']
        )
        
        impacto_tempo = df_temp.groupby('tempo_categoria')['probabilidade'].agg(['count', 'mean']).round(3)
        
        for categoria, stats in impacto_tempo.iterrows():
            count, mean = stats['count'], stats['mean']
            print(f"  {categoria}: n={count:4}, prob_média={mean:.3f}")


def gerar_visualizacoes_exploratórias(df, titulo="Dataset", salvar_path="../models/"):
    """Gera visualizações exploratórias detalhadas"""
    print(f"\n📊 GERANDO VISUALIZAÇÕES - {titulo.upper()}")
    print("=" * 50)
    
    plt.style.use('default')
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'Análise Exploratória - {titulo}', fontsize=16, fontweight='bold')
    
    # 1. Distribuição das classes
    if 'probabilidade' in df.columns:
        dist = df['probabilidade'].value_counts().sort_index()
        classes = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']
        colors = ['green', 'yellow', 'orange', 'red']
        
        axes[0, 0].bar(classes, dist.values, color=colors, alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('Distribuição das Classes')
        axes[0, 0].set_ylabel('Quantidade')
        
        for i, v in enumerate(dist.values):
            axes[0, 0].text(i, v + 5, str(v), ha='center', fontweight='bold')
    
    # 2. Impacto da higienização
    if 'higienizacao_previa' in df.columns and 'probabilidade' in df.columns:
        higiene_prob = pd.crosstab(df['higienizacao_previa'], df['probabilidade'], normalize='columns') * 100
        higiene_prob.plot(kind='bar', ax=axes[0, 1], color=['lightcoral', 'lightgreen'])
        axes[0, 1].set_title('Higienização vs Probabilidade')
        axes[0, 1].set_xlabel('Higienização (0=Não, 1=Sim)')
        axes[0, 1].set_ylabel('Percentual (%)')
        axes[0, 1].legend(title='Probabilidade', labels=classes)
        axes[0, 1].set_xticklabels(['Não', 'Sim'], rotation=0)
    
    # 3. Distribuição do EPI
    if 'uso_epi' in df.columns:
        epi_dist = df['uso_epi'].value_counts().sort_index()
        epi_labels = ['Ausente', 'Parcial', 'Completo']
        epi_colors = ['red', 'yellow', 'green']
        
        axes[0, 2].bar(epi_labels, epi_dist.values, color=epi_colors, alpha=0.7)
        axes[0, 2].set_title('Distribuição do Uso de EPI')
        axes[0, 2].set_ylabel('Quantidade')
        
        for i, v in enumerate(epi_dist.values):
            axes[0, 2].text(i, v + 5, str(v), ha='center', fontweight='bold')
    
    # 4. Tempo de exposição por classe
    if 'tempo_exposicao_ar' in df.columns and 'probabilidade' in df.columns:
        for i in range(4):
            data = df[df['probabilidade'] == i]['tempo_exposicao_ar']
            if len(data) > 0:
                axes[1, 0].hist(data, alpha=0.5, label=classes[i], color=colors[i], bins=15)
        
        axes[1, 0].set_title('Tempo de Exposição por Classe')
        axes[1, 0].set_xlabel('Tempo (minutos)')
        axes[1, 0].set_ylabel('Frequência')
        axes[1, 0].legend()
        axes[1, 0].axvline(x=30, color='red', linestyle='--', alpha=0.7, label='Limite crítico')
    
    # 5. Heatmap de correlações (top features)
    if len(df.columns) > 5:
        # Selecionar apenas correlações mais relevantes
        corr_matrix = df.corr()
        if 'probabilidade' in corr_matrix.columns:
            prob_corr = corr_matrix['probabilidade'].abs().sort_values(ascending=False)
            top_features = prob_corr.head(8).index  # Top 8 features + probabilidade
            
            top_corr = corr_matrix.loc[top_features, top_features]
            
            im = axes[1, 1].imshow(top_corr.values, cmap='RdBu', aspect='auto', vmin=-1, vmax=1)
            axes[1, 1].set_xticks(range(len(top_features)))
            axes[1, 1].set_yticks(range(len(top_features)))
            axes[1, 1].set_xticklabels(top_features, rotation=45, ha='right')
            axes[1, 1].set_yticklabels(top_features)
            axes[1, 1].set_title('Correlações (Top Features)')
            
            # Adicionar valores na matriz
            for i in range(len(top_features)):
                for j in range(len(top_features)):
                    text = axes[1, 1].text(j, i, f'{top_corr.iloc[i, j]:.2f}',
                                         ha="center", va="center", color="black", fontsize=8)
            
            plt.colorbar(im, ax=axes[1, 1], shrink=0.6)
    
    # 6. Box plot - Tempo por probabilidade
    if 'tempo_exposicao_ar' in df.columns and 'probabilidade' in df.columns:
        df_box = df.copy()
        df_box['prob_label'] = df_box['probabilidade'].map({0: 'DESP', 1: 'BAIXA', 2: 'MÉDIA', 3: 'ALTA'})
        
        box_data = [df_box[df_box['prob_label'] == label]['tempo_exposicao_ar'].values 
                   for label in ['DESP', 'BAIXA', 'MÉDIA', 'ALTA']]
        
        bp = axes[1, 2].boxplot(box_data, labels=['DESP', 'BAIXA', 'MÉDIA', 'ALTA'], patch_artist=True)
        
        # Colorir boxes
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        axes[1, 2].set_title('Tempo de Exposição por Classe (Box Plot)')
        axes[1, 2].set_ylabel('Tempo (minutos)')
        axes[1, 2].axhline(y=30, color='red', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    
    # Salvar
    nome_arquivo = f'analise_exploratoria_{titulo.lower().replace(" ", "_")}.png'
    caminho_completo = os.path.join(salvar_path, nome_arquivo)
    plt.savefig(caminho_completo, dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"📊 Visualizações salvas: {caminho_completo}")
    return caminho_completo


def analisar_qualidade_dados(df, titulo="Dataset"):
    """Análise da qualidade dos dados"""
    print(f"\n🔍 ANÁLISE DE QUALIDADE - {titulo.upper()}")
    print("=" * 50)
    
    # Completude
    total_cells = df.shape[0] * df.shape[1]
    missing_cells = df.isnull().sum().sum()
    completude = ((total_cells - missing_cells) / total_cells) * 100
    
    print(f"📊 Completude geral: {completude:.1f}%")
    
    # Valores nulos por coluna
    missing_by_col = df.isnull().sum()
    if missing_by_col.sum() > 0:
        print(f"\n❌ Valores nulos por coluna:")
        for col, missing in missing_by_col[missing_by_col > 0].items():
            pct = (missing / len(df)) * 100
            print(f"  {col}: {missing} ({pct:.1f}%)")
    else:
        print(f"\n✅ Sem valores nulos")
    
    # Duplicados
    duplicados = df.duplicated().sum()
    if duplicados > 0:
        print(f"\n❌ Registros duplicados: {duplicados} ({duplicados/len(df)*100:.1f}%)")
    else:
        print(f"\n✅ Sem registros duplicados")
    
    # Outliers em variáveis numéricas
    numericas = df.select_dtypes(include=[np.number]).columns
    if len(numericas) > 0:
        print(f"\n📈 Análise de Outliers (IQR):")
        for col in numericas:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            if len(outliers) > 0:
                print(f"  {col}: {len(outliers)} outliers ({len(outliers)/len(df)*100:.1f}%)")
    
    # Balanço das classes
    if 'probabilidade' in df.columns:
        print(f"\n⚖️ Balanço das Classes:")
        dist = df['probabilidade'].value_counts().sort_index()
        classes = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']
        
        min_class = dist.min()
        max_class = dist.max()
        ratio = max_class / min_class if min_class > 0 else float('inf')
        
        print(f"  Razão max/min: {ratio:.2f}")
        if ratio > 3:
            print(f"  ⚠️ Classes desbalanceadas")
        else:
            print(f"  ✅ Classes relativamente balanceadas")


def gerar_relatorio_completo(dataset_path, titulo="Dataset"):
    """
    Função principal para gerar relatório completo de análise
    """
    print(f"🔍 RELATÓRIO COMPLETO DE ANÁLISE")
    print(f"Dataset: {dataset_path}")
    print("=" * 70)
    
    try:
        # Carregar dados
        df = pd.read_csv(dataset_path)
        print(f"✅ Dataset carregado: {df.shape[0]} amostras, {df.shape[1]} colunas")
        
        # Executar todas as análises
        analisar_distribuicoes(df, titulo)
        analisar_correlacoes(df, titulo)
        analisar_impactos_criticos(df, titulo)
        analisar_qualidade_dados(df, titulo)
        
        # Gerar visualizações
        caminho_viz = gerar_visualizacoes_exploratórias(df, titulo)
        
        print(f"\n✅ RELATÓRIO COMPLETO GERADO")
        print(f"📊 Visualizações: {caminho_viz}")
        
        return df, caminho_viz
        
    except Exception as e:
        print(f"❌ Erro ao analisar dataset: {e}")
        return None, None


if __name__ == "__main__":
    print("🍯 GERADOR DE ANÁLISES - PRODUÇÃO DE MEL")
    print("=" * 50)
    
    # Datasets padrão para análise
    datasets = [
        ("../dataset/mel/envase_rotulagem/dataset_envase_rotulagem.csv", "Envase e Rotulagem"),
        ("../dataset/mel/pcc/dataset_pcc_mel.csv", "PCC Geral")
    ]
    
    for dataset_path, titulo in datasets:
        if os.path.exists(dataset_path):
            print(f"\n{'='*70}")
            gerar_relatorio_completo(dataset_path, titulo)
        else:
            print(f"\n❌ Dataset não encontrado: {dataset_path}")
    
    print(f"\n✅ Análises concluídas!")