# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Rotas IA
from app.routes.ia import etapas as ia_etapas

# Rotas CRUD
from app.routes.crud import produtos as crud_produtos
from app.routes.crud import etapas as crud_etapas
from app.routes.crud import perigos as crud_perigos
from app.routes.crud import questionario as crud_questionario
from app.routes.crud import resumo as crud_resumo

# Fluxo do questionário (Formulário H)
# from app.routes.questionario.assistente import assistente

app = FastAPI(
    title="SIQUALIA API",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # lembrar: em produção, restringir ao domínio da aplicação
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão de rotas
app.include_router(crud_produtos.router)
app.include_router(crud_etapas.router)
app.include_router(ia_etapas.router)
app.include_router(crud_perigos.router)
app.include_router(crud_resumo.router)
app.include_router(crud_questionario.router)


# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.mount("/avaliacoes", StaticFiles(directory="avaliacoes"), name="avaliacoes")

# Rota raiz com página HTML
@app.get("/", response_class=HTMLResponse)
def home():
    html_path = Path(__file__).parent / "static" / "index.html"
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)
