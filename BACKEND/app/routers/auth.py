from fastapi import APIRouter, Depends
from app.services.auth import logic_login
from app.core.config import settings
from app.schemas.auth import TokenResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db_connection import connect_db
from app.schemas.response import ResponseModel
from app.schemas.user import UserResponse
from app.models.models import User
from app.core.security import get_current_admin

BASE_URL= settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/auth",
    tags= ["Authentication"]
)

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db : Session = Depends(connect_db)
):
    jwt_sig = logic_login(db= db, input_email=form_data.username, input_password=form_data.password)
    return {
        "access_token": jwt_sig,
        "token_type": "bearer",
        "message": "Bạn đã đăng nhập thành công!"
        }
    # return ResponseModel( data={ "access_token": jwt_sig,"token_type": "bearer"}, message="Đăng nhập thành công!")

@router.get("/get-me", response_model=ResponseModel[UserResponse])
def getMe(
    current_admin: User = Depends(get_current_admin)
):
    """
    - API trả về thông tin admin hiện tại.
    - Sử dụng get_current_admin - (func giải mã jwt và tìm kiếm user theo user_id được lưu để tạo jwt token) để trả về thông tin admin hiện tại.
    - Trả về Data theo cấu trúc ResponseModel
    """
    return ResponseModel(
        data=current_admin,
        message="Lấy thông tin Admin hiện tại thành công!"
    )



    