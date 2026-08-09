#type: ignore
from sqlalchemy.orm import Session
from database.repositories import UsuarioRepository, AuditoriaRepository
from utils.auth import verificar_senha

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UsuarioRepository(db)
        self.audit_repo = AuditoriaRepository(db)

    def autenticar(self, username: str, password_plana: str):
        usuario = self.user_repo.buscar_por_username(username)

        # 1. Utilizador não encontrado
        if not usuario:
            self.audit_repo.registrar(
                usuario_id=None,
                usuario_nome=username or "desconhecido",
                acao="LOGIN_FALHA",
                entidade="usuarios",
                detalhes="Tentativa de login com utilizador inexistente."
            )
            return False, "Utilizador ou palavra-passe incorretos.", None

        # 2. Utilizador inativo
        if not usuario.ativo:
            self.audit_repo.registrar(
                usuario_id=usuario.id,
                usuario_nome=usuario.nome,
                acao="LOGIN_FALHA",
                entidade="usuarios",
                detalhes="Tentativa de login em conta inativa."
            )
            return False, "Esta conta de utilizador está inativa. Contacte o supervisor.", None

        # 3. Palavra-passe incorreta
        if not verificar_senha(password_plana, usuario.senha_hash):
            self.audit_repo.registrar(
                usuario_id=usuario.id,
                usuario_nome=usuario.nome,
                acao="LOGIN_FALHA",
                entidade="usuarios",
                detalhes="Palavra-passe incorreta."
            )
            return False, "Utilizador ou palavra-passe incorretos.", None

        # 4. Login bem-sucedido
        self.audit_repo.registrar(
            usuario_id=usuario.id,
            usuario_nome=usuario.nome,
            acao="LOGIN_SUCESSO",
            entidade="usuarios",
            detalhes="Sessão iniciada com sucesso."
        )
        return True, "Login realizado com sucesso!", usuario

    def registrar_logout(self, usuario_id: int, usuario_nome: str):
        if usuario_id:
            self.audit_repo.registrar(
                usuario_id=usuario_id,
                usuario_nome=usuario_nome,
                acao="LOGOUT",
                entidade="usuarios",
                detalhes="Sessão encerrada pelo utilizador."
            )

def registrar_exportacao(self, usuario_id: int, usuario_nome: str, modulo: str):
        self.audit_repo.registrar(
            usuario_id=usuario_id,
            usuario_nome=usuario_nome,
            acao="EXPORTACAO_REALIZADA",
            entidade=modulo,
            detalhes=f"O utilizador exportou os dados do módulo {modulo}."
        )