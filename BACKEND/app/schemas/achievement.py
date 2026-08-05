from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Response(BaseModel):
    id: int
    title: str
    desc: str
    achieved_at: datetime
    img_url: Optional[str] = None
    img_public_id: Optional[str] = None

    class Config: 
        from_attributes = True

class PaginationResponse(BaseModel):
    total: int
    limit: int
    skip: int
    list_data: list[Response]

class Create(BaseModel):
    title: str
    desc: str
    achieved_at: datetime

class Update(BaseModel):
    title: Optional[str] = None
    desc: Optional[str] = None
    achieved_at: Optional[datetime] = None
    