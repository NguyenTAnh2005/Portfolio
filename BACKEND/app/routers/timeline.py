from fastapi import APIRouter, Depends, Query, Form, UploadFile, File
from typing import Literal, Optional, Union
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db_connection import connect_db
from app.schemas.response import ResponseModel
from app.core.security import get_current_admin
from app.models.models import User
from app.services.helper import to_optional_int

from app.schemas import timeline as schemas_timeline
from app.crud import timeline as timeline_crud
from app.services import timeline as timeline_logic

BASE_URL = settings.BASE_API_URL

router = APIRouter(
    prefix=BASE_URL+"/timelines",
    tags=["Timelines"]
)

@router.post("/", response_model=ResponseModel[schemas_timeline.Response])
def create_timeline(
    title: str = Form(...), organization: str = Form(...),
    desc: str = Form(...), start_end: str = Form(...),
    sort_order: int = Form(...),
    img_file: UploadFile = File(...),
    db: Session = Depends(connect_db), 
    current_admin: User = Depends(get_current_admin) 
):
    """
    ## API tạo mới timeline
        + Nhận field text qua Form(...) + file ảnh qua UploadFile (multipart/form-data)
        + Gọi hàm logic [tải ảnh, ánh xạ filed Text vào Pydantic class, gọi crud create]
        + --> Trả về object đã tạo được
    """
    # Do các trường bắt buộc nhập nên ko cần validate bên routers (nhập input ko juan)

    new_timeline = timeline_logic.create_timeline(
        db=db, title=title, 
        organization=organization, desc=desc, 
        start_end=start_end, sort_order=sort_order,
        img_file=img_file
    )
    
    return ResponseModel(
        message=f"🎉 Timeline was created successfully.",
        data=new_timeline
    )
    
@router.get("/{timeline_id}", response_model=ResponseModel[schemas_timeline.Response])
def get_timeline(
    timeline_id: int, 
    db: Session = Depends(connect_db)
):
    """
    ## API lấy thông tin timeline với id
        + Nhận id timeline và trả về kết quả tương ứng từ func bên crud.
        + Trả về kết quả dưới dạng ResponseModel
    """
    found_timeline = timeline_crud.get_by_id(db=db, timeline_id=timeline_id)
    return ResponseModel(
        message=f"🎉 Timeline was found successfully.",
        data= found_timeline
    )

@router.get("/", response_model=ResponseModel[schemas_timeline.PaginationResponse])
def list_timelines(
    db: Session = Depends(connect_db),
    skip: int = Query(0, ge=0, description="Số bản ghi muốn bỏ qua: "),
    limit: int = Query(30, ge=1, le=30, description="Số bản ghi tối đa trên 1 trang: "),
    sort_by: Literal["id", "sort_order"] = Query("id", description="Sắp xếp theo cột nào khi truy vấn (Default: ID) : "),
    order: Literal["desc", "asc"] = Query("asc", description="Sắp xếp theo chiều nào tăng dần - ASC, giảm dần - DESC (Default: DESC) : ")
):
    """
    ## API trả về danh sách timeline với các thông số.
        + Gọi hàm crud trả về danh sách, lưu biến kết quả
        + Trả về kết quả dưới dạng ResponseModel
    """
    response = timeline_crud.get_all(
        db=db, skip=skip, limit=limit,
        sort_by=sort_by, order=order
    )

    return ResponseModel(
        message=f"🎉 Timeline list retrieved successfully.",
        data=response
    )

@router.put("/{timeline_id}", response_model=ResponseModel[schemas_timeline.Response])
def update_timeline(
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
    ## API cập nhật thông tin Timeline qua id
        + Nhận target_id, field_text (title, desc,...) qua Form(...), file ảnh qua UploadFile
    ### Xử lý input (Do tính chất input của swagger ko điền auto ""):
        + [int ko thể bằng ""] -> sort_order: từ str "" --> 1 biến mới int gán None 
        + [File ko thể bằng ""] ->  img_file: từ str "" --> File gán None do có Union  
        + Gọi hàm logic update:(tự xử lý lọc key-value -> dict -> parse sang pydantic, gọi crud cập nhật, xóa ảnh cũ, trả về object đã cập nhật)
        + Return ResponeModel với data là Object đã cập nhật
    """
    # Xem chi tiết funct file helper 
    sort_order_int = to_optional_int(sort_order)
    # isinstance ktra xem có phải là chuỗi
    if isinstance(img_file, str) or (img_file and not img_file.filename):
        img_file = None
    response = timeline_logic.update_timeline(
        db=db, target_id=timeline_id,
        title=title, organization=organization, 
        desc=desc, start_end=start_end, 
        sort_order= sort_order_int,
        img_file=img_file
    )
    return ResponseModel(
        message=f"🎉 Timeline was updated successfully!",
        data=response
    )

@router.delete("/{timeline_id}", response_model=ResponseModel)
def delete_timeline(
    timeline_id: int,
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    ## API xóa timeline. 
        + Gọi CRUD delete (xóa timeline --> call logic xóa ảnh) --> Logic (Xóa ảnh, trả message)
        + Trả về kết quả dưới dạng ResponseModel
    """
    timeline_logic.delete_timeline(db=db, target_id=timeline_id)
    return ResponseModel(
        message=f"🎉 The Timeline with ID [{timeline_id}] has been deleted successfully.",
        data=[]
    )


