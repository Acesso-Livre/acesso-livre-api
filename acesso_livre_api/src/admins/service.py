from sqlalchemy.orm import Session
from . import models, schemas, exceptions
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from ..config import settings
from . import utils
import logging
from .schemas import AdminCreate

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_admin(db: Session, admin: schemas.AdminCreate):
    try:
        if db.query(models.Admins).filter(models.Admins.email == admin.email).first() is not None:
            raise exceptions.AdminAlreadyExistsException()

        data = admin.model_dump()
        data['password'] = get_password_hash(admin.password)
        db_admin = models.Admins(**data, created_at=datetime.now(timezone.utc))
        db.add(db_admin)
        db.commit()
        db.refresh(db_admin)
        return True

    except exceptions.AdminAlreadyExistsException:
        raise
    except exceptions.AdminInvalidEmailException:
        raise
    except exceptions.AdminWeakPasswordException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar admin: {str(e)}")
        raise exceptions.AdminCreationException()

def authenticate_admin(db: Session, email: str, password: str):
    admin = db.query(models.Admins).filter(models.Admins.email == email).first()
    if not admin or not verify_password(password, admin.password):
        return None
    return admin

def create_access_token(data: dict, expires_delta: int = settings.access_token_expire_minutes):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token: str):
    try:
        jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except ExpiredSignatureError:
        return False
    except JWTError:
        return False
        
    return True

def request_password_reset(db: Session, email: str):
    admin = db.query(models.Admins).filter(models.Admins.email == email).first()
    if not admin:
        raise exceptions.AdminNotFoundException()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes= settings.reset_token_expire_minutes)
    code = utils.gen_code_for_reset_password()
    to_encode = {"sub": admin.email, "exp": expire, "code": code}
    reset_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    admin.reset_token_hash = reset_token
    admin.reset_token_expires = expire
    db.commit()
    return {"message": "Enviamos um link de recuperação ao email."}

def password_reset(db: Session, code: str, email: str, new_password: str):
    admin = db.query(models.Admins).filter(models.Admins.email == email).first()
    if not admin:
        raise exceptions.AdminNotFoundException()

    if not admin.reset_token_hash:
        raise exceptions.InvalidResetTokenException("Token de reset não encontrado")

    try:
        payload = jwt.decode(admin.reset_token_hash, settings.secret_key, algorithms=[settings.algorithm])
        stored_code = payload.get("code")
        if stored_code != code:
            raise exceptions.InvalidResetTokenException("Código inválido")
    except ExpiredSignatureError:
        raise exceptions.InvalidResetTokenException("Token expirado")
    except JWTError:
        raise exceptions.InvalidResetTokenException("Token inválido ou corrompido")
    
    try:
        # Passamos um email fictício apenas para satisfazer o validador do Pydantic.
        # O email não é usado, apenas a validação da senha é acionada.
        AdminCreate(email="placeholder@example.com", password=new_password)
    except exceptions.AdminWeakPasswordException as e:
        raise e  # Repassa a exceção específica de senha fraca
    except Exception:
        # Captura outras exceções de validação, mas lança a de senha fraca por contexto
        raise exceptions.AdminWeakPasswordException(
            "A senha fornecida é inválida."
        )

    admin.password = get_password_hash(new_password)
    admin.reset_token_hash = None
    admin.reset_token_expires = None
    db.commit()

    return {"message": "Senha atualizada com sucesso!"}