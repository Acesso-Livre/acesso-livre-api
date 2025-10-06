from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class AdminCreate(BaseModel):
    email: EmailStr = Field(
        ...,
        example="admin@empresa.com"
    )
    password: str = Field(
        ...,
        min_length=8,
        example="Senha123!"
    )

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", v):
            from .exceptions import AdminInvalidEmailException
            raise AdminInvalidEmailException()
        return v

    class Config:
        schema_extra = {
            "example": {
                "email": "admin@empresa.com",
                "password": "Senha123!"
            }
        }


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        example="admin@empresa.com"
    )
    password: str = Field(
        ...,
        example="Senha123!"
    )

    class Config:
        schema_extra = {
            "example": {
                "email": "admin@empresa.com",
                "password": "Senha123!"
            }
        }


class LoginResponse(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBlbXByZXNhLmNvbSIsImV4cCI6MTYzODUwMDAwMH0.signature"
    )
    token_type: str = Field(
        default="bearer",
        example="bearer"
    )

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBlbXByZXNhLmNvbSIsImV4cCI6MTYzODUwMDAwMH0.signature",
                "token_type": "bearer"
            }
        }


class ResetPasswordRequest(BaseModel):

    email: EmailStr = Field(
        ...,
        example="admin@empresa.com"
    )

    class Config:
        schema_extra = {
            "example": {
                "email": "admin@empresa.com"
            }
        }


class ResetPasswordResponse(BaseModel):
    message: str = Field(
        ...,
        example="Enviamos um link de recuperação ao email."
    )

    class Config:
        schema_extra = {
            "example": {
                "message": "Enviamos um link de recuperação ao email."
            }
        }


class ChangePasswordRequest(BaseModel):
    token: str = Field(
        ...,
        example="ABC123"
    )
    email: EmailStr = Field(
        ...,
        example="admin@empresa.com"
    )
    new_password: str = Field(
        ...,
        min_length=8,
        example="NovaSenha456!"
    )

    class Config:
        schema_extra = {
            "example": {
                "token": "ABC123",
                "email": "admin@empresa.com",
                "new_password": "NovaSenha456!"
            }
        }


class ChangePasswordResponse(BaseModel):
    message: str = Field(
        ...,
        example="Senha atualizada com sucesso!"
    )

    class Config:
        schema_extra = {
            "example": {
                "message": "Senha atualizada com sucesso!"
            }
        }


class RegisterResponse(BaseModel):
    status: str = Field(
        ...,
        example="success"
    )

    class Config:
        schema_extra = {
            "example": {
                "status": "success"
            }
        }
