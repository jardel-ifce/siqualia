#!/bin/bash
# ml/reset.sh

# SCRIPT DE RESET - SISTEMA DE CLASSIFICAÇÃO DE MEL
# ==================================================
# Wrapper shell para executar o reset Python de forma interativa

echo "🍯 RESET - SISTEMA DE CLASSIFICAÇÃO DE MEL"
echo "=========================================="
echo ""

# Verificar se está no diretório correto
if [[ ! -f "reset.py" ]]; then
    echo "❌ ERRO: Este script deve ser executado na pasta /ml/"
    echo "   Navegue para a pasta /ml/ e execute novamente."
    exit 1
fi

# Verificar se Python está disponível
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ ERRO: Python não encontrado"
    echo "   Instale Python para executar este script."
    exit 1
fi

# Determinar comando Python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "🔧 Executando script de reset com $PYTHON_CMD..."
echo ""

# Executar o script Python
$PYTHON_CMD reset.py

echo ""
echo "🏁 Script finalizado."