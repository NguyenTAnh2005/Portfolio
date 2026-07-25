from app.core.config import settings

from fastapi import APIRouter, Depends
from app.core.security import get_current_admin
from app.schemas.response import ResponseModel
from sqlalchemy.orm import Session
from app.models.models import Info, User
from app.crud.info import get_info_by_id, update_info_by_id
from app.schemas.info import InfoResponse, InfoUpdate

from app.db_connection import connect_db

BASE_URL = settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/info",
    tags=["Info"]
)
@router.get("/{info_id}", response_model=ResponseModel[InfoResponse])
def read_info(info_id: int, db: Session = Depends(connect_db)):
    """
    - Gọi hàm get theo id của crud bên Info và nhận data dạng Info
    - Ghép data trả về vào response Model.
    """
    info = get_info_by_id(db=db, info_id=info_id)
    return ResponseModel(
        data=info,
        message="Lấy thông tin Info thành công!"
    )

@router.put("/{info_id}", response_model=ResponseModel[InfoResponse])
def update_info(
    info_id: int, update_data: InfoUpdate, 
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin)):
    """
    - Gọi hàm cập nhật bên crud của Info (Ko có xử lý nghiệp vụ nên gọi thẳng)
    - Bên CRUD thực hiện ánh xạ object sang dict và làm việc cập nhật, trả về model Info đã cập nhật
    - Gán model đã cập nhật vào response model (Dùng Inforesponse để xem thông tin đầy đủ ở return hơn là InfoUpdate)
    """
    info = update_info_by_id(db = db, target_info_id = info_id, update_data=update_data)
    return ResponseModel(
        data=info,
        message="Cập nhật thông tin Info thành công!"
    )