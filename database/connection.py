import os
#type: ignore
from sqlalchemy import create_engine
#type: ignore
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Lê a URL do banco de dados da variável de ambiente ou usa o SQLite local como padrão
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sistema.db")

# Ajuste de thread necessário para SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def criar_bd():
    """Cria todas as tabelas no banco de dados se não existirem."""
    Base.metadata.create_all(bind=engine)