from database.connection import criar_bd, SessionLocal, engine
from database.models import Base, Usuario
from database.repositories import UsuarioRepository
#type: ignore
import bcrypt

print("Recriando as tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)

db = SessionLocal()
user_repo = UsuarioRepository(db)

admin_existente = user_repo.buscar_por_username("admin")

if not admin_existente:
    print("Gerando o usuário Administrador padrão...")
    senha_plana = "admin123".encode('utf-8')
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_plana, salt).decode('utf-8')
    
    novo_admin = Usuario(
        nome="Administrador Principal",
        username="admin",
        senha_hash=senha_hash,
        nivel_acesso="Admin",
        setor="Todos",
        ativo=True
    )
    user_repo.criar(novo_admin)
    print("Administrador criado com sucesso! (Username: admin | Password: admin123)")
else:
    print("O banco de dados já está configurado e o usuário admin já existe.")

db.close()