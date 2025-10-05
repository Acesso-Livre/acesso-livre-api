from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from functools import wraps
from . import service
from ..database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login", auto_error=False)

def require_auth(endpoint_func):
    """Decorator para marcar endpoints que precisam de autenticação no Swagger"""
    endpoint_func._requires_auth = True
    return endpoint_func

async def get_current_user_token(token: str = Depends(oauth2_scheme)):
    """
    Dependência para verificar se o token é válido sem exigir autenticação obrigatória
    """
    if not token:
        return None

    if not service.verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token

async def get_current_user_required(token: str = Depends(oauth2_scheme)):
    """
    Dependência para exigir token válido
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not service.verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token