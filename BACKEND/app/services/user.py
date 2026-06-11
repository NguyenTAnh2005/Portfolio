from sqlalchemy.orm import Session
from app.schemas.user import UserUpdateInfo, UserUpdatePassword
from app.core.security import verify_password, get_password_hash
from app.core.exception import AppException
from fastapi import status
from app.schemas.user import UserUpdateInfo, UserUpdatePassword
from app.models.models import User
from sqlalchemy import or_
from app.crud.user import update_username_email, update_password, get_user

# Kiếm tra có thay đổi đúng tài khoản hay không     
def check_true_account(current_user_id: int, target_user_id: int):
    """ Kiểm tra xem có đang thay đổi đúng tài khoản, chỉ cho phép tự cập nhật chính mình."""
    if current_user_id!= target_user_id:
        raise AppException(
            status_code = status.HTTP_403_FORBIDDEN,
            error_code = "NOT_ALLOWED",
            message="Bạn không được phép cập nhật thay đổi thông tin cho tài khoản khác!"
        )
    return

# Kiếm tra trùng email và username
def check_conflict(db:Session, target_user_id: int, data: UserUpdateInfo):
    """
    1. Tạo filter_conflict
    2. Kiểm tra: 
        + Nếu có gửi trường email thì thêm query truy vấn orm tìm kiếm user theo email
        + Tương tự với username
    3. Kiếm tra:
        + Nếu filter_conflict rỗng thì cho qua 
        + Tìm kiếm user conflict dựa theo các query điều kiện lọc trong filter_conflict,
          áp dụng or_ để tiết kiệm số lần kết nối đến db.
        + Nếu như tìm thấy báo lỗi trùng, else cho qua. 
    """
    filter_conflict = []
    if data.email is not None:
        filter_conflict.append(User.email == data.email)
    if data.username is not None:
        filter_conflict.append(User.username == data.username)

    if len(filter_conflict) == 0:
        return
    
    user_conflict = db.query(User).filter(or_(*filter_conflict)).filter(User.id != target_user_id).first()
    if user_conflict:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT_UPDATE_DATA",
            message="Email hoặc username mới đã tồn tại trong hệ thống. Vui lòng đổi lại Email hoặc Username!"
        )
    return


# Logic update username - email
def logic_update_user_email(db: Session, current_user_id: int, target_user_id: int, update_data: UserUpdateInfo):
    """
    1. Kiểm tra cập nhật đúng tài khoản không (Tránh user này sửa data của user khác)
    2. Kiểm tra trùng lặp bằng check_conflict
    3. Gọi hàm cập nhật crud làm việc 
    """
    check_true_account(current_user_id= current_user_id, target_user_id= target_user_id)
    check_conflict(db=db, target_user_id=target_user_id, data=update_data)
    return update_username_email(db=db, target_user_id=target_user_id, update_data=update_data)

# Logic update password
def logic_update_password(db:Session, current_user_id: int, target_user_id: int,  update_data: UserUpdatePassword):
    """
    1. Kiểm tra cập nhật đúng tài khoản không.
    2. Kiểm tra old password nhập có trùng như đã lưu trong db không.
    3. Nếu không trùng thì báo lỗi, còn nếu trùng thì trả về mật khẩu mới được hash cho CRUD làm việc. 
    """
    check_true_account(current_user_id= current_user_id, target_user_id= target_user_id)
    db_user = get_user(db=db, user_id=target_user_id)
    is_valid_password = verify_password(plain_password=update_data.old_password, hashed_password=db_user.password)
    if not is_valid_password:
        raise AppException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            error_code="NOT_VALID_OLD_PASSWORD",
            message="Mật khẩu cũ không chính xác, chưa thể thay đổi mật khẩu mới!"
        )
    hashed_new_password = get_password_hash(update_data.new_password)
    return update_password(db=db, target_user_id=target_user_id, new_hashed_password=hashed_new_password)


