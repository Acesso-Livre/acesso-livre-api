from jose import jwt, JWTError, ExpiredSignatureError
import pytest
from datetime import timedelta

from acesso_livre_api.src.admins import service
from acesso_livre_api.src.admins.schemas import AdminCreate

def test_verify_token():
    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")

    token = service.create_access_token(data={"sub": admin.email})

    verifyToken = service.verify_token(token)

    assert verifyToken is True


def test_verify_expired_token():
    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    
    expired_minutes = -1  # Token expirado há 1 minuto

    token = service.create_access_token(data={"sub": admin.email}, expires_delta=expired_minutes)

    is_valid = service.verify_token(token)

    assert is_valid is False

def test_verify_invalid_token():
    admin = AdminCreate( 
        email="validadmin@gmail.com",
        password="ValidPass123!")
    
    token = service.create_access_token(data={"sub": admin.email})
    
    invalid_token = token + "invalidpart"

    is_valid = service.verify_token(invalid_token)

    assert is_valid is False