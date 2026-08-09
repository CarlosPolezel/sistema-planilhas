#type: ignore
from sqlalchemy import Column, Integer, String
#type: ignore
from sqlalchemy.orm import declarative_base

# Cria a classe base para os nossos modelos
Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    
    # Níveis de acesso: 'Admin', 'Supervisor', ou 'Padrao'
    nivel_acesso = Column(String, nullable=False, default='Padrao')
    
    # Setor ao qual o utilizador pertence (ex: 'Desma'). 
    # Pode ser nulo para o Admin, que tem acesso a tudo.
    setor = Column(String, nullable=True)