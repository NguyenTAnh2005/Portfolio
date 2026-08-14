from typing import Any, Optional
from pydantic import BaseModel

# response 
class Response(BaseModel):
    id: int
    name: str
    value: Any

    class Config:
        from_attributes = True


# create
class Create(BaseModel):
    name: str
    value: Any

# update
class Update(BaseModel):
    name: Optional[str] = None
    value: Optional[Any] = None