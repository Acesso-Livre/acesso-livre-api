import secrets, string
import re

from ..func_log import log_message

def gen_code_for_reset_password() -> str:
    """Gera um código aleatório de 10 caracteres para reset de senha."""
    alphabet = string.ascii_letters + string.digits + '!@#$%&*'
    log_message("Gerando código aleatório para reset de senha", level="debug", logger_name="acesso_livre_api")
    return ''.join(secrets.choice(alphabet) for _ in range(10))

def is_strong_password(password: str) -> bool:
    """Verifica se a senha atende aos requisitos mínimos de segurança usando regex."""
    pattern = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")
    log_message("Verificando força da senha fornecida", level="debug", logger_name="acesso_livre_api")
    return bool(pattern.match(password))