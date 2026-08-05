from sqlalchemy.orm import Session
from fastapi import status
from sqlalchemy import asc, desc
from typing import Optional

from app.core.security import AppException
from app.models.models import Achievement

from app.schemas import achievement as schemas_achieve

def get_by_id(db: Session, achieve_id: int):
    """
    CRUD nhận id achievements và trả về kết quả tương ứng. 
    + Lỗi nếu không tìm thấy - App Exception
    + Trả về object nếu có
    """
    db_achieve = db.query(Achievement).filter(Achievement.id == achieve_id).first()
    if not db_achieve:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ACHIEVEMENT_NOT_FOUND",
            message=f"❌ The achievement does not exist in system. Please verify the ID and try again."
        )
    return db_achieve

def get_all(
  db: Session,
  skip: int, 
  limit: int,
  sort_by:str,
  order: str
):
    """
    Func nhận các thông số lọc để trả về danh sách Achievements .
    """
    query = db.query(Achievement)
    sort_col = getattr(Achievement, sort_by, Achievement.id)
    if order == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    total = query.count()
    list_achieves = query.offset(skip).limit(limit).all()
    return schemas_achieve.PaginationResponse(
        total=total, skip = skip, limit=limit,
        list_data=list_achieves
    )

def create(
    db: Session, create_data: schemas_achieve.Create,
    secure_url: str, public_id: str   
):
    """
    Hàm nhận vào pydantic class Create của Achievement và thông tin ảnh (url, public_id và tiến hành thêm dữ liệu)
    """
    new_achieve = Achievement(
        title = create_data.title,
        desc = create_data.desc, 
        achieved_at = create_data.achieved_at,
        img_url = secure_url,
        img_public_id = public_id
    )

    db.add(new_achieve)
    db.commit()
    db.refresh(new_achieve)

    return new_achieve

def update(
    db: Session, db_achieve: Achievement,
    update_data: schemas_achieve.Update,
    new_secure_url: Optional[str] = None,
    new_public_id: Optional[str] = None
):
    """
    CRUD Nhận các giá trị từ schemas update, thông tin ảnh - nếu có, db_achieve cần cập nhật.
    + Tiến hành cập nhật các giá trị:
        1. Khởi tạo 1 dict lấy hết các trường và giá trị ở update_data, sử dụng exclude_unset = true để loại bỏ các giá trị None.
        2. Nếu như có thuộc tính ảnh thì thêm vào dict các giá trị này.
        3. Ghi đè vào db_achieve bằng cách duyệt qua từng key - value, sử dụng setattr(object, key, value).
    + Return updated_db_achieve
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    if new_secure_url:
        update_dict["img_url"] = new_secure_url
        update_dict["img_public_id"] = new_public_id
    for key, value in update_dict.items():
        setattr(db_achieve, key, value)
    db.add(db_achieve)
    db.commit()
    db.refresh(db_achieve)

    return db_achieve

def delete(
    db: Session,
    db_achieve: Achievement
):
    """
    CRUD nhận vào object achieve và tiến hành xóa 
    """
    db.delete(db_achieve)
    db.commit()
    
    return 
