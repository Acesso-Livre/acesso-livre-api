from pydantic import BaseModel, EmailStr, field_validator
import re

class AdminCreate(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", v):
            from .exceptions import AdminInvalidEmailException
            raise AdminInvalidEmailException()
        return v


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordResponse(BaseModel):
    message: str


class ChangePasswordRequest(BaseModel):
    token: str
    email: EmailStr
    new_password: str


class ChangePasswordResponse(BaseModel):
    message: str


class RegisterResponse(BaseModel):
    status: str
