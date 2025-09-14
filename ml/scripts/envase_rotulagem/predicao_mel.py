# ml/scripts/envase_rotulagem/predicao_mel.py
"""
PREDITOR DE PROBABILIDADE DE FALHAS - PRODUÇÃO DE MEL
====================================================
Script para usar modelos já treinados sem retreinar
"""

import pandas as pd
import joblib
import json
import os

# Classes de probabilidade
CLASSES = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']

def listar_modelos_por_algoritmo():
    """Lista modelos agrupados por algoritmo"""
    # Determinar caminho absoluto baseado na localização do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    models_dir = os.path.join(ml_dir, "models", "envase_rotulagem")
    
    if not os.path.exists(models_dir):
        print("❌ Pasta de modelos não encontrada")
        return {}
    
    # Dicionário para agrupar modelos por algoritmo
    modelos_por_algoritmo = {}
    
    try:
        # Procurar todos os arquivos .pkl de modelo
        arquivos = [f for f in os.listdir(models_dir) if f.endswith('.pkl') and not f.startswith('scaler_')]
        
        for arquivo in arquivos:
            modelo_path = os.path.join(models_dir, arquivo)
            
            # Tentar identificar o tipo de modelo carregando
            try:
                modelo = joblib.load(modelo_path)
                algoritmo = type(modelo).__name__
                
                # Encontrar arquivos relacionados (scaler e config)
                timestamp = arquivo.replace('classificador_mel_', '').replace('.pkl', '')
                scaler_path = os.path.join(models_dir, f"scaler_mel_{timestamp}.pkl")
                config_path = os.path.join(models_dir, f"config_classificador_{timestamp}.json")
                
                if os.path.exists(scaler_path) and os.path.exists(config_path):
                    # Ler configuração
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                    
                    # Mapear nomes amigáveis
                    nome_algoritmo = {
                        'RandomForestClassifier': 'Random Forest',
                        'SVC': 'SVM',
                        'GradientBoostingClassifier': 'Gradient Boosting',
                        'LogisticRegression': 'Regressão Logística'
                    }.get(algoritmo, algoritmo)
                    
                    if nome_algoritmo not in modelos_por_algoritmo:
                        modelos_por_algoritmo[nome_algoritmo] = []
                    
                    modelos_por_algoritmo[nome_algoritmo].append({
                        'timestamp': timestamp,
                        'modelo_path': modelo_path,
                        'scaler_path': scaler_path,
                        'config_path': config_path,
                        'config': config,
                        'algoritmo_original': algoritmo
                    })
                    
            except Exception as e:
                print(f"  ⚠️  Erro ao carregar {arquivo}: {e}")
                continue
                
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
    
    return modelos_por_algoritmo

def escolher_modelo(modelos):
    """Permite ao usuário escolher um modelo"""
    if not modelos:
        return None
    
    print("0. Voltar")
    opcao = input(f"\nEscolha um modelo (0-{len(modelos)}): ").strip()
    
    try:
        opcao = int(opcao)
        if opcao == 0:
            return None
        elif 1 <= opcao <= len(modelos):
            return modelos[opcao - 1]
        else:
            print("❌ Opção inválida")
            return escolher_modelo(modelos)
    except ValueError:
        print("❌ Digite um número válido")
        return escolher_modelo(modelos)

def carregar_modelo_direto(modelo_info):
    """Carrega o modelo e scaler diretamente"""
    try:
        print(f"\n🔧 Carregando modelo {modelo_info['config']['timestamp']}...")
        
        # Carregar modelo
        modelo = joblib.load(modelo_info['modelo_path'])
        print(f"✅ Modelo carregado: {os.path.basename(modelo_info['modelo_path'])}")
        
        # Carregar scaler
        scaler = joblib.load(modelo_info['scaler_path'])
        print(f"✅ Scaler carregado: {os.path.basename(modelo_info['scaler_path'])}")
        
        return modelo, scaler
        
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return None, None

def criar_amostra_manual():
    """Permite criar uma amostra manualmente para predição"""
    print("\n🔧 CRIANDO AMOSTRA PARA PREDIÇÃO")
    print("=" * 50)
    
    # Definir atributos esperados (mesmo do dataset_generator)
    atributos = {
        # A) Estrutura da Embalagem
        'tipo_embalagem': {
            'desc': 'Tipo de embalagem',
            'opcoes': {0: 'PET', 1: 'Vidro'},
            'tipo': 'choice'
        },
        'estado_embalagem': {
            'desc': 'Estado da embalagem',
            'opcoes': {0: 'Danificada', 1: 'Íntegra'},
            'tipo': 'choice'
        },
        'tampa_correta': {
            'desc': 'Tampa correta',
            'opcoes': {0: 'Não', 1: 'Sim'},
            'tipo': 'choice'
        },
        'vedacao_adequada': {
            'desc': 'Vedação adequada',
            'opcoes': {0: 'Inadequada', 1: 'Adequada'},
            'tipo': 'choice'
        },
        
        # B) Higiene e Manipulação
        'higienizacao_previa': {
            'desc': 'Higienização prévia',
            'opcoes': {0: 'Não', 1: 'Sim'},
            'tipo': 'choice'
        },
        'uso_epi': {
            'desc': 'Uso de EPI',
            'opcoes': {0: 'Ausente', 1: 'Parcial', 2: 'Completo'},
            'tipo': 'choice'
        },
        'local_envase': {
            'desc': 'Local de envase',
            'opcoes': {0: 'Inadequado', 1: 'Adequado'},
            'tipo': 'choice'
        },
        'manipulador_higiene': {
            'desc': 'Higiene do manipulador',
            'opcoes': {0: 'Inadequada', 1: 'Adequada'},
            'tipo': 'choice'
        },
        
        # C) Condições do Mel
        'aspecto_visual': {
            'desc': 'Aspecto visual do mel',
            'opcoes': {0: 'Sujidades', 1: 'Espuma', 2: 'Normal'},
            'tipo': 'choice'
        },
        'umidade_mel': {
            'desc': 'Umidade do mel',
            'opcoes': {0: '>20%', 1: '≤20%'},
            'tipo': 'choice'
        },
        'temperatura_envase': {
            'desc': 'Temperatura de envase',
            'opcoes': {0: 'Inadequada', 1: 'Adequada'},
            'tipo': 'choice'
        },
        'cristalizacao': {
            'desc': 'Cristalização',
            'opcoes': {0: 'Excessiva', 1: 'Parcial', 2: 'Ausente'},
            'tipo': 'choice'
        },
        
        # D) Rotulagem
        'rotulo_presente': {
            'desc': 'Rótulo presente',
            'opcoes': {0: 'Não', 1: 'Sim'},
            'tipo': 'choice'
        },
        'informacoes_completas': {
            'desc': 'Informações completas',
            'opcoes': {0: 'Incompletas', 1: 'Completas'},
            'tipo': 'choice'
        },
        'data_validade_legivel': {
            'desc': 'Data de validade legível',
            'opcoes': {0: 'Não', 1: 'Sim'},
            'tipo': 'choice'
        },
        'lote_identificado': {
            'desc': 'Lote identificado',
            'opcoes': {0: 'Não', 1: 'Sim'},
            'tipo': 'choice'
        },
        
        # E) Histórico/Organização
        'treinamento_equipe': {
            'desc': 'Treinamento da equipe',
            'opcoes': {0: 'Não', 1: 'Sim'},
            'tipo': 'choice'
        },
        'historico_reclamacoes': {
            'desc': 'Histórico de reclamações',
            'opcoes': {0: 'Frequentes', 1: 'Poucas', 2: 'Nenhuma'},
            'tipo': 'choice'
        },
        'registro_lote': {
            'desc': 'Registro do lote',
            'opcoes': {0: 'Não', 1: 'Sim'},
            'tipo': 'choice'
        },
        'tempo_exposicao_ar': {
            'desc': 'Tempo de exposição ao ar (5-60 minutos)',
            'tipo': 'numeric',
            'min': 5,
            'max': 60
        }
    }
    
    amostra = {}
    
    print("Digite os valores para cada atributo:")
    print("(Digite 'q' para cancelar)\n")
    
    for attr_name, attr_info in atributos.items():
        while True:
            if attr_info['tipo'] == 'choice':
                print(f"\n{attr_info['desc']}:")
                for key, value in attr_info['opcoes'].items():
                    print(f"  {key}: {value}")
                
                entrada = input(f"Escolha ({'/'.join(map(str, attr_info['opcoes'].keys()))}): ").strip()
                
                if entrada.lower() == 'q':
                    return None
                
                try:
                    valor = int(entrada)
                    if valor in attr_info['opcoes']:
                        amostra[attr_name] = valor
                        break
                    else:
                        print("❌ Opção inválida")
                except ValueError:
                    print("❌ Digite um número válido")
                    
            elif attr_info['tipo'] == 'numeric':
                entrada = input(f"\n{attr_info['desc']}: ").strip()
                
                if entrada.lower() == 'q':
                    return None
                
                try:
                    valor = float(entrada)
                    if attr_info['min'] <= valor <= attr_info['max']:
                        amostra[attr_name] = valor
                        break
                    else:
                        print(f"❌ Valor deve estar entre {attr_info['min']} e {attr_info['max']}")
                except ValueError:
                    print("❌ Digite um número válido")
    
    return pd.DataFrame([amostra])

def salvar_resultado_predicao(amostra_df, predicao, probabilidades, modelo_info, algoritmo_escolhido):
    """Salva resultado da predição em arquivo na nova estrutura /results_trained_models/"""
    import pandas as pd
    
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    
    # Determinar etapa baseada na configuração do modelo
    etapa = modelo_info.get('config', {}).get('etapa', 'envase_rotulagem')
    
    # Criar pasta se não existir (nova estrutura)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ml_dir = os.path.join(script_dir, "..", "..")
    pasta_results = os.path.join(ml_dir, "results_trained_models", etapa)
    os.makedirs(pasta_results, exist_ok=True)
    
    # Nome do arquivo
    nome_arquivo = f"predicao_{algoritmo_escolhido.lower().replace(' ', '_')}_{timestamp}.txt"
    caminho_arquivo = os.path.join(pasta_results, nome_arquivo)
    
    # Salvar resultado
    with open(caminho_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"RESULTADO DA PREDIÇÃO - {algoritmo_escolhido.upper()}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Dataset: {modelo_info['config']['dataset_usado']}\n")
        f.write(f"Algoritmo: {algoritmo_escolhido}\n")
        f.write(f"Modelo timestamp: {modelo_info['config']['timestamp']}\n\n")
        
        f.write("DADOS DE ENTRADA:\n")
        f.write("-" * 20 + "\n")
        for col, val in amostra_df.iloc[0].items():
            f.write(f"{col}: {val}\n")
        
        f.write(f"\nRESULTADO:\n")
        f.write("-" * 10 + "\n")
        f.write(f"Classe predita: {CLASSES[predicao]}\n\n")
        
        f.write("Probabilidades por classe:\n")
        for i, (classe, prob) in enumerate(zip(CLASSES, probabilidades)):
            marker = ">>> " if i == predicao else "    "
            f.write(f"{marker}{classe:11}: {prob:.1%}\n")
    
    print(f"💾 Resultado salvo em: {os.path.relpath(caminho_arquivo, ml_dir)}")
    return caminho_arquivo


def fazer_predicao_com_resultado(modelo, scaler, amostra_df, modelo_info, algoritmo_escolhido):
    """Faz predição usando modelo carregado e salva resultado na nova estrutura"""
    try:
        # Normalizar amostra
        amostra_scaled = scaler.transform(amostra_df)
        
        # Fazer predição
        predicao = modelo.predict(amostra_scaled)[0]
        probabilidades = modelo.predict_proba(amostra_scaled)[0]
        
        print(f"\n🎯 RESULTADO DA PREDIÇÃO")
        print("=" * 30)
        print(f"Classe predita: {CLASSES[predicao]}")
        print(f"\nProbabilidades por classe:")
        
        for i, (classe, prob) in enumerate(zip(CLASSES, probabilidades)):
            emoji = "👉" if i == predicao else "  "
            print(f"{emoji} {classe:11}: {prob:.1%}")
        
        # Salvar resultado
        caminho_resultado = salvar_resultado_predicao(amostra_df, predicao, probabilidades, modelo_info, algoritmo_escolhido)
        
        return predicao, probabilidades, caminho_resultado
        
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        return None, None, None

def fazer_predicao(modelo, scaler, amostra_df):
    """Faz predição usando modelo carregado (função legada)"""
    try:
        # Normalizar amostra
        amostra_scaled = scaler.transform(amostra_df)
        
        # Fazer predição
        predicao = modelo.predict(amostra_scaled)[0]
        probabilidades = modelo.predict_proba(amostra_scaled)[0]
        
        print(f"\\n🎯 RESULTADO DA PREDIÇÃO")
        print("=" * 30)
        print(f"Classe predita: {CLASSES[predicao]}")
        print(f"\\nProbabilidades por classe:")
        
        for i, (classe, prob) in enumerate(zip(CLASSES, probabilidades)):
            emoji = "👉" if i == predicao else "  "
            print(f"{emoji} {classe:11}: {prob:.1%}")
        
        return predicao, probabilidades, None
        
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
        return None, None, None

def main():
    """Função principal para predição sem retreinamento"""
    print("🍯 PREDITOR DE PROBABILIDADE DE FALHAS - MEL")
    print("=" * 60)
    print("🎯 PROPÓSITO: Classificar amostras usando modelos já treinados")
    print("📋 ENTRADA: 20 atributos do processo de envase e rotulagem")
    print("📊 SAÍDA: Probabilidade de falha (DESPREZÍVEL/BAIXA/MÉDIA/ALTA)")
    print("=" * 60)
    
    # 1. DATASET
    print(f"\n1️⃣ DATASET: Envase e Rotulagem")
    print("   📊 1500 amostras, 20 atributos realistas")
    
    # 2. ESCOLHA DO MODELO
    print(f"\n2️⃣ ESCOLHA O MODELO TREINADO:")
    
    modelos_por_algoritmo = listar_modelos_por_algoritmo()
    
    if not modelos_por_algoritmo:
        print("❌ Nenhum modelo disponível")
        print("💡 Execute primeiro o script classificador_mel.py para treinar modelos")
        return
    
    # Mostrar opções de algoritmos
    algoritmos = list(modelos_por_algoritmo.keys())
    for i, algoritmo in enumerate(algoritmos):
        count = len(modelos_por_algoritmo[algoritmo])
        mais_recente = max(modelos_por_algoritmo[algoritmo], key=lambda x: x['timestamp'])
        print(f"   {chr(97+i)}) {algoritmo} ({count} modelo{'s' if count > 1 else ''} - mais recente: {mais_recente['timestamp']})")
    
    # Escolher algoritmo
    while True:
        escolha = input(f"\nEscolha um algoritmo ({'-'.join([chr(97+i) for i in range(len(algoritmos))])}): ").strip().lower()
        
        if escolha in [chr(97+i) for i in range(len(algoritmos))]:
            indice = ord(escolha) - 97
            algoritmo_escolhido = algoritmos[indice]
            break
        else:
            print("❌ Opção inválida!")
    
    # Usar o modelo mais recente do algoritmo escolhido
    modelo_info = max(modelos_por_algoritmo[algoritmo_escolhido], key=lambda x: x['timestamp'])
    
    print(f"\n🤖 USANDO: {algoritmo_escolhido}")
    print(f"   📅 Timestamp: {modelo_info['timestamp']}")
    print(f"   📊 Dataset: {modelo_info['config']['dataset_usado']}")
    
    # Carregar modelo
    modelo, scaler = carregar_modelo_direto(modelo_info)
    
    if modelo is None:
        return
    
    print(f"\n✅ Modelo carregado e pronto para predições!")
    
    # Loop de predições
    while True:
        print(f"\n" + "="*50)
        print("🔧 OPÇÕES:")
        print("1. 🔮 Fazer nova predição")
        print("2. 🔄 Escolher outro modelo")
        print("0. 🚪 Sair")
        print("="*50)
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            print("\n" + "🔮 NOVA PREDIÇÃO".center(50, "="))
            
            # Criar amostra
            amostra_df = criar_amostra_manual()
            
            if amostra_df is not None:
                # Fazer predição
                predicao, _, caminho_resultado = fazer_predicao_com_resultado(modelo, scaler, amostra_df, modelo_info, algoritmo_escolhido)
                
                if predicao is not None:
                    if caminho_resultado:
                        print(f"\n💾 Resultado salvo: {os.path.basename(caminho_resultado)}")
                    
                    continuar = input("\n🔄 Fazer outra predição? (s/N): ").strip().lower()
                    if continuar not in ['s', 'sim', 'y', 'yes']:
                        break
            else:
                print("❌ Predição cancelada")
                
        elif opcao == "2":
            # Reiniciar escolha de modelo
            main()
            return
            
        elif opcao == "0":
            print("\n👋 Encerrando preditor...")
            break
            
        else:
            print("❌ Opção inválida! Digite 0, 1 ou 2.")

if __name__ == "__main__":
    main()