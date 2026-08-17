from fastapi import status
from sqlalchemy.orm import Session

from app.models.models import Info
from app.core.exception import AppException
from app.schemas import info as schemas_info

# Get Info by ID
def get_by_id(db: Session, info_id: int) -> Info:
    """Hàm này nhận vào id info và trả về thông tin đầy đủ của Info."""
    db_info = db.query(Info).filter(Info.id == info_id).first()
    if not db_info:
        # Kiểm tra lại hệ thống database, chạy lại seed data nếu cần thiết. 
        raise AppException(
            status_code= status.HTTP_404_NOT_FOUND,
            error_code="INFO_NOT_FOUND",
            message=f"❌ The Info does not exist in system. Please verify the ID and try again."
        )
    return db_info

# Update Info by ID
def update(db: Session, db_info: Info, update_data: schemas_info.Update):
    """
    Hàm này nhận vào id_info và update_data (Schema đã qua Pydantic).
    Chỉ làm đúng việc là gán đè data mới lên data cũ và lưu lại.
    1. Biến bản thân object pydantic update_data -> dict để dễ thao tác, tách các cặp key - value
    2. Sử dụng excluse_unset = True chỉ để nhận cập nhật giá trị khác với mặc định ( tức là user không gửi lên), tránh mất oan dữ liệu. 
     - lệnh setattr(db_user, key, value) thay giá trị mới vào Object Info cũ một cách tự động.
    3. Lưu xuống DB
    """

    update_data_dict = update_data.model_dump(exclude_unset=True)
    
    for key, value in update_data_dict.items():
        setattr(db_info, key, value)

    db.add(db_info)
    db.commit()
    db.refresh(db_info)
    
    return db_info