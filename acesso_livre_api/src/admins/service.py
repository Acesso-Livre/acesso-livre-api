from sqlalchemy.orm import Session
from . import models, schemas, exceptions
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from ..config import settings
from . import utils
import logging
import re

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_admin(db: Session, admin: schemas.AdminCreate):
    try:
        # Verificar se email já existe
        if db.query(models.Admins).filter(models.Admins.email == admin.email).first():
            raise exceptions.AdminAlreadyExistsException(email=admin.email)
        
        # Validar robustez da senha
        if not PASSWORD_PATTERN.match(admin.password):
            raise exceptions.AdminWeakPasswordException(
                "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."
            )
        
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
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        exp = payload.get("exp")
        if exp is None:
            return False
        if datetime.now(timezone.utc).timestamp() > exp:
            return False
    except ExpiredSignatureError:
        return False
    except JWTError:
        return False
        
    return True

async def request_password_reset(db: Session, email: str):
    admin = db.query(models.Admins).filter(models.Admins.email == email).first()
    if not admin:
        raise exceptions.AdminNotFoundException()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes= settings.reset_token_expire_minutes)
    code = await utils.gen_code_for_reset_password()
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
        exp = payload.get("exp")
        if stored_code != code:
            raise exceptions.InvalidResetTokenException("Código inválido")
    except JWTError:
        raise exceptions.InvalidResetTokenException("Token inválido ou corrompido")

    if datetime.now(timezone.utc).timestamp() > exp:
        raise exceptions.ExpiredResetTokenException()

    # Validar robustez da nova senha
    if not PASSWORD_PATTERN.match(new_password):
        raise exceptions.AdminWeakPasswordException(
            "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."
        )

    admin.password = get_password_hash(new_password)
    admin.reset_token_hash = None
    admin.reset_token_expires = None
    db.commit()

    return {"message": "Senha atualizada com sucesso!"}