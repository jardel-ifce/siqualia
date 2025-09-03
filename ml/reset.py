"""
SCRIPT DE RESET - SISTEMA DE CLASSIFICAÇÃO DE MEL
================================================
Remove todos os modelos treinados e resultados gerados

ATENÇÃO: Esta operação é IRREVERSÍVEL!
"""

import os
import shutil
from datetime import datetime

def contar_arquivos_pasta(pasta):
    """Conta quantos arquivos existem numa pasta"""
    if not os.path.exists(pasta):
        return 0
    
    total = 0
    for root, dirs, files in os.walk(pasta):
        total += len(files)
    return total

def listar_conteudo_pasta(pasta, mostrar_max=10):
    """Lista o conteúdo de uma pasta limitando a quantidade"""
    if not os.path.exists(pasta):
        return []
    
    arquivos = []
    for root, dirs, files in os.walk(pasta):
        for file in files:
            if len(arquivos) < mostrar_max:
                arquivos.append(os.path.relpath(os.path.join(root, file), pasta))
    
    return arquivos

def calcular_tamanho_pasta(pasta):
    """Calcula o tamanho total de uma pasta em MB"""
    if not os.path.exists(pasta):
        return 0
    
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(pasta):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                pass
    
    return total_size / (1024 * 1024)  # Converter para MB

def exibir_status_atual():
    """Mostra o status atual dos arquivos que serão removidos"""
    print("🔍 ANÁLISE DO SISTEMA ATUAL")
    print("=" * 50)
    
    # Determinar caminho base
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    pastas_para_limpar = [
        {
            'nome': 'Modelos Treinados',
            'pasta': os.path.join(script_dir, 'models'),
            'descricao': 'Modelos .pkl, scalers e configurações'
        },
        {
            'nome': 'Resultados de Análise',
            'pasta': os.path.join(script_dir, 'results'),
            'descricao': 'Gráficos .png e relatórios .txt'
        },
        {
            'nome': 'Resultados de Predição',
            'pasta': os.path.join(script_dir, 'results_trained_models'),
            'descricao': 'Resultados das predições realizadas'
        }
    ]
    
    total_arquivos = 0
    total_tamanho = 0
    
    for pasta_info in pastas_para_limpar:
        pasta = pasta_info['pasta']
        arquivos = contar_arquivos_pasta(pasta)
        tamanho = calcular_tamanho_pasta(pasta)
        
        total_arquivos += arquivos
        total_tamanho += tamanho
        
        print(f"\n📁 {pasta_info['nome']}")
        print(f"   Pasta: {os.path.relpath(pasta, script_dir)}")
        print(f"   Descrição: {pasta_info['descricao']}")
        print(f"   Arquivos: {arquivos}")
        print(f"   Tamanho: {tamanho:.1f} MB")
        
        if arquivos > 0:
            print(f"   Exemplos:")
            exemplos = listar_conteudo_pasta(pasta, 5)
            for exemplo in exemplos:
                print(f"     • {exemplo}")
            if arquivos > 5:
                print(f"     ... e mais {arquivos - 5} arquivo(s)")
    
    print(f"\n📊 RESUMO TOTAL:")
    print(f"   Total de arquivos: {total_arquivos}")
    print(f"   Tamanho total: {total_tamanho:.1f} MB")
    
    return pastas_para_limpar, total_arquivos, total_tamanho

def confirmar_remocao(total_arquivos, total_tamanho):
    """Solicita confirmação do usuário para remover os arquivos"""
    print(f"\n⚠️  ATENÇÃO: OPERAÇÃO IRREVERSÍVEL!")
    print("=" * 40)
    print(f"🗑️  Serão removidos {total_arquivos} arquivo(s)")
    print(f"💾 Liberando {total_tamanho:.1f} MB de espaço")
    print(f"⏰ Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    print(f"\n❌ ESTA AÇÃO NÃO PODE SER DESFEITA!")
    print("   • Todos os modelos treinados serão perdidos")
    print("   • Todos os resultados de análise serão perdidos")
    print("   • Todas as predições salvas serão perdidas")
    
    print(f"\n🤔 Tem certeza que deseja continuar?")
    
    while True:
        resposta = input("   Digite 'CONFIRMAR' para prosseguir ou 'CANCELAR' para abortar: ").strip().upper()
        
        if resposta == 'CONFIRMAR':
            return True
        elif resposta == 'CANCELAR':
            return False
        else:
            print("   ❌ Resposta inválida! Digite 'CONFIRMAR' ou 'CANCELAR'")

def limpar_pasta(pasta, nome_pasta):
    """Remove todo o conteúdo de uma pasta de forma segura"""
    if not os.path.exists(pasta):
        print(f"   ⚠️  {nome_pasta}: Pasta não existe - ignorando")
        return True
    
    try:
        # Contar arquivos antes
        arquivos_antes = contar_arquivos_pasta(pasta)
        
        if arquivos_antes == 0:
            print(f"   ✅ {nome_pasta}: Já vazia - nada a fazer")
            return True
        
        print(f"   🔄 {nome_pasta}: Removendo {arquivos_antes} arquivo(s)...")
        
        # Remover conteúdo mas manter a pasta
        for item in os.listdir(pasta):
            item_path = os.path.join(pasta, item)
            
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        
        # Verificar se está vazia
        arquivos_depois = contar_arquivos_pasta(pasta)
        
        if arquivos_depois == 0:
            print(f"   ✅ {nome_pasta}: Limpeza concluída!")
            return True
        else:
            print(f"   ❌ {nome_pasta}: Erro - ainda restam {arquivos_depois} arquivo(s)")
            return False
            
    except Exception as e:
        print(f"   ❌ {nome_pasta}: Erro durante limpeza - {str(e)}")
        return False

def executar_reset():
    """Executa o reset completo do sistema"""
    print("🍯 SCRIPT DE RESET - SISTEMA DE CLASSIFICAÇÃO DE MEL")
    print("=" * 60)
    print("⚠️  REMOVE TODOS OS MODELOS TREINADOS E RESULTADOS GERADOS")
    print("=" * 60)
    
    # 1. Mostrar status atual
    pastas_para_limpar, total_arquivos, total_tamanho = exibir_status_atual()
    
    if total_arquivos == 0:
        print(f"\n🎉 SISTEMA JÁ ESTÁ LIMPO!")
        print("   Não há arquivos para remover.")
        return
    
    # 2. Confirmar com o usuário
    if not confirmar_remocao(total_arquivos, total_tamanho):
        print(f"\n🚫 OPERAÇÃO CANCELADA PELO USUÁRIO")
        print("   Nenhum arquivo foi removido.")
        return
    
    # 3. Executar limpeza
    print(f"\n🗑️  INICIANDO LIMPEZA DO SISTEMA...")
    print("=" * 40)
    
    sucesso_total = True
    
    for pasta_info in pastas_para_limpar:
        resultado = limpar_pasta(pasta_info['pasta'], pasta_info['nome'])
        if not resultado:
            sucesso_total = False
    
    # 4. Relatório final
    print(f"\n📋 RELATÓRIO FINAL")
    print("=" * 25)
    
    if sucesso_total:
        print(f"✅ RESET CONCLUÍDO COM SUCESSO!")
        print(f"   • {total_arquivos} arquivo(s) removido(s)")
        print(f"   • {total_tamanho:.1f} MB liberado(s)")
        print(f"   • Sistema limpo e pronto para novos treinamentos")
    else:
        print(f"⚠️  RESET CONCLUÍDO COM ALGUNS ERROS")
        print(f"   Verifique as mensagens acima para detalhes")
    
    print(f"\n⏰ Concluído em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

def main():
    """Função principal"""
    try:
        executar_reset()
    except KeyboardInterrupt:
        print(f"\n\n🚫 OPERAÇÃO INTERROMPIDA PELO USUÁRIO")
        print("   Reset cancelado - nenhum arquivo foi removido.")
    except Exception as e:
        print(f"\n\n❌ ERRO INESPERADO: {str(e)}")
        print("   Reset interrompido por segurança.")

if __name__ == "__main__":
    main()