from fastapi import status
from sqlalchemy.orm import Session
from app.models.models import TimeLine
from app.core.exception import AppException
from app.schemas.timeline import TimelineCreate, TimelineResponse, TimelineUpdate, TimelinePaginationResponse
from sqlalchemy import desc, asc
from typing import Optional


# Create
def create_timeline(db: Session, data_create: TimelineCreate, img_url: str, img_public_id:str):
    """
    - Func nhận data: dict theo khung TimeLineCreate 
    - Tạo đối tượng Timeline tương ứng
    - Trả về db model cho router dùng."""

    new_timeline = TimeLine(
        title= data_create.title, organization= data_create.organization, 
        desc= data_create.desc, start_end= data_create.start_end,
        sort_order= data_create.sort_order, 
        img_url= img_url, img_public_id= img_public_id
    )
    db.add(new_timeline)
    db.commit()
    db.refresh(new_timeline)
    return new_timeline

# Get Timeline by id
def get_timeline_by_id(db: Session, timeline_id: int):
    """
    - Func nhận vào là id: timeline cần tìm
    - Trả về kết quả: 
        + App Exception nếu không thấy.
        + Đối tượng timeline nếu tìm thấy.
    """
    db_timeline = db.query(TimeLine).filter(TimeLine.id == timeline_id).first()
    if not db_timeline:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="TIMELINE_NOT_FOUND",
            message="The timeline does not exist in system. Please verify the ID and try again!"
        )
    return db_timeline

# Get All 
def get_all_timeline(
        db: Session,
        skip: int ,
        limit: int,
        sort_by: str,
        order: str
):
    """
    - Func nhận các thông số lọc để trả về danh sách time line .
    - Lưu ý: schema trả về.
    """
    query = db.query(TimeLine)
    # Kiếm sortby dựa theo chuỗi bằng getattr (get attribute) - none thì lấy mặc định là id.
    sort_column = getattr(TimeLine, sort_by, TimeLine.id)
    # query = query.order_by(desc(sort_column)) if order == "desc" else query = query.order_by(asc(sort_column))
    if order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(asc(sort_column))

    total = query.count()
    list_data = query.offset(skip).limit(limit).all()

    return TimelinePaginationResponse( total=total, skip=skip, limit=limit, list_data=list_data)
    
# Update
def update_timeline(
    db: Session, target_id: int, 
    update_data: TimelineUpdate,
    img_url: Optional[str] = None, 
    img_public_id: Optional[str] = None
):
    """
    - Func nhận id target và dữ liệu cần cập nhật để cập nhật.
    - Tìm kiếm đối tượng.
    - Thực hiện cập nhật nếu có. 
    - Trả về đối tượng với schema - Timeline Response. 
    """
    db_timeline = get_timeline_by_id(db=db, timeline_id=target_id)

    update_data_dict = update_data.model_dump(exclude_unset=True)
    if img_url:
        update_data_dict["img_url"] = img_url
    if img_public_id:
        update_data_dict["img_public_id"] = img_public_id

    for key, value in update_data_dict.items():
        setattr(db_timeline, key, value)

    db.add(db_timeline)
    db.commit()
    db.refresh(db_timeline)

    return db_timeline

# Delete
def delete_timeline(
    db: Session, target_id: int, db_timeline: TimeLine
):
    """
    Funct nhận vào là db, id timelime cần xóa và object db_timeline
    - Xóa Timeline
    - Không return vì đây là 1 phần code bên logic delete
    """
    # Bên logic đã kiếm rồi nên bên này chỉ có xóa thôi
    # db_timeline = get_timeline_by_id(db=db, timeline_id=target_id)
    db.delete(db_timeline)
    db.commit()

