from pydantic import BaseModel
from typing import Optional

class BaseContact(BaseModel):
    name: str
    url: str

class Response(BaseModel):
    id: int
    fullname: str
    hometown: str
    gender: bool
    major: str
    language: list[str]
    framework: list[str]
    intro: str
    contact: list[BaseContact]
    bio: str

class Update(BaseModel):
    fullname: Optional[str] = None
    hometown: Optional[str] = None
    gender: Optional[bool] = True
    major: Optional[str] = None
    language: Optional[list[str]] = None
    framework: Optional[list[str]] = None
    intro: Optional[str] = None
    contact: Optional[list[BaseContact]] = None
    bio: Optional[str] = None

