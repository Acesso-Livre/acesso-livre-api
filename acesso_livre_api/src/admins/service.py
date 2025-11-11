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
        db.rollback()
        raise exceptions.AdminCreationException()

def authenticate_admin(db: Session, email: str, password: str):
    try:
        admin = db.query(models.Admins).filter(models.Admins.email == email).first()
        if not admin or not verify_password(password, admin.password):
            raise exceptions.AdminAuthenticationFailedException()
        return admin
    
    except exceptions.AdminInvalidEmailException:
        raise
    except Exception as e:
        logger.error(f"Erro na autenticação do admin: {str(e)}")
        raise exceptions.AdminAuthenticationFailedException()

def create_access_token(data: dict, expires_delta: int = settings.access_token_expire_minutes):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    except Exception as e:
        logger.error(f"Erro ao criar token de acesso: {str(e)}")
        raise exceptions.TokenCreationException()

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

# TODO: implementar o envio de email com o token de reset
def request_password_reset(db: Session, email: str):
    try:
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
    except exceptions.AdminNotFoundException:
        raise
    except Exception as e:
        logger.error(f"Erro ao solicitar reset de senha: {str(e)}")
        db.rollback()
        raise exceptions.PasswordResetRequestException()

def password_reset(db: Session, code: str, email: str, new_password: str):
    try:
        # Validar senha forte usando função utilitária
        if not utils.is_strong_password(new_password):
            raise exceptions.AdminWeakPasswordException()

        admin = db.query(models.Admins).filter(models.Admins.email == email).first()
        if not admin:
            raise exceptions.AdminNotFoundException()

        if not admin.reset_token_hash:
            raise exceptions.InvalidResetTokenException("Token de reset não encontrado")

        payload = jwt.decode(admin.reset_token_hash, settings.secret_key, algorithms=[settings.algorithm])
        stored_code = payload.get("code")
        if stored_code != code:
            raise exceptions.InvalidResetTokenException("Código inválido")
        
        admin.password = get_password_hash(new_password)
        admin.reset_token_hash = None
        admin.reset_token_expires = None
        db.commit()

        return {"message": "Senha atualizada com sucesso!"}
    
    except (exceptions.AdminNotFoundException, exceptions.InvalidResetTokenException, exceptions.AdminWeakPasswordException):
        raise
    except (ExpiredSignatureError, JWTError):
        raise exceptions.InvalidResetTokenException("Token inválido ou corrompido")
    except Exception as e:
        logger.error(f"Erro ao resetar a senha do admin: {str(e)}")
        db.rollback()
        raise exceptions.PasswordResetException()