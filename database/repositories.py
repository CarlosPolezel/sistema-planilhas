#type: ignore
from sqlalchemy.orm import Session
from database.models import Usuario, Auditoria, RegistroDesmoldante, RegistroSolaArrancada, RegistroDescarte

class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_username(self, username: str) -> Usuario:
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def buscar_por_id(self, usuario_id: int) -> Usuario:
        return self.db.query(Usuario).filter(Usuario.id == usuario_id).first()

    def listar_todos(self):
        return self.db.query(Usuario).all()

    def criar(self, usuario: Usuario) -> Usuario:
        self.db.add(usuario)
        self.db.commit()
        self.db.refresh(usuario)
        return usuario


class AuditoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def registrar(self, usuario_id: int, usuario_nome: str, acao: str, entidade: str, registro_id: int = None, detalhes: str = None) -> Auditoria:
        log = Auditoria(
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao=acao,
            entidade=entidade,
            registro_id=registro_id,
            detalhes=detalhes
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

class RegistroDesmoldanteRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, registro: RegistroDesmoldante) -> RegistroDesmoldante:
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def listar_todos(self):
        # Retorna os registos ordenados do mais recente para o mais antigo
        return self.db.query(RegistroDesmoldante).order_by(RegistroDesmoldante.id.desc()).all()

class RegistroSolaArrancadaRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, registro: RegistroSolaArrancada) -> RegistroSolaArrancada:
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def listar_todos(self):
        return self.db.query(RegistroSolaArrancada).order_by(RegistroSolaArrancada.id.desc()).all()

class RegistroDescarteRepository:
    def __init__(self, db: Session):
        self.db = db

    def criar(self, registro: RegistroDescarte) -> RegistroDescarte:
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def listar_todos(self):
        return self.db.query(RegistroDescarte).order_by(RegistroDescarte.id.desc()).all()