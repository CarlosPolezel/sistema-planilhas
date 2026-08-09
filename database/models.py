#type: ignore
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
#type: ignore
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    senha_hash = Column(String, nullable=False)
    nivel_acesso = Column(String, nullable=False, default='Padrao')  # 'Admin', 'Supervisor', 'Padrao'
    setor = Column(String, nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Auditoria(Base):
    __tablename__ = 'auditoria'

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True)
    usuario_nome = Column(String, nullable=False)
    acao = Column(String, nullable=False)
    entidade = Column(String, nullable=False)
    registro_id = Column(Integer, nullable=True)
    detalhes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)

class RegistroDesmoldante(Base):
    __tablename__ = 'registros_desmoldante'

    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, nullable=False)
    periodo = Column(String, nullable=False)
    mes = Column(String, nullable=True)
    ano = Column(Integer, nullable=True)
    pesagem_1 = Column(Float, nullable=True)
    pesagem_2 = Column(Float, nullable=True)
    diferenca = Column(Float, nullable=True)
    producao = Column(Integer, nullable=True)
    compacta = Column(Integer, nullable=True)
    arrancada = Column(Integer, nullable=True)
    qtd_descarte = Column(Integer, nullable=True)
    observacao = Column(Text, nullable=True)
    
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    criado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    atualizado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=True)

class RegistroSolaArrancada(Base):
    __tablename__ = 'registros_sola_arrancada'

    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, nullable=False)
    maquina = Column(String, nullable=False)
    turno = Column(String, nullable=False)
    tamanho = Column(String, nullable=True)
    quantidade = Column(Integer, nullable=False)
    motivo = Column(String, nullable=False)
    observacao = Column(Text, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    criado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    atualizado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=True)

class RegistroDescarte(Base):
    __tablename__ = 'registros_descarte'

    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, nullable=False)
    maquina = Column(String, nullable=False)
    turno = Column(String, nullable=False)
    matriz = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    reduzido = Column(String, nullable=True)
    tamanho = Column(String, nullable=True)
    quantidade = Column(Integer, nullable=False)
    motivo = Column(String, nullable=False)
    ficha = Column(String, nullable=True)
    observacao = Column(Text, nullable=True)

    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    criado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    atualizado_por = Column(Integer, ForeignKey('usuarios.id'), nullable=True)