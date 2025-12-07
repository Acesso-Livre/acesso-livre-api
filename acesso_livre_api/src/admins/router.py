from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from . import service, schemas, exceptions, dependencies
from ..database import get_db
from .dependencies import oauth2_scheme
from .docs import (
    REGISTER_DOCS,
    LOGIN_DOCS,
    CHECK_TOKEN_DOCS,
    FORGOT_PASSWORD_DOCS,
    PASSWORD_RESET_DOCS,
)

from func_log import *

router = APIRouter()
logger = logging.getLogger(__name__)


# TODO: Adicionar auth
@router.post(
    "/register",
    response_model=schemas.RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    **REGISTER_DOCS,
)
async def register_admin(admin: schemas.AdminCreate, db: AsyncSession = Depends(get_db)):
    await service.create_admin(db, admin)
    log_message(f"Novo admin registrado: {admin.email}", level="info")
    return {"status": "success"}


@router.post("/login", response_model=schemas.LoginResponse, **LOGIN_DOCS)
async def login(
    admin: schemas.LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    admin = await service.authenticate_admin(db, admin.email, admin.password)
    if not admin:
        log_message(f"Falha na autenticação para o admin: {admin.email}", level="warning")
        raise exceptions.AdminAuthenticationFailedException()

    access_token = service.create_access_token({"sub": admin.email})
    log_message(f"Admin autenticado com sucesso: {admin.email}", level="info")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/check-token", **CHECK_TOKEN_DOCS)
@dependencies.require_auth
async def check_token(token: str = Depends(oauth2_scheme)):
    if not token:
        log_message("Token não fornecido para verificação.", level="warning")
        return {"valid": False, "message": "Token não fornecido"}

    is_valid = service.verify_token(token)
    log_message(f"Verificação de token: {'válido' if is_valid else 'inválido'}", level="info")
    return {"valid": is_valid}


@router.post(
    "/forgot-password",
    response_model=schemas.ResetPasswordResponse,
    **FORGOT_PASSWORD_DOCS,
)
async def forgot_password(
    request: schemas.ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    log_message(f"Solicitação de recuperação de senha para: {request.email}", level="info")
    return await service.request_password_reset(db, request.email)


@router.post(
    "/password-reset",
    response_model=schemas.ChangePasswordResponse,
    **PASSWORD_RESET_DOCS,
)
async def password_reset(
    request: schemas.ChangePasswordRequest, db: AsyncSession = Depends(get_db)
):
    log_message(f"Solicitação de redefinição de senha para: {request.email}", level="info")
    return await service.password_reset(
        db, request.token, request.email, request.new_password
    )
