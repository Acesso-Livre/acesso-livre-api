from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from acesso_livre_api.src.database import get_db
from acesso_livre_api.src.login import models, schemas, utils, jwt

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.AdminUser).filter(models.AdminUser.email == request.email).first()
    if not user or not utils.verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    access_token = jwt.create_access_token(data={"sub": user.email})
    return schemas.TokenResponse(access_token=access_token)