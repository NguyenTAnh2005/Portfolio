from fastapi import APIRouter, Depends, Query
from typing import  Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db_connection import connect_db
from app.schemas.response import ResponseModel
from app.core import jwt_token as jwt_service
from app.models.models import User

from app.schemas import systemconfig as schemas_sys_config
from app.services import systemconfig as logic_sys_config

BASE_URL = settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/system-configs",
    tags=["System Configs"]
)

@router.post("/", response_model=ResponseModel[schemas_sys_config.Response])
def create_config(
    create_data: schemas_sys_config.Create,
    db: Session = Depends(connect_db), 
    current_admin: User = Depends(jwt_service.get_current_admin) 
):
    """
    ## API tạo mới System config 
    """
    result = logic_sys_config.create_config(db=db, create_data=create_data)
    
    return ResponseModel(
        message=f"🎉 System config was created successfully.",
        data=result
    )

 
@router.get("/{system_config_id}", response_model=ResponseModel[schemas_sys_config.Response])
def get_config(
    system_config_id: int,
    db: Session = Depends(connect_db)
):
    """
    ## API lấy thông tin system_config với id
        + Nhận id system_config và trả về kết quả tương ứng từ func bên crud.
        + Trả về kết quả dưới dạng ResponseModel
    """
    result = logic_sys_config.get_config(db=db, config_id=system_config_id)
    return ResponseModel(
        message=f"🎉 System config was found successfully.",
        data= result
    )

@router.get("/", response_model=ResponseModel[list[schemas_sys_config.Response]])
def list_config(
    db: Session = Depends(connect_db),
    skip: int = Query(0, ge=0, description="Số bản ghi muốn bỏ qua: "),
    limit: int = Query(30, ge=1, le=30, description="Số bản ghi tối đa trên 1 trang: "),
):
    """
    ## API trả về danh sách system_config với các thông số.
        + Gọi hàm crud trả về danh sách, lưu biến kết quả
        + Trả về kết quả dưới dạng ResponseModel
    """
    result = logic_sys_config.get_all_config(db=db, skip=skip, limit=limit)
    return ResponseModel(
        message=f"🎉 System config list retrieved successfully.",
        data=result
    )

@router.put("/{system_config_id}", response_model=ResponseModel[schemas_sys_config.Response])
def update_config(
    system_config_id: int,
    update_data: schemas_sys_config.Update,
    db: Session = Depends(connect_db), 
    current_admin: User = Depends(jwt_service.get_current_admin) 
):
    """
    ## API cập nhật thông tin Timeline qua id
        + Gọi hàm logic update
        + Return ResponeModel với data là Object đã cập nhật
    """
    result = logic_sys_config.update_config(db=db, target_id=system_config_id, update_data=update_data)
    return ResponseModel(
        message=f"🎉 System config was updated successfully!",
        data=result
    )

@router.delete("/{system_config_id}", response_model=ResponseModel)
def delete_config(
    system_config_id: int,
    db: Session = Depends(connect_db),
    current_admin: User = Depends(jwt_service.get_current_admin)
):
    """
    ## API xóa system_config. 
        + Gọi CRUD delete
        + Trả về kết quả dưới dạng ResponseModel
    """
    logic_sys_config.delete_config(db=db, target_id=system_config_id)
    return ResponseModel(
        message=f"🎉 The System Config with ID [{system_config_id}] has been deleted successfully.",
        data=[]
    )
