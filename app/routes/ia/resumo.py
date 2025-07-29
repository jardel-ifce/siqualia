# app/routes/ia/resumo.py

# 📦 Bibliotecas externas
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# 📁 Serviços internos
from app.services.ia.consultar_resumo import sugerir_resumo_dados

# 🔧 Inicialização do modelo de embeddings
model = SentenceTransformer("msmarco-distilbert-base-v4")

# 🔧 Configuração da rota
router = APIRouter(prefix="/ia", tags=["IA - Resumo"])

# 📋 Perguntas do Formulário I
PERGUNTAS_FORM_I = {
    "limite_critico": "Qual o limite crítico necessário para garantir que esse perigo esteja sob controle?",
    "monitoramento.oque": "O que deve ser monitorado para garantir o controle desse perigo?",
    "monitoramento.como": "Como o monitoramento deve ser realizado?",
    "monitoramento.quando": "Com que frequência o monitoramento deve ocorrer?",
    "monitoramento.quem": "Quem é o responsável por realizar o monitoramento?",
    "acao_corretiva": "Qual ação corretiva deve ser tomada se o perigo não estiver controlado?",
    "registro": "Quais registros devem ser mantidos para comprovar o controle?",
    "verificacao": "Como verificar se o controle do perigo está sendo efetivo?"
}

# 📦 Modelo de entrada para sugestão
class ResumoRequest(BaseModel):
    produto: str
    etapa: str
    id_perigo: int
    tipo: str
    perigo: str
    justificativa: str
    medida: str

# 🧠 Função de geração de prompt contextualizado
def gerar_prompt(ctx, pergunta):
    return (
        f"query: Produto: {ctx['produto']}. Etapa: {ctx['etapa']}. "
        f"Perigo identificado: ({ctx['tipo']}) {ctx['perigo']}. "
        f"Medida preventiva: {ctx['medida']}. Justificativa: {ctx['justificativa']}. {pergunta}"
    )

# 🔍 Rota de sugestão de dados para o Formulário I
@router.post("/resumo/sugerir")
def sugerir_resumo(req: ResumoRequest):
    dados = sugerir_resumo_dados(
        req.produto, req.etapa, req.tipo,
        req.perigo, req.medida, req.justificativa
    )
    if not dados:
        raise HTTPException(status_code=404, detail="Não foi possível sugerir os dados do Formulário I.")
    return {"mensagem": "Sugestão gerada com sucesso", "resumo": dados}
