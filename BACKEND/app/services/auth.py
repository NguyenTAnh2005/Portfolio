from app.crud.user import get_user_by_email
from app.core.security import  verify_password, create_access_token, get_current_user, get_current_admin
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.core.exception import AppException
from fastapi import status
from app.models.models import RoleType


# Logic đăng nhập 
def logic_login(db: Session, input_email: EmailStr, input_password: str):
    """
    1. Kiểm tra xem có user dựa theo email không (CRUD đã tự handle ném lỗi 404 nếu không có). 
    2. Kiểm tra quyền user hiện tại có phải là Admin không mới cho đăng nhập.
    3. Kiểm tra mật khẩu có trùng với mật khẩu lưu trong DB không.
    4. Nếu oke thì tạo và trả về access_token.
    """
    db_user=get_user_by_email(db=db, user_email=input_email)

    if db_user.role != RoleType.ADMIN:
        raise AppException(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code= "NOT_ADMIN",
            message="Chức năng đăng nhập hiện tại chỉ dành cho các tài khoản Admin!"
        )

    is_valid_password = verify_password(plain_password=input_password, hashed_password=db_user.password)
    if not is_valid_password:
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="WRONG_PASSWORD",
            message="Email hoặc mật khẩu chưa chính xác. Vui lòng kiếm tra lại!"
        )
    else:
        # Chọn phần data muốn lưu vào JWT - payload - chứa thông tin -- Email và id user
        data = {
            "sub": db_user.email,
            "data": db_user.id
        }
        jwt_signature = create_access_token(data= data, expires_delta=None)
        return jwt_signature
