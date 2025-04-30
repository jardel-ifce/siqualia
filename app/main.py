# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import produto, rag, etapa_rag, formulario

app = FastAPI(title="SIQUALIA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produto.router)
app.include_router(rag.router)
app.include_router(etapa_rag.router)

app.include_router(formulario.router)
