from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Response(BaseModel):
    # img thì cloud lo riêng
    # list_lang, created_at, last_updated, desc thì project_url lấy đc 
    title: str
    list_tech: Optional[list[str]] = None
    project_url: str
    desc: Optional[str] = None
    list_lang: Optional[list[str]] = None
    created_at: datetime
    last_updated: datetime
    img_url: str
    img_public_id: str

    class Config:
        from_attributes = True


class PaginationResponse(BaseModel):
    total: int
    skip: int
    limit: int
    list_data: list[Response]


class Create(BaseModel):
    # img thì cloud lo riêng
    # list_lang, created_at, last_updated, desc thì project_url lấy đc  
    # - nhưng do logic lấy, crud nên đầy đủ để ghi vào Db 
    title: str
    list_tech: Optional[list[str]] = None
    project_url: str
    desc: Optional[str] = None
    list_lang: Optional[list[str]] = None
    created_at: datetime
    last_updated: datetime


class UpdateTextForm(BaseModel):
    title: Optional[str] = None
    list_tech: Optional[list[str]] = None
    project_url: Optional[str] = None


class UpdateFetchRepo(BaseModel):
    desc: Optional[str] = None
    list_lang: Optional[list[str]] = None
    created_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    

