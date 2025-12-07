import secrets, string
import re

from func_log import *

def gen_code_for_reset_password() -> str:
    """Gera um código aleatório de 10 caracteres para reset de senha."""
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    log_message("Código de reset de senha gerado.", level="info")
    return ''.join(secrets.choice(alphabet) for _ in range(10))

def is_strong_password(password: str) -> bool:
    """Verifica se a senha atende aos requisitos mínimos de segurança usando regex."""
    pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")
    log_message("Verificação de força da senha realizada.", level="info")
    return bool(pattern.match(password))