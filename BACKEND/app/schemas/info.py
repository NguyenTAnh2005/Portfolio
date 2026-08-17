from pydantic import BaseModel
from typing import Optional

class BaseContact(BaseModel):
    name: str
    url: str

class TechStack(BaseModel):
    language: list[str]
    framework: list[str]
    database: list[str]
    tools: list[str]

class Response(BaseModel):
    id: int
    fullname: str
    hometown: str
    gender: bool
    major: str
    techstack: TechStack
    intro: str
    contact: list[BaseContact]
    bio: str

    class Config:
        from_attributes = True

class Update(BaseModel):
    fullname: Optional[str] = None
    hometown: Optional[str] = None
    gender: Optional[bool] = True
    major: Optional[str] = None
    techstack: Optional[TechStack] = None
    intro: Optional[str] = None
    contact: Optional[list[BaseContact]] = None
    bio: Optional[str] = None

