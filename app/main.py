from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.routes import etapa
from app.routes import questionario
from app.routes import avaliar

app = FastAPI()

# Habilita CORS para permitir requisições do navegador (ex: localhost:5500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, substitua pelo domínio final ["https://seusite.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas da API
app.include_router(etapa.router)
app.include_router(questionario.router)
app.include_router(avaliar.router)

# Serve arquivos estáticos como CSS, JS e imagens
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

# Rota principal que serve o index.html
@app.get("/", response_class=HTMLResponse)
def home():
    html_path = Path(__file__).parent / "static" / "index.html"
    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content, status_code=200)
