from fastapi import UploadFile, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from typing import Optional
from app.models.models import Project
from app.core.exception import AppException

from app.core import cloudinary_config as cloud_config
from app.core import github_service
from app.schemas import project as schemas_project
from app.crud import project as crud_project

BASE_FOLDER="Portfolio/Projects"

# Check trùng lặp
def check_conflict(
    db: Session, 
    title: str,
    project_url: int,  
    exclude_id: Optional[int] = None, # Id loại trừ, nếu cập nhật thì phải loại TH id mình đang update.
):
    """
    Func check trùng lặp dữ liệu. 
    - Duyệt qua từng lớp lọc và trả về lỗi tương ứng với từng field trùng, giúp Admin debug tốt hơn. 
    """
    db_query = db.query(Project)

    if exclude_id: 
        db_query = db_query.filter(Project.id!=exclude_id)
    check_dict = { 
        "title": title, "project_url": project_url
    }
    for key, value in check_dict.items():
        if value and value is not None:
            column = getattr(Project, key)
            conflict = db_query.filter(column == value).first()
            if conflict:
                raise AppException(
                    status_code=status.HTTP_409_CONFLICT,
                    error_code="CONFLICT_DATA",
                    message= f"There is a Project object that has this {key} value in the database. Please check and try again."
                )

# Logic thêm dữ liệu 
async def create_project(
    db: Session,
    title: str,  project_url: str,
    img_file: UploadFile,
    list_tech: Optional[list[str]] = None,
):
    """
    Func tạo mới project
    - Nhận các đầu vào từ router
    1. Check trùng lặp
    2. Fetch repository info qua project_url
    3. Tải ảnh lên, get thông tin url cần thiết
    4. Tổng hợp lại gửi cho CRUD 
    """
    # Lấy thông tin id lớn nhất, scalar giúp biến đổi kết quả dạng Tuple -> Số
    # func.max(...): Hàm của SQLAlchemy để sinh ra lệnh MAX(id) trong SQL.
    # .scalar(): Rất quan trọng. Lệnh này ép kiểu kết quả trả về thành một con số duy nhất 
    # (ví dụ: 42). Nếu không có .scalar(), bạn sẽ nhận về một Tuple dạng (42,) rất khó xử lý.
    max_id = db.query(func.max(Project.id)).scalar()
    if max_id is None: 
        max_id = 0

    check_conflict( db=db, title=title, project_url=project_url, exclude_id=None)
    repo_response = await github_service.get_repo_info(url= project_url)
    new_image = cloud_config.upload_image(file=img_file.file, folder_name=f"{BASE_FOLDER}/{max_id+1}")

    repo_info = repo_response.data
    create_data = schemas_project.Create(
        title=title, list_tech=list_tech, project_url=project_url,
        desc=repo_info["desc"], list_lang= repo_info["list_lang"],
        created_at= github_service.parse_github_datetime(repo_info["created_at"]),
        last_updated= github_service.parse_github_datetime(repo_info["last_updated"]) 
    )

    return crud_project.create(
        db=db, create_data=create_data,
        img_url=new_image["secure_url"],
        img_public_id=new_image["public_id"]
    )

# Logic cập nhật project
# Vì nếu làm chung form như Timeline thì sẽ vướng ở chỗ list_tech. Gửi none lên là ko muốn cập nhật hay để nó rỗng ???. Vì list_tech được phép rỗng. 
# Tách ra thì request sẽ nhiều hơn nhưng giải quyết được vấn đề trên
async def update_project_text_form(
    db:Session, target_id: int,
    update_data: schemas_project.UpdateTextForm
):
    """
    Nhận class pydantic từ bên router
    Không cần check loại bỏ None hay "" vì router ko dùng Form(...) để gộp chung với file img nữa.
    1. Từ target_id đầu vào, get_by_id xem có trong db không?
    2. Check trùng lặp dữ liệu với exclude_id = target_id,...
    3. Kiểm tra input project_url có != None ko, nếu true thì thực hiện fetch github repo info
    4. Gửi cục data kèm thêm cái gì cần thiết để CRUD tiến hành cập nhật.
    """
    # 1. Check có trong DB?
    db_project = crud_project.get_by_id(db=db, project_id=target_id)
    # 2. Check trùng lặp
    check_conflict(
        db=db, exclude_id=target_id,
        title=update_data.title, 
        project_url=update_data.project_url,
    )
    # 3. Kiểm tra project_url
    update_data_fetch = schemas_project.UpdateFetchRepo()
    if update_data.project_url is not None:
        response = await github_service.get_repo_info(update_data.project_url)
        info_response = response.data
        #data = {
        #     "desc": repo_data.get("description"),
        #     "created_at": repo_data.get("created_at"),
        #     "last_updated":repo_data.get("pushed_at"),
        #     "list_lang": list(lang_data.keys())
        # }

        update_data_fetch.desc = info_response["desc"]
        update_data_fetch.list_lang = info_response["list_lang"]
        update_data_fetch.created_at = github_service.parse_github_datetime(info_response["created_at"])
        update_data_fetch.last_updated = github_service.parse_github_datetime(info_response["last_updated"])

    # 4. Gọi CRUD 
    return crud_project.update_text_form(
        db=db, db_project= db_project,
        update_data= update_data,
        update_data_fetch= update_data_fetch
    )

# Logic update img project 
def update_project_img_file(
    db: Session, target_id: int, img_file: UploadFile
):
    """
    ## Nhận các đầu vào: db, target_id, img_file
        + kiểm tra có trong db?
        + lưu public_id cũ để xóa, upload ảnh lên
        + gọi crud cập nhật (lưu biến)
        + xóa ảnh cũ
        + trả về object cho router
    """
    # kiểm tra có trong db?
    db_project = crud_project.get_by_id(db=db, project_id=target_id)
    # lưu public_id cũ để xóa, upload ảnh lên
    old_img_public_id = db_project.img_public_id
    new_img = cloud_config.upload_image(file=img_file.file, folder_name=f"{BASE_FOLDER}/{target_id}")
    # gọi crud cập nhật (lưu biến)
    updated_project = crud_project.update_img_file(
        db=db, db_project= db_project,
        new_secure_url= new_img["secure_url"],
        new_public_id=new_img["public_id"]
    )
    # xóa ảnh cũ
    cloud_config.destroy_image(old_img_public_id)
    # trả về object cho router
    return updated_project

# Logic sync project info
async def sync_project(
    db: Session, target_id: int
):
    """
    ## Func đồng bộ thông tin project khi repo trên github có cập nhật thông tin (desc, language)
        + 1. Kiểm tra có trong db, nếu có lấy thông tin project_url
        + 2. fetch info và gán vào cho pydantic class 
        + 3. Gọi crud 
    """
    db_project = crud_project.get_by_id(db=db, project_id= target_id)
    target_project_url = db_project.project_url
    # gọi fetch data và gán từng giá trị cho pydantic class
    repo_response = await github_service.get_repo_info(target_project_url)
    repo_info = repo_response.data
    sync_data = schemas_project.UpdateFetchRepo()
    sync_data.desc = repo_info["desc"] 
    sync_data.list_lang = repo_info["list_lang"] 
    sync_data.created_at = github_service.parse_github_datetime(repo_info["created_at"])
    sync_data.last_updated = github_service.parse_github_datetime(repo_info["last_updated"])

    return crud_project.sync(db= db, db_project=db_project, sync_data=sync_data)

# Logic delete project 
def delete_project(
    db: Session, target_id: int    
):
    """
    Func Logic xóa object project
    + 1. Kiểm tra có trong db, lưu biến public_id
    + 2. Gọi crud xóa object
    + 3. Tiến hành xóa ảnh + folder trên cloudinary
    """
    db_project = crud_project.get_by_id(db= db, project_id= target_id)
    deleted_public_id = db_project.img_public_id

    crud_project.delete(db= db, db_project= db_project)

    cloud_config.destroy_image(public_id=deleted_public_id)
    cloud_config.delete_folder(folder_name=f"{BASE_FOLDER}/{target_id}")

    return

    