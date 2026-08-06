from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.response import ResponseModel
from app.db_connection import connect_db
from app.core.config import settings

from app.schemas import index as schemas_index
from app.services import index as logic_index

BASE_URL = settings.BASE_API_URL
router = APIRouter(
    prefix=BASE_URL+"/index-list",
    tags=["Index"]
)

@router.get("/", response_model=ResponseModel[schemas_index.Response])
def list_data_index(
    db: Session = Depends(connect_db)
):
    """
    ## API trả về danh sách các phần tử ở trang Index theo các thông số được hardcode. 
    ### Xử lý:
        + 1. Gọi service logic 
        + 2. Trả respone dưới dạng Response Model
    """
    result = logic_index.get_index_list(db=db)

    return ResponseModel(
        message=f"🎉 Index data list retrieved successfully.",
        data=result
    )