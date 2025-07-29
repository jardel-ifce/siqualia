# 📁 app/main.py

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Rotas de IA
from app.routes.ia import etapas as ia_etapas
from app.routes.ia import resumo as ia_resumo

# Rotas de CRUD
from app.routes.crud import produtos as crud_produtos
from app.routes.crud import etapas as crud_etapas
from app.routes.crud import perigos as crud_perigos
from app.routes.crud import questionario as crud_questionario
from app.routes.crud import resumo as crud_resumo

# Instância do app
app = FastAPI(
    title="SIQUALIA API",
    version="1.0.0"
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção: restringir ao domínio da aplicação
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusão de rotas
## CRUD
app.include_router(crud_produtos.router)
app.include_router(crud_etapas.router)
app.include_router(crud_perigos.router)
app.include_router(crud_questionario.router)
app.include_router(crud_resumo.router)

## IA
app.include_router(ia_etapas.router)
app.include_router(ia_resumo.router)

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
app.mount("/avaliacoes", StaticFiles(directory="avaliacoes"), name="avaliacoes")

# Página inicial
@app.get("/", response_class=HTMLResponse)
def home():
    html_path = Path(__file__).parent / "static" / "index.html"
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)
