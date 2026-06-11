from typing import Optional, Generic, TypeVar
from pydantic import BaseModel

# Tạo biến T là kiểu dữ liệu động (Generic Type)
T = TypeVar("T")

class ResponseModel(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None