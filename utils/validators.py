import re

def validar_username(username):
    """
    Previne Injection e padroniza os logins.
    Regra: Apenas letras e números, sem espaços ou símbolos especiais, entre 3 e 20 caracteres.
    """
    if not re.match(r"^[a-zA-Z0-9]{3,20}$", username):
        return False, "O login deve ter entre 3 e 20 caracteres, contendo apenas letras e números."
    return True, ""

def validar_senha(senha):
    """
    Previne senhas fracas (Broken Authentication).
    Regra: Mínimo de 8 caracteres, contendo pelo menos uma letra e um número.
    """
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."
    if not re.search(r"[A-Za-z]", senha) or not re.search(r"[0-9]", senha):
        return False, "A senha deve conter pelo menos uma letra e um número."
    return True, ""

def sanitizar_texto(texto):
    """
    Previne XSS (Cross-Site Scripting).
    Remove qualquer tentativa de inserir tags HTML (ex: <script>) no nome do usuário.
    """
    if not texto:
        return ""
    texto_limpo = re.sub(r'<[^>]*>', '', texto)
    return texto_limpo.strip()