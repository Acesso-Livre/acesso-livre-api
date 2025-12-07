from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas, exceptions
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from ..config import settings
from . import utils
from .email_service import send_password_reset_email
import logging
from func_log import *

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    log_message("Gerando hash para a senha fornecida.", level="debug")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    log_message("Verificando senha fornecida contra o hash armazenado.", level="debug")
    return pwd_context.verify(plain_password, hashed_password)


async def create_admin(db: AsyncSession, admin: schemas.AdminCreate):
    try:
        stmt = select(models.Admins).where(models.Admins.email == admin.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none() is not None:
            log_message(f"Falha ao criar admin: email {admin.email} já existe.", level="warning")
            raise exceptions.AdminAlreadyExistsException()

        data = admin.model_dump()
        data["password"] = get_password_hash(admin.password)
        db_admin = models.Admins(**data, created_at=datetime.now(timezone.utc))
        db.add(db_admin)
        await db.commit()
        await db.refresh(db_admin)
        log_message(f"Admin criado com sucesso: {admin.email}", level="info")
        return True

    except exceptions.AdminAlreadyExistsException:
        log_message(f"Falha ao criar admin: email {admin.email} já existe.", level="warning")
        raise
    except exceptions.AdminInvalidEmailException:
        log_message(f"Falha ao criar admin: email inválido {admin.email}.", level="warning")
        raise
    except exceptions.AdminWeakPasswordException:
        log_message(f"Falha ao criar admin: senha fraca fornecida para {admin.email}.", level="warning")
        raise
    except Exception as e:
        log_message("Erro ao criar admin.", level="error")
        logger.error("Erro ao criar admin: %s", str(e))
        await db.rollback()
        raise exceptions.AdminCreationException()


async def authenticate_admin(db: AsyncSession, email: str, password: str):
    try:
        stmt = select(models.Admins).where(models.Admins.email == email)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()
        if not admin or not verify_password(password, admin.password):
            log_message(f"Falha na autenticação para o admin: {email}", level="warning")
            raise exceptions.AdminAuthenticationFailedException()
            log_message(f"Admin autenticado com sucesso: {email}", level="info")
        return admin

    except exceptions.AdminInvalidEmailException:
        log_message(f"Falha na autenticação para o admin: {email}", level="warning")
        raise
    except Exception as e:
        logger.error("Erro na autenticação do admin: %s", str(e))
        log_message("Erro na autenticação do admin.", level="error")
        log_message(str(e), level="error")
        raise exceptions.AdminAuthenticationFailedException()


def create_access_token(
    data: dict, expires_delta: int = settings.access_token_expire_minutes
):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        log_message("Token de acesso criado com sucesso.", level="info")
        return encoded_jwt
    except Exception as e:
        logger.error("Erro ao criar token de acesso: %s", str(e))
        log_message("Erro ao criar token de acesso.", level="error")
        log_message(str(e), level="error")
        raise exceptions.TokenCreationException()


def verify_token(token: str):
    try:
        jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except ExpiredSignatureError:
        log_message("Token expirado durante verificação.", level="warning")
        return False
    except JWTError:
        log_message("Token inválido durante verificação.", level="warning")
        return False
    log_message("Token verificado com sucesso.", level="info")
    return True


# TODO: implementar o envio de email com o token de reset
async def request_password_reset(db: AsyncSession, email: str):
    try:
        stmt = select(models.Admins).where(models.Admins.email == email)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()
        if not admin:
            log_message(f"Solicitação de recuperação de senha falhou: admin {email} não encontrado.", level="warning")
            raise exceptions.AdminNotFoundException()

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.reset_token_expire_minutes
        )
        code = utils.gen_code_for_reset_password()
        to_encode = {"sub": admin.email, "exp": expire, "code": code}
        reset_token = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )

        admin.reset_token_hash = reset_token
        admin.reset_token_expires = expire
        await db.commit()

        try:
            await send_password_reset_email(
                to_email=admin.email, code=code, reset_token=reset_token
            )
            logger.info("Email de recuperação de senha enviado para %s", admin.email)
        except Exception as e:
            log_message("Erro ao enviar email de recuperação.", level="error")
            log_message(str(e), level="error")
            logger.error(
                "Erro ao enviar email de recuperação para %s: %s", admin.email, str(e)
            )
            raise exceptions.EmailSendException(
                reason="Não foi possível enviar o email de recuperação. Tente novamente mais tarde."
            )
        log_message(f"Solicitação de recuperação de senha processada para: {email}", level="info")
        return {"message": "Enviamos um link de recuperação ao email."}
    except exceptions.AdminNotFoundException:
        log_message(f"Solicitação de recuperação de senha falhou: admin {email} não encontrado.", level="warning")
        raise
    except exceptions.EmailSendException:
        log_message("Erro ao enviar email de recuperação.", level="error")
        raise
    except Exception as e:
        logger.error("Erro ao solicitar reset de senha: %s", str(e))
        log_message("Erro ao solicitar reset de senha.", level="error")
        log_message(str(e), level="error")
        await db.rollback()
        raise exceptions.PasswordResetRequestException()


async def password_reset(db: AsyncSession, code: str, email: str, new_password: str):
    try:
        # Validar senha forte usando função utilitária
        if not utils.is_strong_password(new_password):
            log_message("Falha ao resetar senha: senha fraca fornecida.", level="warning")
            raise exceptions.AdminWeakPasswordException()

        stmt = select(models.Admins).where(models.Admins.email == email)
        result = await db.execute(stmt)
        admin = result.scalar_one_or_none()
        if not admin:
            log_message(f"Falha ao resetar senha: admin {email} não encontrado.", level="warning")
            raise exceptions.AdminNotFoundException()

        if not admin.reset_token_hash:
            log_message("Falha ao resetar senha: token de reset não encontrado.", level="warning")
            raise exceptions.InvalidResetTokenException("Token de reset não encontrado")

        payload = jwt.decode(
            admin.reset_token_hash, settings.secret_key, algorithms=[settings.algorithm]
        )
        stored_code = payload.get("code")
        if stored_code != code:
            log_message("Falha ao resetar senha: código inválido fornecido.", level="warning")
            raise exceptions.InvalidResetTokenException("Código inválido")

        admin.password = get_password_hash(new_password)
        admin.reset_token_hash = None
        admin.reset_token_expires = None
        await db.commit()

        log_message(f"Senha resetada com sucesso para o admin: {email}", level="info")
        return {"message": "Senha atualizada com sucesso!"}

    except (
        exceptions.AdminNotFoundException,
        exceptions.InvalidResetTokenException,
        exceptions.AdminWeakPasswordException,
    ):
        log_message(f"Falha ao resetar senha para o admin: {email}", level="warning")
        raise
    except (ExpiredSignatureError, JWTError):
        log_message("Falha ao resetar senha: token de reset inválido ou expirado.", level="warning")
        raise exceptions.InvalidResetTokenException("Token inválido ou corrompido")
    except Exception as e:
        log_message("Erro ao resetar a senha do admin.", level="error")
        log_message(str(e), level="error")
        logger.error("Erro ao resetar a senha do admin: %s", str(e))
        await db.rollback()
        raise exceptions.PasswordResetException()
