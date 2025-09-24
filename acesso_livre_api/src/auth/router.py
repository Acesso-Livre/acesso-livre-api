from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import service, schemas, models
from ..database import get_db
from jose import JWTError, jwt
from ..config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login")


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    admin = db.query(models.Admins).filter(
        models.Admins.email == email).first()
    if admin is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    return admin


@router.post("/register", response_model=schemas.AdminResponse)
def register_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    return service.create_admin(db, admin)


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db),
):
    admin = service.authenticate_admin(
        db, form_data.username, form_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = service.create_access_token(
        data={"sub": admin.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.AdminResponse)
def read_current_admin(current_admin: models.Admins = Depends(get_current_admin)):
    return current_admin
