"""
GERADOR DE DATASETS - PRODUÇÃO DE MEL
=====================================
Responsável pela geração de dados sintéticos para diferentes etapas do processo
"""

import pandas as pd
import numpy as np
import os

def gerar_dataset_envase_rotulagem(n_samples=1500, seed=42):
    """
    Gera dataset para etapa ENVASE E ROTULAGEM
    20 atributos realistas para pequenos e médios produtores
    """
    np.random.seed(seed)
    data = []
    
    print(f"🏭 Gerando {n_samples} amostras para ENVASE E ROTULAGEM...")
    
    for i in range(n_samples):
        # A) Estrutura da Embalagem
        tipo_embalagem = np.random.choice([0, 1], p=[0.3, 0.7])  # 0: PET, 1: vidro
        estado_embalagem = np.random.choice([0, 1], p=[0.05, 0.95])  # 0: danificada, 1: íntegra
        tampa_correta = np.random.choice([0, 1], p=[0.02, 0.98])  # 0: não, 1: sim
        vedacao_adequada = np.random.choice([0, 1], p=[0.08, 0.92])  # 0: inadequada, 1: adequada
        
        # B) Higiene e Manipulação
        higienizacao_previa = np.random.choice([0, 1], p=[0.1, 0.9])  # 0: não, 1: sim
        uso_epi = np.random.choice([0, 1, 2], p=[0.05, 0.25, 0.70])  # 0: ausente, 1: parcial, 2: completo
        local_envase = np.random.choice([0, 1], p=[0.15, 0.85])  # 0: inadequado, 1: adequado
        manipulador_higiene = np.random.choice([0, 1], p=[0.08, 0.92])  # 0: inadequada, 1: adequada
        
        # C) Condições do Mel
        aspecto_visual = np.random.choice([0, 1, 2], p=[0.02, 0.08, 0.90])  # 0: sujidades, 1: espuma, 2: normal
        umidade_mel = np.random.choice([0, 1], p=[0.2, 0.8])  # 0: >20%, 1: ≤20%
        temperatura_envase = np.random.choice([0, 1], p=[0.15, 0.85])  # 0: inadequada, 1: adequada
        cristalizacao = np.random.choice([0, 1, 2], p=[0.1, 0.3, 0.6])  # 0: excessiva, 1: parcial, 2: ausente
        
        # D) Rotulagem
        rotulo_presente = np.random.choice([0, 1], p=[0.03, 0.97])  # 0: não, 1: sim
        informacoes_completas = np.random.choice([0, 1], p=[0.12, 0.88])  # 0: incompletas, 1: completas
        data_validade_legivel = np.random.choice([0, 1], p=[0.05, 0.95])  # 0: não, 1: sim
        lote_identificado = np.random.choice([0, 1], p=[0.08, 0.92])  # 0: não, 1: sim
        
        # E) Histórico/Organização
        treinamento_equipe = np.random.choice([0, 1], p=[0.25, 0.75])  # 0: não, 1: sim
        historico_reclamacoes = np.random.choice([0, 1, 2], p=[0.05, 0.20, 0.75])  # 0: frequentes, 1: poucas, 2: nenhuma
        registro_lote = np.random.choice([0, 1], p=[0.1, 0.9])  # 0: não, 1: sim
        tempo_exposicao_ar = np.random.uniform(5, 60)  # minutos
        
        # Calcular probabilidade usando regras de negócio
        probabilidade_score = 0
        
        # CRÍTICOS
        if higienizacao_previa == 0: probabilidade_score += 8
        if estado_embalagem == 0: probabilidade_score += 7
        if vedacao_adequada == 0: probabilidade_score += 6
        if uso_epi == 0: probabilidade_score += 7
        if aspecto_visual == 0: probabilidade_score += 8
        if manipulador_higiene == 0: probabilidade_score += 6
        if rotulo_presente == 0: probabilidade_score += 5
            
        # IMPORTANTES
        if umidade_mel == 0: probabilidade_score += 4
        if uso_epi == 1: probabilidade_score += 3
        if local_envase == 0: probabilidade_score += 4
        if historico_reclamacoes == 0: probabilidade_score += 4
        if tempo_exposicao_ar > 30: probabilidade_score += 3
        if temperatura_envase == 0: probabilidade_score += 3
        if aspecto_visual == 1: probabilidade_score += 2
        if informacoes_completas == 0: probabilidade_score += 3
            
        # MENORES
        if treinamento_equipe == 0: probabilidade_score += 2
        if cristalizacao == 0: probabilidade_score += 2
        if data_validade_legivel == 0: probabilidade_score += 2
        if lote_identificado == 0: probabilidade_score += 1
        if registro_lote == 0: probabilidade_score += 1
        if tampa_correta == 0: probabilidade_score += 3
            
        # REDUTORES
        if treinamento_equipe == 1: probabilidade_score -= 1
        if historico_reclamacoes == 2: probabilidade_score -= 2
        if uso_epi == 2: probabilidade_score -= 2
        if higienizacao_previa == 1 and manipulador_higiene == 1: probabilidade_score -= 2
        if tipo_embalagem == 1: probabilidade_score -= 1
        if rotulo_presente == 1 and informacoes_completas == 1: probabilidade_score -= 2
            
        # Classificar probabilidade
        if probabilidade_score >= 12:
            probabilidade = 3  # ALTA
        elif probabilidade_score >= 6:
            probabilidade = 2  # MÉDIA
        elif probabilidade_score >= 3:
            probabilidade = 1  # BAIXA
        else:
            probabilidade = 0  # DESPREZÍVEL
            
        # Ruído
        if np.random.random() < 0.05:
            probabilidade = np.random.choice([0, 1, 2, 3])
            
        sample = {
            'tipo_embalagem': tipo_embalagem,
            'estado_embalagem': estado_embalagem,
            'tampa_correta': tampa_correta,
            'vedacao_adequada': vedacao_adequada,
            'higienizacao_previa': higienizacao_previa,
            'uso_epi': uso_epi,
            'local_envase': local_envase,
            'manipulador_higiene': manipulador_higiene,
            'aspecto_visual': aspecto_visual,
            'umidade_mel': umidade_mel,
            'temperatura_envase': temperatura_envase,
            'cristalizacao': cristalizacao,
            'rotulo_presente': rotulo_presente,
            'informacoes_completas': informacoes_completas,
            'data_validade_legivel': data_validade_legivel,
            'lote_identificado': lote_identificado,
            'treinamento_equipe': treinamento_equipe,
            'historico_reclamacoes': historico_reclamacoes,
            'registro_lote': registro_lote,
            'tempo_exposicao_ar': tempo_exposicao_ar,
            'probabilidade': probabilidade
        }
        
        data.append(sample)
    
    return pd.DataFrame(data)




def salvar_dataset(df, tipo_dataset, pasta_destino):
    """Salva o dataset na pasta apropriada"""
    # Criar pasta se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Definir nome do arquivo
    nome_arquivo = f"dataset_{tipo_dataset}.csv"
    caminho_completo = os.path.join(pasta_destino, nome_arquivo)
    
    # Salvar
    df.to_csv(caminho_completo, index=False)
    
    print(f"💾 Dataset salvo: {caminho_completo}")
    return caminho_completo


def mostrar_estatisticas_basicas(df, nome_dataset):
    """Mostra estatísticas básicas do dataset gerado"""
    print(f"\n📊 ESTATÍSTICAS - {nome_dataset.upper()}")
    print("=" * 50)
    print(f"Total de amostras: {len(df)}")
    print(f"Atributos: {len(df.columns)-1}")
    
    # Distribuição das classes
    if 'probabilidade' in df.columns:
        dist = df['probabilidade'].value_counts().sort_index()
        classes = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']
        
        print("\nDistribuição das Classes:")
        for i, count in enumerate(dist.values):
            pct = (count / len(df)) * 100
            print(f"  {classes[i]:11}: {count:4} ({pct:.1f}%)")
    
    # Atributos críticos
    criticos = ['higienizacao_previa', 'vedacao_adequada', 'uso_epi', 'aspecto_visual']
    criticos_existentes = [col for col in criticos if col in df.columns]
    
    if criticos_existentes:
        print("\nAtributos Críticos:")
        for col in criticos_existentes:
            if col == 'uso_epi':
                dist = df[col].value_counts().sort_index()
                labels = {0: 'Ausente', 1: 'Parcial', 2: 'Completo'}
                for val, count in dist.items():
                    print(f"  {col} - {labels[val]}: {count} ({count/len(df)*100:.1f}%)")
            elif col == 'aspecto_visual':
                dist = df[col].value_counts().sort_index()
                labels = {0: 'Sujidades', 1: 'Espuma', 2: 'Normal'}
                for val, count in dist.items():
                    print(f"  {col} - {labels[val]}: {count} ({count/len(df)*100:.1f}%)")
            else:
                ok = df[col].sum()
                print(f"  {col}: OK={ok} ({ok/len(df)*100:.1f}%)")


def gerar_dataset_por_tipo(tipo, n_samples=1500):
    """
    Função principal para gerar dataset por tipo
    """
    print(f"🔧 Gerando dataset: {tipo}")
    
    if tipo.lower() == 'envase_rotulagem':
        df = gerar_dataset_envase_rotulagem(n_samples)
        pasta = "../dataset/mel/envase_rotulagem/"
        nome = "envase_rotulagem"
        
    else:
        raise ValueError(f"Tipo '{tipo}' não reconhecido. Use: 'envase_rotulagem'")
    
    # Salvar dataset
    caminho = salvar_dataset(df, nome, pasta)
    
    # Mostrar estatísticas
    mostrar_estatisticas_basicas(df, nome)
    
    print(f"\n✅ Dataset {tipo} gerado com sucesso!")
    return caminho, df


if __name__ == "__main__":
    print("🍯 GERADOR DE DATASETS - PRODUÇÃO DE MEL")
    print("=" * 50)
    
    # Gerar dataset
    tipo = 'envase_rotulagem'
    print(f"\n{'-'*30}")
    gerar_dataset_por_tipo(tipo)
    
    print(f"\n✅ Todos os datasets gerados com sucesso!")