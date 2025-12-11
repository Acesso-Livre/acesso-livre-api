from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import service

from ..func_log import log_message

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login")

def require_auth(endpoint_func):
    """Decorator para marcar endpoints que precisam de autenticação no Swagger"""
    endpoint_func._requires_auth = True
    log_message(f"Endpoint {endpoint_func.__name__} requer autenticação", level="debug", logger_name="acesso_livre_api")
    return endpoint_func

def simple_token_verification(token: str = Depends(oauth2_scheme)) -> bool:
    """
    Verifica se o token é válido. Se não for, lança um erro 401.
    Esta dependência centraliza a lógica de autenticação.
    Retorna True se o token for válido.
    """
    if token is None:
        log_message("Token de autenticação não fornecido", level="warning", logger_name="acesso_livre_api")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not service.verify_token(token):
        log_message("Token inválido ou expirado", level="warning", logger_name="acesso_livre_api")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    log_message("Token de autenticação verificado com sucesso", level="info", logger_name="acesso_livre_api")
    return True

authenticated_user = Depends(simple_token_verification)