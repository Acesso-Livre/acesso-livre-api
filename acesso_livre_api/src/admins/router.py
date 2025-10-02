from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from . import service, schemas
from ..database import get_db

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login")


@router.post("/register", response_model=schemas.AdminCreate)
def register_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    return service.create_admin(db, admin)


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    admin: schemas.LoginRequest, db: Session = Depends(get_db),
):
    admin = service.authenticate_admin(
        db, admin.email, admin.password)
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

@router.get("/check-token")
def check_token(token: str):
    is_valid = service.verify_token(token)
    return {"valid": is_valid}
