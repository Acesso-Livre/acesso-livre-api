from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class AdminBase(BaseModel):
    email: EmailStr


class AdminCreate(AdminBase):
    password: str


class AdminResponse(AdminBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None