import secrets, string

def gen_code_for_reset_password() -> str:
    """Gera um código aleatório de 10 caracteres para reset de senha."""
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    return ''.join(secrets.choice(alphabet) for _ in range(10))