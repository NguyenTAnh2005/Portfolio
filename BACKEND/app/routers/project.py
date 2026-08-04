from fastapi import APIRouter, Depends, Query, status, Form, File, UploadFile
from typing import Optional, Literal
from sqlalchemy.orm import Session

from app.schemas.response import ResponseModel
from app.db_connection import connect_db
from app.core.security import get_current_admin
from app.models.models import User
from app.core.config import settings

from app.schemas import project as schemas_project
from app.crud import project as project_crud
from app.services import project as project_logic

BASE_URL = settings.BASE_API_URL
router = APIRouter(
    prefix=BASE_URL+"/projects",
    tags=["Projects"]
)

@router.post("/", response_model=ResponseModel[schemas_project.Response])
async def create_project(
    db: Session = Depends(connect_db),
    title: str = Form(...), 
    list_tech: Optional[list[str]] = Form(None), 
    project_url: str = Form(...),
    img_file: UploadFile = File(...),
    current_admin : User = Depends(get_current_admin),
):
    """
    ## API tạo mới. 
    ### Nhận vào các thành phần: 
        + Các input Field: title, list_tech, project_url -> Form(...)
        + Các input File: img_file -> File(...)
    ### Xử lý:
        + 1. Gọi service logic create 
        + 2. Trả respone dưới dạng Response Model
    """
    new_project = await project_logic.create_project(
        db=db, title=title, project_url=project_url, 
        list_tech=list_tech, img_file=img_file
    )
    return ResponseModel(
        message=f"🎉 New Project was created successfully.",
        data=new_project
    )

@router.get("/{project_id}", response_model= ResponseModel[schemas_project.Response])
def get_project(
    project_id: int,
    db: Session = Depends(connect_db),
):
    """
    ## API trả về thông tin project theo id nhận vào. 
        + Gọi hàm crud trả về thông tin project theo id.
        + Trả về kết quả dưới dạng ResponseModel
    """
    db_project = project_crud.get_by_id(db=db, project_id=project_id)
    return ResponseModel(
        message="Project was found successfully.",
        data=db_project,
    )

@router.get("/", response_model= ResponseModel[schemas_project.PaginationResponse])
def list_projects(
    db: Session = Depends(connect_db),
    skip: int = Query(0, ge=0, description="Số bản ghi muốn bỏ qua: "),
    limit: int = Query(30, ge=1, le=30, description="Số bản ghi tối đa trên 1 trang: "),
    title: str = Query(None, description=" Tìm theo tên dự án: " ),
    tech: str = Query(None, description="Lọc dự án theo tên thư viện hay framework (React, Tailwind,...): "),
    lang: str = Query(None, description="Lọc dự án theo tên ngôn ngữ lập trình (JavaScript, HTML,..): "),
    sort_by: Literal["id", "created_at", "last_updated"] = Query("id", description="Sắp xếp theo cột nào khi truy vấn (Default: ID) : "),
    order: Literal["desc", "asc"] = Query("desc", description="Sắp xếp theo chiều nào tăng dần - ASC, giảm dần - DESC (Default: DESC) : ")
):
    """
    ## API trả về danh sách các project dựa theo các đầu vào.
        + Gọi hàm crud get_all_project. 
        + + Trả về kết quả dưới dạng ResponseModel.
    """
    list_project = project_crud.get_all(
        db=db, skip= skip, limit= limit,
        sort_by=sort_by, order= order,
        title=title, tech=tech, lang=lang
    )

    return ResponseModel(
        message="Project list retrieved successfully.",
        data=list_project
    )

@router.patch("/{project_id}", response_model=ResponseModel[schemas_project.Response])
async def update_project_text(
    project_id: int, 
    update_data: schemas_project.UpdateTextForm,
    db:Session = Depends(connect_db),
    current_admin:User = Depends(get_current_admin)
):
    """
    ## API cập nhật các field text cho Project
    ### Tách riêng update text form để giải quyết vấn đề list_tech:
        + 1. list_tech được phép null nhưng gửi none hay "" ở trong Form thì nên xử lý ntn.
        + 2. Bỏ ra khỏi Pydantic update hay update rỗng ???
        + 3. Tách riêng ntn sẽ kiểm soát chặt chẽ nhất. Update thì gửi lên, không update thì không gửi. 
        + 4. Dùng Form thì mặc định đều gửi hết, chẳng qua là gửi nó khác None hoặc "" không thôi.
    ### Đầu vào:
        + db: kết nối db 
        + project_id: project cần cập nhật
        + update_data: (pydantic class) Cục dữ liệu cần cập nhật, này là gửi dạng JSON != Form (3,4)
    ### Xử lý 
        + Gọi hàm logic update.
        + Trả về kết quả kèm message.
    """
    result = await project_logic.update_project_text_form(db=db, target_id=project_id, update_data=update_data)
    return ResponseModel(
        message=f"🎉 Project was updated successfully.",
        data=result
    )

@router.patch("/image/{project_id}", response_model=ResponseModel[schemas_project.Response])
def update_project_img(
    project_id: int,
    db: Session = Depends(connect_db),
    img_file: UploadFile = File(...),
    current_admin: User = Depends(get_current_admin)
):
    """
    ## API cập nhật các thuộc tính liên quan đến ảnh của models. 
    ### Đầu vào: 
        + db, project_id, 
        + file ảnh (bắt buộc có, vì endpoint này chỉ có 1 input nhập)
    ### Xử lý: 
        + 1. Tiến hành gọi hàm update ảnh bên logic 
        + 2. Trả về ResponeModel
    """
    result = project_logic.update_project_img_file(
        db= db, target_id= project_id,
        img_file= img_file
    )

    return ResponseModel(
        message=f"🎉 Project image was updated successfully.",
        data=result
    )

@router.patch("/sync/{project_id}", response_model=ResponseModel[schemas_project.Response])
async def sync_project(
    project_id: int,
    db: Session= Depends(connect_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    ## API cập nhật đồng bộ thông tin project
    ### Nếu bên trên repo github có thay đổi (desc, languages,...) thì đồng bộ ngay.
        + 1. Gọi func logic bên service (func này xử lý -> gọi crud -> trả về object)
        + 2. Trả về đối tượng dưới dạng ResponseModel
    """
    result = await project_logic.sync_project(db=db, target_id=project_id)
    return ResponseModel(
        message=f"🎉 Project was synced successfully.",
        data=result
    )

@router.delete("/{project_id}", response_model=ResponseModel)
def delete_project(
    project_id: int,
    db: Session = Depends(connect_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    ## API xóa Project theo id.
    ### Xóa project theo project_id
        + 1. Gọi func logic xóa (tìm kiếm, xóa crud, xóa ảnh, xóa folder)
        + 2. Return chay kết quả xóa thành công (data rỗng)
    """
    project_logic.delete_project(db=db, target_id=project_id)
    return ResponseModel(
        message=f"🎉 The Project with ID [{project_id}] has been deleted successfully.",
        data=[]
    )