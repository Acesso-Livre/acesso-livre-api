from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from . import service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login")

def require_auth(endpoint_func):
    """Decorator para marcar endpoints que precisam de autenticação no Swagger"""
    endpoint_func._requires_auth = True
    return endpoint_func

def simple_token_verification(token: str = Depends(oauth2_scheme)) -> bool:
    """
    Verifica se o token é válido. Se não for, lança um erro 401.
    Esta dependência centraliza a lógica de autenticação.
    Retorna True se o token for válido.
    """
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not service.verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

authenticated_user = Depends(simple_token_verification)