from fastapi import APIRouter, Depends, Query, Form, UploadFile, File
from typing import Literal, Optional, Union
from app.core.config import settings
from app.db_connection import connect_db
from app.schemas.response import ResponseModel
from app.core.security import get_current_admin
from sqlalchemy.orm import Session
from app.models.models import User
from app.crud.timeline import get_timeline_by_id, get_all_timeline
from app.schemas.timeline import TimelineResponse, TimelinePaginationResponse
from app.services.helper import to_optional_int
from app.services.timeline import logic_create_timeline, logic_update_timeline, logic_delete_timeline

BASE_URL = settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/timeline",
    tags=["Timeline"]
)

@router.post("/", response_model=ResponseModel[TimelineResponse])
def create(
    title: str = Form(...), organization: str = Form(...),
    desc: str = Form(...), start_end: str = Form(...),
    sort_order: int = Form(...),
    img_file: UploadFile = File(...),
    db: Session = Depends(connect_db), 
    current_admin: User = Depends(get_current_admin) 
):
    """
    - Nhận field text qua Form(...) + file ảnh qua UploadFile (multipart/form-data)
    - Gọi hàm logic [tải ảnh, ánh xạ filed Text vào Pydantic class, gọi crud create]
    --> Trả về object đã tạo được
    """
    # Do các trường bắt buộc nhập nên ko cần validate bên routers (nhập input ko juan)

    new_timeline = logic_create_timeline(
        db=db, title=title, 
        organization=organization, desc=desc, 
        start_end=start_end, sort_order=sort_order,
        img_file=img_file
    )
    
    return ResponseModel(
        message= "Timeline was created successfully!",
        data=new_timeline
    )
    
@router.get("/{timeline_id}", response_model=ResponseModel[TimelineResponse])
def get(
    timeline_id: int, 
    db: Session = Depends(connect_db)
):
    """
    - Nhận id timeline và trả về kết quả tương ứng từ func bên crud.
    """
    found_timeline = get_timeline_by_id(db=db, timeline_id=timeline_id)
    return ResponseModel(
        message="Timeline was found successfully!",
        data= found_timeline
    )

@router.get("/", response_model=ResponseModel[TimelinePaginationResponse])
def get_all(
    db: Session = Depends(connect_db),
    skip: int = Query(0, ge=0, description="Số bản ghi muốn bỏ qua: "),
    limit: int = Query(30, ge=1, le=30, description="Số bản ghi tối đa trên 1 trang: "),
    sort_by: Literal["id", "sort_order"] = Query("id", description="Sắp xếp theo cột nào khi truy vấn (Default: ID) : "),
    order: Literal["desc", "asc"] = Query("asc", description="Sắp xếp theo chiều nào tăng dần - ASC, giảm dần - DESC (Default: DESC) : ")
):
    response = get_all_timeline(
        db=db, skip=skip, limit=limit,
        sort_by=sort_by, order=order
    )

    return ResponseModel(
        message= "Timeline list retrieved successfully!",
        data=response
    )

@router.put("/{timeline_id}", response_model=ResponseModel[TimelineResponse])
def update(
    timeline_id: int,
    title: Optional[str] = Form(None), 
    organization: Optional[str] = Form(None),
    desc: Optional[str] = Form(None), 
    start_end: Optional[str] = Form(None),
    sort_order: Optional[str] = Form(None),
    img_file: Union[UploadFile, str, None] = File(None),
    db: Session = Depends(connect_db), 
    current_admin: User = Depends(get_current_admin) 
):
    """
    - Nhận target_id, field_text (title, desc,...) qua Form(...), file ảnh qua UploadFile
    - Xử lý input (Do tính chất input của swagger ko điền auto ""):
        + [int ko thể bằng ""] -> sort_order: từ str "" --> 1 biến mới int gán None 
        + [File ko thể bằng ""] ->  img_file: từ str "" --> File gán None do có Union  
    - Gọi hàm logic update:(tự xử lý lọc key-value -> dict -> parse sang pydantic, gọi crud cập nhật, xóa ảnh cũ, trả về object đã cập nhật)
    - Return ResponeModel với data là Object đã cập nhật
    """
    # Xem chi tiết funct file helper 
    sort_order_int = to_optional_int(sort_order)
    # isinstance ktra xem có phải là chuỗi
    if isinstance(img_file, str) or (img_file and not img_file.filename):
        img_file = None
    response = logic_update_timeline(
        db=db, target_id=timeline_id,
        title=title, organization=organization, 
        desc=desc, start_end=start_end, 
        sort_order= sort_order_int,
        img_file=img_file
    )
    return ResponseModel(
        message="Timeline was updated successfully!",
        data=response
    )

        

    # db_timeline = None
    # if img_file:
    #     db_timeline = get_timeline_by_id(db=db, timeline_id=target_id)

    # # Sau này nếu cập nhật nếu muốn set none thì phải điền trong form hơi khác, để trống hoặc !="" thì khê, có thể dùng "none" thay thế ???
    # update_data = parse_field_text_to_pydantic_class(
    #     title=title, organization=organization, 
    #     desc=desc, start_end=start_end, 
    #     sort_order= sort_order_int
    # )

    # new_secure_url = None
    # new_public_id = None
    # old_public_id = None

    # if img_file:
    #     new_image = upload_image(img_file.file)   # tự raise AppException nếu lỗi, không cần catch
    #     old_public_id = db_timeline.img_public_id
    #     new_secure_url = new_image["secure_url"]
    #     new_public_id = new_image["public_id"]

    # response = update_timeline(
    #     db=db, target_id=target_id,
    #     update_data=update_data,
    #     img_url=new_secure_url,
    #     img_public_id=new_public_id
    # )   # cũng tự raise nếu lỗi (404 not found, DB lỗi...)

    # if img_file and old_public_id:
    #     try:
    #         destroy_image(old_public_id)
    #     except Exception as e:
    #         # Không fail request vì đây chỉ là dọn rác, DB đã commit thành công rồi
    #         print(f"[WARN] Failed to destroy old image {old_public_id}: {e}")

@router.delete("/{timeline_id}", response_model=ResponseModel)
def delete(
    timeline_id: int,
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    API xóa timeline. 
    - Gọi CRUD delete (xóa timeline --> call logic xóa ảnh) --> Logic (Xóa ảnh, trả message)
    """
    return logic_delete_timeline(db=db, target_id=timeline_id)


