from fastapi import APIRouter, Depends, Query, Form, File, UploadFile
from typing import Literal, Union, Optional
from sqlalchemy.orm import Session
from app.db_connection import connect_db
from datetime import datetime



from app.core.config import settings
from app.models.models import User
from app.core.security import get_current_admin

from app.schemas.response import ResponseModel
from app.schemas import achievement as schemas_achieve
from app.crud import achievement as crud_achieve
from app.services import achievement as logic_achieve

BASE_URL = settings.BASE_API_URL
router = APIRouter(
    prefix=BASE_URL+"/achievements",
    tags=["Achievements"]
)

@router.get("/{achievement_id}", response_model= ResponseModel[schemas_achieve.Response])
def get_achievement(
    achievement_id: int,
    db: Session = Depends(connect_db)
):
    """
    ## API lấy thông tin achievement với id
        + Nhận id achievement và trả về kết quả tương ứng từ func bên crud.
        + Trả về kết quả dưới dạng ResponseModel
    """
    result = crud_achieve.get_by_id(db=db, achieve_id=achievement_id)

    return ResponseModel(
        message=f"🎉 Achievement was found successfully.",
        data= result
    )

@router.get("/", response_model=ResponseModel[schemas_achieve.PaginationResponse])
def list_achievements(
    db: Session = Depends(connect_db),
    limit: int = Query(20, ge=1, le=20, description=" Số bản ghi tối đa trong response: "),
    skip: int = Query(0, ge=0, description="Số bản ghi muốn bỏ qua: "),
    sort_by: Literal["id", "achieved_at"] = Query("id", description="Sắp xếp theo cột nào khi truy vấn (Default: ID) : "),
    order: Literal["asc", "desc"] = Query("desc", description="Sắp xếp theo chiều nào tăng dần - ASC, giảm dần - DESC (Default: DESC) : ")
):
    """
        ## API trả về danh sách achievements với các thông số.
        + Gọi hàm crud trả về danh sách, lưu biến kết quả
        + Trả về kết quả dưới dạng ResponseModel
    """
    result = crud_achieve.get_all(
        db= db, limit= limit, skip= skip,
        sort_by=sort_by, order=order
    )
    return ResponseModel(
        message=f"🎉 Achievements list retrieved successfully.",
        data=result
    ) 

@router.post("/", response_model=ResponseModel[schemas_achieve.Response])
def create_achievement(
    db: Session = Depends(connect_db),
    title: str = Form(...),
    desc: str = Form(...),
    achieved_at: datetime = Form(
        ...,
        description="Định dạng ISO 8601 kèm timezone [YY-MM-DDTHH:MM:SS+Timezone] , ví dụ: 2025-11-16T14:30:00+07:00",
        example="2025-11-16T14:30:00+07:00"
    ),
    img_file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin)
):
    """
    ## API tạo mới achievement
    + Nhận field text qua Form(...) + file ảnh qua UploadFile (multipart/form-data)
    + Gọi hàm logic tạo achievement
    + --> Trả về object đã tạo được
    """
    result = logic_achieve.create_achievement(
        db=db, title=title, desc=desc, achieved_at=achieved_at, img_file=img_file
    )
    return ResponseModel(
        message=f"🎉 Achievement was created successfully.",
        data=result
    )

@router.put("/{achievement_id}", response_model= ResponseModel[schemas_achieve.Response])
def update_achievement(
    achievement_id: int,
    db: Session = Depends(connect_db),
    title: Optional[str] = Form(None),
    desc: Optional[str] = Form(None),
    achieved_at: Optional[datetime] = Form(None, description="Định dạng ISO 8601 kèm timezone [YY-MM-DDTHH:MM:SS+Timezone] , ví dụ: 2025-11-16T14:30:00+07:00"),
    img_file: Optional[Union[UploadFile, str, None]] = File(None),
    current_admin: User = Depends(get_current_admin)
):
    """
    ## API cập nhật thông tin Achievement qua id
        + Nhận achievement_id, field_text (title, desc,...) qua Form(...), file ảnh qua UploadFile
    ### Xử lý input (Do tính chất input của swagger ko điền auto ""):
        + [File ko thể bằng ""] ->  img_file: từ str "" --> File gán None do có Union.
        + Gọi hàm logic update.
        + Return ResponeModel với data là Object đã cập nhật.
    """
    if isinstance(img_file, str) or (img_file and not img_file.filename):
        img_file = None
    result = logic_achieve.update_achievement(
        db= db, target_id=achievement_id,
        title=title, desc=desc, achieved_at=achieved_at, img_file=img_file
    )

    return ResponseModel(
        message=f"🎉 Achievement was updated successfully!",
        data= result
    )

@router.delete("/{achievement_id}", response_model=ResponseModel)
def delete_achievement(
    achievement_id: int,
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    ## API xóa Achievement. 
        + Gọi CRUD delete (xóa achievement --> call logic xóa ảnh) --> Logic (Xóa ảnh, trả message)
        + Trả về kết quả dưới dạng ResponseModel
    """
    logic_achieve.delete_achievement(db=db, target_id=achievement_id)
    return ResponseModel(
        message=f"🎉 The Achievement with ID [{achievement_id}] has been deleted successfully.",
        data=[]
    )