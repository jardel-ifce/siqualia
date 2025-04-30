import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
# from sqlalchemy import text

load_dotenv()

# Configuração da conexão
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não está definido no ambiente.")

# Criação do engine de conexão
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10
)

# SessionLocal será utilizado nas rotas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para os modelos ORM
Base = declarative_base()

# Função de dependência para ser usada nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Função opcional de teste de conexão
# def testar_conexao():
#     try:
#         with engine.connect() as connection:
#             connection.execute(text("SELECT 1;"))
#             print("Conexão bem-sucedida com o banco Neon!")
#     except Exception as e:
#         print("Erro ao conectar com o Neon:", e)
#
# # Se quiser testar diretamente
# if __name__ == "__main__":
#     testar_conexao()
