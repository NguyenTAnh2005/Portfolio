from fastapi import APIRouter, Depends
from app.services.user import logic_update_password, logic_update_user_email
from app.crud.user import get_user
from app.core.config import settings
from app.schemas.user import UserResponse, UserUpdateInfo, UserUpdatePassword
from sqlalchemy.orm import Session
from app.db_connection import connect_db
from app.core.security import get_current_admin, get_current_user
from app.models.models import User
from app.schemas.response import ResponseModel

BASE_URL= settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/user",
    tags = ["User"]
)

@router.get("/{user_id}", response_model = ResponseModel[UserResponse])
def read_user_profile(user_id: int, db: Session = Depends(connect_db), current_admin: User = Depends(get_current_admin)):
    """
    - CRUD (get_user): Đi vào kho, lấy ra một Object (chứa cả password, id, role,...), và trả nguyên cái Object đó về.
    - Router: Nhận được cái Object từ CRUD, và cứ thế return user.
    - response_model: FastAPI sẽ tự động cầm cái Object đối chiếu với khuôn UserResponse, vứt bỏ đi cái password, và đóng gói thành JSON trả về cho Frontend.
    """
    user = get_user(db= db, user_id=user_id)
    return ResponseModel(
        data=user,
        message="Lấy thông tin người dùng thành công!"
        )

@router.put("/info/{user_id}", response_model= ResponseModel[UserUpdateInfo])
def update_user_info(
    user_id: int,update_data: UserUpdateInfo, 
    db: Session = Depends(connect_db), 
    current_user: User = Depends(get_current_user)):

    db_user = logic_update_user_email(db=db, current_user_id=current_user.id, target_user_id=user_id, update_data=update_data)

    return ResponseModel( data = db_user, message="Cập nhật thông tin thành công!")


@router.put("/password/{user_id}", response_model=ResponseModel[UserResponse])
def user_update_password(
    user_id: int, update_data: UserUpdatePassword,
    db: Session = Depends(connect_db), current_user: User = Depends(get_current_user)
):
    """ Thay vì trả về schemas cập nhật mật khẩu thì nên trả về thông tin cả User đẻ tăng tính bảo mật hơn!"""
    db_user = logic_update_password(db=db, current_user_id= current_user.id, target_user_id=user_id, update_data = update_data)

    return ResponseModel( data = db_user, message="Cập nhật mật khẩu thành công!")



