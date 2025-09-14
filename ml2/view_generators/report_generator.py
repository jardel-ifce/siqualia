# ml/view_generators/report_generator.py
"""
GERADOR DE RELATÓRIOS - PRODUÇÃO DE MEL
======================================
Responsável por simulações, relatórios executivos e recomendações
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
import json

def carregar_modelo_treinado(caminho_modelo, caminho_scaler):
    """Carrega modelo e scaler salvos"""
    try:
        modelo = joblib.load(caminho_modelo)
        scaler = joblib.load(caminho_scaler)
        print(f"✅ Modelo carregado: {caminho_modelo}")
        return modelo, scaler
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return None, None


def criar_cenarios_teste():
    """Cria cenários padronizados para teste"""
    cenarios = {
        'Produtor Exemplar': {
            'tipo_embalagem': 1, 'estado_embalagem': 1, 'tampa_correta': 1, 'vedacao_adequada': 1,
            'higienizacao_previa': 1, 'uso_epi': 2, 'local_envase': 1, 'manipulador_higiene': 1,
            'aspecto_visual': 2, 'umidade_mel': 1, 'temperatura_envase': 1, 'cristalizacao': 2,
            'rotulo_presente': 1, 'informacoes_completas': 1, 'data_validade_legivel': 1, 'lote_identificado': 1,
            'treinamento_equipe': 1, 'historico_reclamacoes': 2, 'registro_lote': 1, 'tempo_exposicao_ar': 15
        },
        'Produtor Médio': {
            'tipo_embalagem': 1, 'estado_embalagem': 1, 'tampa_correta': 1, 'vedacao_adequada': 1,
            'higienizacao_previa': 1, 'uso_epi': 1, 'local_envase': 1, 'manipulador_higiene': 1,
            'aspecto_visual': 2, 'umidade_mel': 1, 'temperatura_envase': 1, 'cristalizacao': 1,
            'rotulo_presente': 1, 'informacoes_completas': 0, 'data_validade_legivel': 1, 'lote_identificado': 1,
            'treinamento_equipe': 0, 'historico_reclamacoes': 1, 'registro_lote': 1, 'tempo_exposicao_ar': 25
        },
        'Produtor com Falhas': {
            'tipo_embalagem': 0, 'estado_embalagem': 1, 'tampa_correta': 1, 'vedacao_adequada': 0,
            'higienizacao_previa': 0, 'uso_epi': 1, 'local_envase': 0, 'manipulador_higiene': 1,
            'aspecto_visual': 1, 'umidade_mel': 0, 'temperatura_envase': 0, 'cristalizacao': 1,
            'rotulo_presente': 1, 'informacoes_completas': 0, 'data_validade_legivel': 1, 'lote_identificado': 0,
            'treinamento_equipe': 0, 'historico_reclamacoes': 1, 'registro_lote': 1, 'tempo_exposicao_ar': 45
        },
        'Situação Crítica': {
            'tipo_embalagem': 0, 'estado_embalagem': 0, 'tampa_correta': 0, 'vedacao_adequada': 0,
            'higienizacao_previa': 0, 'uso_epi': 0, 'local_envase': 0, 'manipulador_higiene': 0,
            'aspecto_visual': 0, 'umidade_mel': 0, 'temperatura_envase': 0, 'cristalizacao': 0,
            'rotulo_presente': 0, 'informacoes_completas': 0, 'data_validade_legivel': 0, 'lote_identificado': 0,
            'treinamento_equipe': 0, 'historico_reclamacoes': 0, 'registro_lote': 0, 'tempo_exposicao_ar': 60
        }
    }
    return cenarios


def avaliar_cenario(modelo, scaler, dados_cenario, nome_cenario):
    """Avalia um cenário específico"""
    # Criar DataFrame
    cenario_df = pd.DataFrame([dados_cenario])
    
    # Normalizar
    cenario_scaled = scaler.transform(cenario_df)
    
    # Prever
    predicao = modelo.predict(cenario_scaled)[0]
    probabilidades = modelo.predict_proba(cenario_scaled)[0]
    
    classes = ['DESPREZÍVEL', 'BAIXA', 'MÉDIA', 'ALTA']
    
    resultado = {
        'nome': nome_cenario,
        'predicao': predicao,
        'classe': classes[predicao],
        'probabilidades': {classes[i]: prob for i, prob in enumerate(probabilidades)},
        'confianca': probabilidades[predicao]
    }
    
    return resultado


def gerar_recomendacoes(resultado, dados_cenario):
    """Gera recomendações baseadas no resultado"""
    predicao = resultado['predicao']
    classe = resultado['classe']
    nome = resultado['nome']
    
    recomendacoes = {
        'nivel_urgencia': None,
        'acoes_imediatas': [],
        'melhorias_recomendadas': [],
        'monitoramento': [],
        'prazo': None
    }
    
    if predicao == 3:  # ALTA
        recomendacoes['nivel_urgencia'] = 'CRÍTICA'
        recomendacoes['prazo'] = 'IMEDIATO'
        recomendacoes['acoes_imediatas'] = [
            "⛔ INTERROMPER PRODUÇÃO imediatamente",
            "🧹 Higienização completa de equipamentos e ambiente",
            "👥 Retreinamento obrigatório de toda equipe",
            "📋 Revisão completa de todos os procedimentos",
            "🔍 Auditoria de segurança alimentar"
        ]
        
        # Recomendações específicas baseadas nos problemas identificados
        if dados_cenario.get('higienizacao_previa', 1) == 0:
            recomendacoes['acoes_imediatas'].append("🚿 Implementar protocolo de higienização obrigatório")
        
        if dados_cenario.get('vedacao_adequada', 1) == 0:
            recomendacoes['acoes_imediatas'].append("🔒 Substituir sistema de vedação")
        
        if dados_cenario.get('uso_epi', 2) == 0:
            recomendacoes['acoes_imediatas'].append("🥽 Fornecimento obrigatório de EPI completo")
            
    elif predicao == 2:  # MÉDIA
        recomendacoes['nivel_urgencia'] = 'ALTA'
        recomendacoes['prazo'] = '24-48 HORAS'
        recomendacoes['acoes_imediatas'] = [
            "⚠️ Implementar ações corretivas urgentes",
            "📊 Monitoramento intensificado dos PCCs",
            "👨‍🏫 Treinamento de reforço para equipe",
            "📝 Revisão dos procedimentos operacionais"
        ]
        
        recomendacoes['melhorias_recomendadas'] = [
            "Melhorar controle de tempo de exposição",
            "Reforçar uso adequado de EPIs",
            "Implementar checklist de verificação"
        ]
        
    elif predicao == 1:  # BAIXA
        recomendacoes['nivel_urgencia'] = 'MODERADA'
        recomendacoes['prazo'] = '7 DIAS'
        recomendacoes['melhorias_recomendadas'] = [
            "📚 Completar informações de rotulagem",
            "🎓 Programa de capacitação da equipe",
            "🔄 Revisar procedimentos de registro",
            "⏱️ Otimizar tempo de processo"
        ]
        
        recomendacoes['monitoramento'] = [
            "Monitoramento semanal dos indicadores",
            "Verificação quinzenal dos procedimentos"
        ]
        
    else:  # DESPREZÍVEL
        recomendacoes['nivel_urgencia'] = 'BAIXA'
        recomendacoes['prazo'] = 'CONTINUAR'
        recomendacoes['melhorias_recomendadas'] = [
            "✅ Manter as excelentes práticas atuais",
            "📈 Continuar monitoramento regular",
            "📖 Documentar boas práticas para replicação",
            "🏆 Servir como referência para outros produtores"
        ]
        
        recomendacoes['monitoramento'] = [
            "Monitoramento mensal de rotina",
            "Auditoria semestral preventiva"
        ]
    
    return recomendacoes


def simular_cenarios_completos(modelo, scaler):
    """Simula todos os cenários e gera relatório completo"""
    print("\n🎯 SIMULAÇÃO COMPLETA DE CENÁRIOS")
    print("=" * 70)
    
    cenarios = criar_cenarios_teste()
    resultados = []
    
    for nome, dados in cenarios.items():
        print(f"\n{'='*50}")
        print(f"📊 Cenário: {nome}")
        print(f"{'='*50}")
        
        # Avaliar cenário
        resultado = avaliar_cenario(modelo, scaler, dados, nome)
        
        # Gerar recomendações
        recomendacoes = gerar_recomendacoes(resultado, dados)
        
        # Mostrar resultados
        print(f"\n🎯 Classificação: {resultado['classe']}")
        print(f"📊 Confiança: {resultado['confianca']:.1%}")
        
        print(f"\nProbabilidades:")
        for classe, prob in resultado['probabilidades'].items():
            barra = '█' * int(prob * 20)
            print(f"  {classe:11}: {barra:<20} {prob:.1%}")
        
        print(f"\n📋 RECOMENDAÇÕES - Urgência: {recomendacoes['nivel_urgencia']}")
        print(f"⏱️ Prazo: {recomendacoes['prazo']}")
        
        if recomendacoes['acoes_imediatas']:
            print(f"\n🚨 AÇÕES IMEDIATAS:")
            for acao in recomendacoes['acoes_imediatas']:
                print(f"  {acao}")
        
        if recomendacoes['melhorias_recomendadas']:
            print(f"\n💡 MELHORIAS RECOMENDADAS:")
            for melhoria in recomendacoes['melhorias_recomendadas']:
                print(f"  • {melhoria}")
        
        if recomendacoes['monitoramento']:
            print(f"\n👀 MONITORAMENTO:")
            for item in recomendacoes['monitoramento']:
                print(f"  • {item}")
        
        # Armazenar para relatório
        resultado['recomendacoes'] = recomendacoes
        resultado['dados_cenario'] = dados
        resultados.append(resultado)
    
    return resultados


def gerar_relatorio_executivo(resultados, caminho_salvar="../models/"):
    """Gera relatório executivo em formato JSON e texto"""
    print(f"\n📄 GERANDO RELATÓRIO EXECUTIVO")
    print("=" * 50)
    
    # Preparar dados do relatório
    relatorio = {
        'metadata': {
            'data_geracao': datetime.now().isoformat(),
            'total_cenarios': len(resultados),
            'versao_sistema': '1.0'
        },
        'resumo_executivo': {},
        'cenarios': resultados
    }
    
    # Resumo executivo
    classes_contagem = {}
    for resultado in resultados:
        classe = resultado['classe']
        classes_contagem[classe] = classes_contagem.get(classe, 0) + 1
    
    relatorio['resumo_executivo'] = {
        'distribuicao_classes': classes_contagem,
        'cenarios_criticos': len([r for r in resultados if r['predicao'] >= 2]),
        'cenarios_adequados': len([r for r in resultados if r['predicao'] < 2]),
        'confianca_media': np.mean([r['confianca'] for r in resultados])
    }
    
    # Salvar JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    arquivo_json = os.path.join(caminho_salvar, f"relatorio_executivo_{timestamp}.json")
    
    with open(arquivo_json, 'w', encoding='utf-8') as f:
        json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"💾 Relatório JSON salvo: {arquivo_json}")
    
    # Gerar relatório em texto
    arquivo_txt = os.path.join(caminho_salvar, f"relatorio_executivo_{timestamp}.txt")
    
    with open(arquivo_txt, 'w', encoding='utf-8') as f:
        f.write("🍯 RELATÓRIO EXECUTIVO - CLASSIFICADOR DE PROBABILIDADES MEL\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"📊 Total de cenários analisados: {len(resultados)}\n\n")
        
        f.write("📈 RESUMO EXECUTIVO:\n")
        f.write("-" * 30 + "\n")
        f.write(f"• Cenários críticos (MÉDIA/ALTA): {relatorio['resumo_executivo']['cenarios_criticos']}\n")
        f.write(f"• Cenários adequados (DESPREZÍVEL/BAIXA): {relatorio['resumo_executivo']['cenarios_adequados']}\n")
        f.write(f"• Confiança média do modelo: {relatorio['resumo_executivo']['confianca_media']:.1%}\n\n")
        
        f.write("🎯 DISTRIBUIÇÃO POR CLASSE:\n")
        f.write("-" * 30 + "\n")
        for classe, count in classes_contagem.items():
            pct = (count / len(resultados)) * 100
            f.write(f"• {classe}: {count} cenários ({pct:.1f}%)\n")
        
        f.write(f"\n\n📋 DETALHES DOS CENÁRIOS:\n")
        f.write("=" * 50 + "\n")
        
        for resultado in resultados:
            f.write(f"\n🏷️ {resultado['nome']}\n")
            f.write("-" * 30 + "\n")
            f.write(f"Classificação: {resultado['classe']}\n")
            f.write(f"Confiança: {resultado['confianca']:.1%}\n")
            f.write(f"Urgência: {resultado['recomendacoes']['nivel_urgencia']}\n")
            f.write(f"Prazo: {resultado['recomendacoes']['prazo']}\n\n")
            
            if resultado['recomendacoes']['acoes_imediatas']:
                f.write("AÇÕES IMEDIATAS:\n")
                for acao in resultado['recomendacoes']['acoes_imediatas']:
                    f.write(f"• {acao}\n")
                f.write("\n")
    
    print(f"📄 Relatório TXT salvo: {arquivo_txt}")
    
    return arquivo_json, arquivo_txt


def comparar_modelos_salvos(caminho_modelos="../models/"):
    """Compara performance de modelos salvos"""
    print(f"\n⚖️ COMPARAÇÃO DE MODELOS SALVOS")
    print("=" * 50)
    
    # Buscar arquivos de modelos
    modelos_encontrados = []
    
    for arquivo in os.listdir(caminho_modelos):
        if arquivo.startswith('modelo_') and arquivo.endswith('.pkl'):
            nome_modelo = arquivo.replace('modelo_', '').replace('_mel.pkl', '').replace('_', ' ').title()
            caminho_completo = os.path.join(caminho_modelos, arquivo)
            modelos_encontrados.append((nome_modelo, caminho_completo))
    
    if not modelos_encontrados:
        print("❌ Nenhum modelo encontrado")
        return
    
    print(f"📊 Modelos encontrados: {len(modelos_encontrados)}")
    
    # Carregar scaler
    caminho_scaler = os.path.join(caminho_modelos, "scaler_mel.pkl")
    if not os.path.exists(caminho_scaler):
        print("❌ Scaler não encontrado")
        return
    
    scaler = joblib.load(caminho_scaler)
    
    # Testar cada modelo
    cenarios = criar_cenarios_teste()
    comparacao = {}
    
    for nome_modelo, caminho_modelo in modelos_encontrados:
        try:
            modelo = joblib.load(caminho_modelo)
            
            # Testar em cenários
            acertos = 0
            total = 0
            
            for nome_cenario, dados in cenarios.items():
                cenario_df = pd.DataFrame([dados])
                cenario_scaled = scaler.transform(cenario_df)
                
                predicao = modelo.predict(cenario_scaled)[0]
                probabilidades = modelo.predict_proba(cenario_scaled)[0]
                confianca = probabilidades[predicao]
                
                # Critério simples: cenário crítico deve ter probabilidade >= 2
                if nome_cenario == "Situação Crítica" and predicao >= 2:
                    acertos += 1
                elif nome_cenario == "Produtor Exemplar" and predicao <= 1:
                    acertos += 1
                elif nome_cenario in ["Produtor Médio", "Produtor com Falhas"] and 1 <= predicao <= 2:
                    acertos += 1
                
                total += 1
            
            taxa_acerto = (acertos / total) * 100
            comparacao[nome_modelo] = {
                'taxa_acerto_cenarios': taxa_acerto,
                'modelo_carregado': True
            }
            
            print(f"✅ {nome_modelo}: {taxa_acerto:.1f}% acerto nos cenários")
            
        except Exception as e:
            print(f"❌ Erro ao carregar {nome_modelo}: {e}")
            comparacao[nome_modelo] = {
                'taxa_acerto_cenarios': 0,
                'modelo_carregado': False,
                'erro': str(e)
            }
    
    # Identificar melhor modelo
    if comparacao:
        melhor_modelo = max(comparacao.keys(), key=lambda x: comparacao[x]['taxa_acerto_cenarios'])
        print(f"\n🏆 Melhor modelo nos cenários: {melhor_modelo}")
    
    return comparacao


def gerar_relatorio_completo_sistema(caminho_modelo="../models/melhor_modelo_mel.pkl",
                                   caminho_scaler="../models/scaler_mel.pkl"):
    """
    Função principal para gerar relatório completo do sistema
    """
    print(f"🍯 GERADOR DE RELATÓRIOS COMPLETO - SISTEMA MEL")
    print("=" * 70)
    
    # Carregar modelo
    modelo, scaler = carregar_modelo_treinado(caminho_modelo, caminho_scaler)
    
    if modelo is None or scaler is None:
        print("❌ Não foi possível carregar o modelo")
        return
    
    # Simular cenários
    resultados = simular_cenarios_completos(modelo, scaler)
    
    # Gerar relatório executivo
    arquivo_json, arquivo_txt = gerar_relatorio_executivo(resultados)
    
    # Comparar modelos
    comparacao = comparar_modelos_salvos()
    
    print(f"\n✅ RELATÓRIO COMPLETO GERADO")
    print(f"📄 Arquivos gerados:")
    print(f"  • JSON: {arquivo_json}")
    print(f"  • TXT: {arquivo_txt}")
    
    return resultados, arquivo_json, arquivo_txt


if __name__ == "__main__":
    print("🍯 GERADOR DE RELATÓRIOS - PRODUÇÃO DE MEL")
    print("=" * 50)
    
    # Verificar se existem modelos
    if os.path.exists("../models/melhor_modelo_mel.pkl"):
        gerar_relatorio_completo_sistema()
    else:
        print("❌ Modelos não encontrados. Execute primeiro o classificador_mel.py")
        print("💡 Comparando modelos existentes...")
        comparar_modelos_salvos()