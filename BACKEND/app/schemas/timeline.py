from pydantic import BaseModel
from typing import Optional

# get by id
class Response(BaseModel):
    title: str 
    organization: str 
    desc: str 
    start_end: str 
    sort_order: int 
    img_url: Optional[str] = None
    img_public_id: Optional[str] = None
    # img_public_url: str

    class Config:
        from_attributes = True

# get all 
class PaginationResponse(BaseModel):
    total: int
    skip: int
    limit: int
    list_data: list[Response]

# ko cần url, public id , phần này sẽ cấu bên dịch vụ của cloudinary lo 
# create - 
class Create(BaseModel):
    title: str 
    organization: str 
    desc: str 
    start_end: str 
    sort_order: int 


# update - 
class Update(BaseModel):
    title: Optional[str] = None
    organization: Optional[str] = None
    desc: Optional[str] = None
    start_end: Optional[str] = None
    sort_order: Optional[int] = None 