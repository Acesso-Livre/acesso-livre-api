from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
import re
from .exceptions import AdminInvalidEmailException, AdminWeakPasswordException

PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$")

class AdminCreate(BaseModel):
    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "admin@empresa.com"}
    )
    password: str = Field(
        ...,
        min_length=8,
        json_schema_extra={"example": "Senha123!"}
    )

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", v):
            raise AdminInvalidEmailException()
        return v

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if not PASSWORD_PATTERN.match(v):
            raise AdminWeakPasswordException(
                "A senha deve ter pelo menos 8 caracteres, incluindo letra maiúscula, minúscula, número e caractere especial."
            )
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@empresa.com",
                "password": "Senha123!"
            }
        }
    )


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "admin@empresa.com"}
    )
    password: str = Field(
        ...,
        json_schema_extra={"example": "Senha123!"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@empresa.com",
                "password": "Senha123!"
            }
        }
    )


class LoginResponse(BaseModel):
    access_token: str = Field(
        ...,
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBlbXByZXNhLmNvbSIsImV4cCI6MTYzODUwMDAwMH0.signature"}
    )
    token_type: str = Field(
        default="bearer",
        json_schema_extra={"example": "bearer"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBlbXByZXNhLmNvbSIsImV4cCI6MTYzODUwMDAwMH0.signature",
                "token_type": "bearer"
            }
        }
    )


class ResetPasswordRequest(BaseModel):

    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "admin@empresa.com"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@empresa.com"
            }
        }
    )


class ResetPasswordResponse(BaseModel):
    message: str = Field(
        ...,
        json_schema_extra={"example": "Enviamos um link de recuperação ao email."}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Enviamos um link de recuperação ao email."
            }
        }
    )


class ChangePasswordRequest(BaseModel):
    token: str = Field(
        ...,
        json_schema_extra={"example": "ABC123"}
    )
    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "admin@empresa.com"}
    )
    new_password: str = Field(
        ...,
        min_length=8,
        json_schema_extra={"example": "NovaSenha456!"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "token": "ABC123",
                "email": "admin@empresa.com",
                "new_password": "NovaSenha456!"
            }
        }
    )


class ChangePasswordResponse(BaseModel):
    message: str = Field(
        ...,
        json_schema_extra={"example": "Senha atualizada com sucesso!"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Senha atualizada com sucesso!"
            }
        }
    )


class RegisterResponse(BaseModel):
    status: str = Field(
        ...,
        json_schema_extra={"example": "success"}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success"
            }
        }
    )
