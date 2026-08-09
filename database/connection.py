#type: ignore
from sqlalchemy import create_engine
#type: ignore
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Definimos o uso do SQLite localmente para esta fase de testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./sistema.db"

# O argumento 'check_same_thread' é obrigatório no SQLite quando usamos Streamlit
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Cria a sessão que usaremos para fazer as consultas (queries)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def criar_bd():
    """Função para criar as tabelas na base de dados caso não existam."""
    Base.metadata.create_all(bind=engine)