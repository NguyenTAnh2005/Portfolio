from fastapi import UploadFile, status, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.core import cloudinary_config
from app.core.exception import AppException

from app.models.models import Achievement
from app.schemas import achievement as schemas_achieve
from app.crud import achievement as crud_achieve

BASE_FOLDER="Portfolio/Achievements"

def check_conflict(
    db:Session, 
    title: str,
    exclude_id: Optional[str] = None
):
    """
    Func check giá trị trùng lặp:
    + Tạo 1 query lọc sẵn
    + Nếu có exclude id thì nên loại bỏ (!= exclude id)
    + Tạo 1 dict chứa key và value
    + duyệt qua từng item của dict và xét:
        1. tìm colum trong đối tượng bằng getattr với key
        2. gán db_confilct = query filter column tìm được bên trên
        3. nếu có db_conflict thì raise lỗi
        4. return
    """
    query = db.query(Achievement)
    if exclude_id:
        query = query.filter(Achievement.id != exclude_id)
    check_dict = {
        "title": title
    }
    for key, value in check_dict.items():
        col_check = getattr(Achievement, key)
        # if not col_check: Lỗi sẽ trả về dạng Attribute Error
        db_conflict = query.filter(col_check == value).first()
        if db_conflict:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                error_code="CONFLICT_DATA",
                message= f"❌ There is a Achievement object that has this {key} value in the database. Please check and try again."
            )

def create_achievement(
    db: Session,
    title: str,
    desc: str,
    achieved_at: datetime,
    img_file: UploadFile,
):
    """
    Hàm xử lý logic tạo mới Achievement:
    + Kiểm tra trùng lặp
    + Lấy thông tin ảnh
    + Đóng gói và gọi cho crud tạo
    """
    check_conflict(db=db, title= title)

    img_info = cloudinary_config.upload_image(folder_name=BASE_FOLDER, file=img_file.file)

    create_data = schemas_achieve.Create(
        title=title, desc=desc, achieved_at=achieved_at,
    )

    return crud_achieve.create(
        db=db, create_data=create_data,
        secure_url=img_info["secure_url"],
        public_id=img_info["public_id"]
    )

def update_achievement(
    db: Session,
    target_id: int,

    title: Optional[str] = Form(None),
    desc: Optional[str] = Form(None),
    achieved_at: Optional[datetime] = Form(None),
    img_file: Optional[UploadFile] = File(None)
):
    """
    LOGIC UPDATE ACHIEVEMENT
    Nhận vào các giá trị input từ bên router (Form, File), achieve_id.
    Thực hiện:
        1. Check có trong db.
        2. Check trùng lặp dữ liệu.
        3. Thực hiện gán các giá trị cần cập nhật vào pydantic class Update. 
        4. Nếu có ảnh thì lưu lại biến public_id, sau đó upload ảnh lên và lấy thông tin.
        5. Gọi hàm CRUD update và gán biến đầu ra hàm này (để tí trả về).
        6. Nếu có ảnh thì thực hiện xóa ảnh.
    """
    db_achieve = crud_achieve.get_by_id(db=db, achieve_id=target_id)

    check_conflict(db=db, title=title, exclude_id=target_id)
    update_data = schemas_achieve.Update()
    update_input = {
        "title":title,
        "desc":desc,
        "achieved_at":achieved_at,
    }

    for key, value in update_input.items():
        if value is None:
            continue
        if isinstance(value, str) and value == "":
            continue
        setattr(update_data, key, value)

    new_secure_url = None
    new_public_id = None
    old_public_id = None
    if img_file:
        old_public_id = db_achieve.img_public_id
        new_img = cloudinary_config.upload_image(
            folder_name=BASE_FOLDER,
            file=img_file.file
        )
        new_secure_url = new_img["secure_url"]
        new_public_id = new_img["public_id"]

    updated_db_achieve = crud_achieve.update(
        db=db, db_achieve=db_achieve, 
        update_data=update_data, 
        new_secure_url=new_secure_url, 
        new_public_id=new_public_id
    )

    if img_file:
        cloudinary_config.destroy_image(old_public_id)

    return updated_db_achieve

def delete_achievement(
    db: Session, target_id: int
):
    """
    LOGIC XÓA ACHIEVEMENT
        + Kiểm tra có trong db ?
        + lưu biến img_public_id
        + Gọi crud xóa
        + gọi dịch vụ Cloudinary xóa ảnh
    """
    db_achieve = crud_achieve.get_by_id(db=db, achieve_id=target_id)

    delete_img_public_id = db_achieve.img_public_id

    crud_achieve.delete(db= db, db_achieve= db_achieve)

    cloudinary_config.destroy_image(public_id=delete_img_public_id)
    
    return