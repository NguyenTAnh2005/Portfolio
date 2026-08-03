from app.core.config import settings

from fastapi import APIRouter, Depends
from app.core.security import get_current_admin
from app.schemas.response import ResponseModel
from sqlalchemy.orm import Session
from app.models.models import Info, User
from app.crud import info as info_crud
from app.schemas import info as schemas_info

from app.db_connection import connect_db

BASE_URL = settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/infos",
    tags=["Infos"]
)
@router.get("/{info_id}", response_model=ResponseModel[schemas_info.Response])
def get_info(info_id: int, db: Session = Depends(connect_db)):
    """
    ## API trả về info theo id:
        + Gọi hàm get theo id của crud bên Info và nhận data dạng Info
        + Ghép data trả về vào response Model.
    """
    info = info_crud.get_by_id(db=db, info_id=info_id)
    return ResponseModel(
        data=info,
        message=f"🎉 Info was found successfully."
    )

@router.put("/{info_id}", response_model=ResponseModel[schemas_info.Response])
def update_info(
    info_id: int, update_data: schemas_info.Update, 
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin)):
    """
    ## API Cập nhật thông tin info:
        + Gọi hàm cập nhật bên crud của Info (Ko có xử lý nghiệp vụ nên gọi thẳng)
        + Bên CRUD thực hiện ánh xạ object sang dict và làm việc cập nhật, trả về model Info đã cập nhật
        + Gán model đã cập nhật vào response model (Dùng Inforesponse để xem thông tin đầy đủ ở return hơn là InfoUpdate)
    """
    info = info_crud.update(db = db, target_info_id = info_id, update_data=update_data)
    return ResponseModel(
        data=info,
        message=f"🎉 Info was updated successfully."
    )