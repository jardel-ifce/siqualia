from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import produtos, etapas, avaliacoes, formulario_i

app = FastAPI(
    title="SIQUALIA IA MODULE API",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Primeiro registre as rotas da API
app.include_router(produtos.router)
app.include_router(etapas.router)
app.include_router(avaliacoes.router)

app.include_router(formulario_i.router)

# ✅ Só depois monte os arquivos estáticos
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
