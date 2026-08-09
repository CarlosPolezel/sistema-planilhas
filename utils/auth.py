#type: ignore
import bcrypt

def verificar_senha(senha_plana, senha_hash):
    """Compara a palavra-passe em texto plano com o hash guardado."""
    return bcrypt.checkpw(senha_plana.encode('utf-8'), senha_hash.encode('utf-8'))

def gerar_hash(senha_plana):
    """Gera um hash seguro para uma nova palavra-passe."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha_plana.encode('utf-8'), salt).decode('utf-8')