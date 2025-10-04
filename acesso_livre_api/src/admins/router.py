from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
import logging
from . import service, schemas, exceptions
from ..database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admins/login")

@router.post("/register", response_model=schemas.RegisterResponse, status_code=status.HTTP_201_CREATED, responses={201: {"description": "Administrador criado com sucesso"}})
def register_admin(admin: schemas.AdminCreate, db: Session = Depends(get_db)):
    service.create_admin(db, admin)
    return {"status": "success"}


@router.post("/login", response_model=schemas.LoginResponse)
def login(
    admin: schemas.LoginRequest, db: Session = Depends(get_db),
):
    admin = service.authenticate_admin(
        db, admin.email, admin.password)
    if not admin:
        raise exceptions.AdminAuthenticationFailedException()

    access_token = service.create_access_token(
        data={"sub": admin.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/check-token")
def check_token(token: str = Depends(oauth2_scheme)):
    is_valid = service.verify_token(token)
    return {"valid": is_valid}


@router.post("/forgot-password", response_model=schemas.ResetPasswordResponse)
def forgot_password(request: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    return service.request_password_reset(db, request.email)


@router.post("/password-reset", response_model=schemas.ChangePasswordResponse)
def password_reset(request: schemas.ChangePasswordRequest, db: Session = Depends(get_db)):
    return service.password_reset(db, request.token, request.new_password)
