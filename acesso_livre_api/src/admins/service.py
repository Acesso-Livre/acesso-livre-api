from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext
from ..config import settings
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_admin(db: Session, admin: schemas.AdminCreate):
    if db.query(models.Admins).filter(models.Admins.email == admin.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    data = admin.model_dump()
    data['password'] = get_password_hash(admin.password)
    db_admin = models.Admins(**data, created_at=datetime.now(timezone.utc))
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

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

def request_password_reset(db: Session, email: str):
    admin = db.query(models.Admins).filter(models.Admins.email == email).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Email não encontrado!")
    
    expire = datetime.now(timezone.utc) + timedelta(minutes= settings.reset_token_expire_minutes)
    to_encode = {"sub": admin.email, "exp": expire}
    reset_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    admin.reset_token_hash = reset_token
    admin.reset_token_expires = expire
    db.commit()

    return {"message": "Enviamos um link de recuperação ao email."}

def password_reset(db: Session, token: str, new_password: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str =payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    
    admin = db.query(models.Admins).filter(models.Admins.email == email).first()
    if not admin or admin.reset_token_hash != token:
        raise HTTPException(status_code=400, detail="Token inválido ou já usado")
    if datetime.now(timezone.utc) > admin.reset_token_expires:
        raise HTTPException(status_code=400, detail="Token expirado")
    
    admin.password = get_password_hash(new_password)
    admin.reset_token_hash = None
    admin.reset_token_expires = None
    db.commit()

    return {"message": "Senha atualizada com sucesso!"}