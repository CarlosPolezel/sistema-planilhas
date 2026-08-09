from database.connection import criar_bd, SessionLocal
from database.models import Usuario
#type: ignore
import bcrypt

print("A criar a base de dados e as tabelas...")
criar_bd()

# Inicia a ligação
db = SessionLocal()

# Verifica se o admin já existe para não criar duplicados
admin_existente = db.query(Usuario).filter(Usuario.username == "admin").first()

if not admin_existente:
    print("A gerar o primeiro utilizador Admin...")
    # Usa o bcrypt para criar o hash da palavra-passe 'admin123'
    senha_plana = "admin123".encode('utf-8')
    salt = bcrypt.gensalt()
    senha_hash = bcrypt.hashpw(senha_plana, salt).decode('utf-8')
    
    novo_admin = Usuario(
        nome="Administrador Principal",
        username="admin",
        senha_hash=senha_hash,
        nivel_acesso="Admin",
        setor="Todos"
    )
    db.add(novo_admin)
    db.commit()
    print("Sucesso! Utilizador Admin criado (Username: admin | Password: admin123)")
else:
    print("A base de dados já está pronta e o Admin já existe.")

db.close()