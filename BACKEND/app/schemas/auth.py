from typing import Optional
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: str


class TokenPayload(BaseModel):
    data: Optional[int] = None  # Chứa id user
    sub: Optional[str] = None   # Chứa Email user


