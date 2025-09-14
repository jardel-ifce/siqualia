# 🗑️ Script de Reset - Sistema de Classificação de Mel

## 📋 Descrição

O script `reset.py` remove **TODOS** os modelos treinados e resultados gerados pelo sistema de classificação de mel. Esta operação é **IRREVERSÍVEL**.

## 🎯 O que é removido

### 📁 Modelos Treinados (`/models/`)
- Arquivos `.pkl` (modelos treinados)
- Arquivos `scaler_*.pkl` (normalizadores)
- Arquivos `config_*.json` (configurações)

### 📊 Resultados de Análise (`/results/`)
- Gráficos `.png` (visualizações dos resultados)
- Relatórios `.txt` (métricas detalhadas)

### 🔮 Resultados de Predição (`/results_trained_models/`)
- Arquivos de predição `.txt` (resultados de classificações)

## 🚀 Como usar

### Opção 1: Script Python (Recomendado)
```bash
cd /path/to/siqualia-ia-main/ml
python reset.py
```

### Opção 2: Script Shell
```bash
cd /path/to/siqualia-ia-main/ml
./reset.sh
```

## 🔍 Funcionalidades

### ✅ Análise Prévia
- Mostra quantos arquivos serão removidos
- Calcula o espaço que será liberado
- Lista exemplos de arquivos encontrados

### 🛡️ Segurança
- Solicita confirmação explícita do usuário
- Digite `CONFIRMAR` para executar
- Digite `CANCELAR` para abortar
- Operação pode ser interrompida com `Ctrl+C`

### 📊 Relatório Final
- Confirma quais arquivos foram removidos
- Informa quanto espaço foi liberado
- Registra data/hora da operação

## ⚠️ Importante

- **OPERAÇÃO IRREVERSÍVEL**: Não há como recuperar os arquivos removidos
- **USE COM CUIDADO**: Todos os modelos treinados serão perdidos
- **BACKUP**: Faça backup antes se necessário

## 📝 Exemplo de Execução

```
🍯 SCRIPT DE RESET - SISTEMA DE CLASSIFICAÇÃO DE MEL
============================================================
⚠️  REMOVE TODOS OS MODELOS TREINADOS E RESULTADOS GERADOS
============================================================
🔍 ANÁLISE DO SISTEMA ATUAL
==================================================

📁 Modelos Treinados
   Pasta: models
   Descrição: Modelos .pkl, scalers e configurações
   Arquivos: 8
   Tamanho: 1.2 MB

📁 Resultados de Análise
   Pasta: results
   Descrição: Gráficos .png e relatórios .txt
   Arquivos: 15
   Tamanho: 3.8 MB

📊 RESUMO TOTAL:
   Total de arquivos: 23
   Tamanho total: 5.0 MB

⚠️  ATENÇÃO: OPERAÇÃO IRREVERSÍVEL!
🗑️  Serão removidos 23 arquivo(s)
💾 Liberando 5.0 MB de espaço

🤔 Tem certeza que deseja continuar?
   Digite 'CONFIRMAR' para prosseguir ou 'CANCELAR' para abortar:
```

## 🆘 Em caso de problemas

- Verifique se está na pasta `/ml/` correta
- Certifique-se que Python está instalado
- Execute com permissões adequadas
- Interrompa com `Ctrl+C` se necessário