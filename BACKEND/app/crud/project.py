from fastapi import status
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from app.core.exception import AppException
from app.models.models import Project
from app.schemas import project as schemas_project


# get by id
def get_by_id(db:Session, project_id: int):
    """
    Func tìm kiếm project theo id.
    - Nhận vào: bd Session và int id project cần tìm
        + không thấy thì trả lỗi
        + Có thì trả về object
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="PROJECT_NOT_FOUND",
            message=f"❌ The project does not exist in system. Please verify the ID and try again."
        )
    return db_project

# get all
def get_all(
    db: Session,
    skip: int,
    limit: int,
    sort_by: str ,
    order: str,
):
    """
    Func trả về danh sách project, các input:
    - skip: Số bản ghi bỏ qua
    - Limit: Số bản ghi tối đa trong danh sách trả về. 
    - sort_by: Sắp xếp theo cột nào 
    - order: xếp theo tăng(asc) hay giảm dần(desc) 
    """
    query = db.query(Project)
    # Kiếm sortby dựa theo chuỗi bằng getattr (get attribute) - none thì lấy mặc định là id.
    sort_col = getattr(Project, sort_by, Project.id)

    if order == "desc": query = query.order_by(desc(sort_col))
    elif order == "asc": query = query.order_by(asc(sort_col))

    # count tổng số hiện có trong hệ thống
    total_count = query.count()
    list_data = query.offset(skip).limit(limit).all()

    return schemas_project.PaginationResponse( total = total_count, skip = skip, limit = limit, list_data = list_data )

# create
def create(db: Session, create_data: schemas_project.Create, img_url: str, img_public_id:str):
    """
    Func CURD  tạo mới project nhận các đầu vào: 
        + create_data:(chứa các field Form(...))
        + img_url, img_public_id: từ logic (thông qua upload ảnh trong CloudinaryConfig)
    - Check trùng lặp thì logic (service) lo, oke thì gọi crud ra
    - Tạo mới object Project từ các đầu vào
    - Thêm vào csdl
    """
    new_project = Project(
        title = create_data.title, list_tech = create_data.list_tech, 
        project_url = create_data.project_url,
        desc = create_data.desc, list_lang = create_data.list_lang,
        created_at = create_data.created_at, last_updated = create_data.last_updated,
        img_url = img_url, img_public_id = img_public_id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project
    
# update
def update_text_form(
    db: Session,
    db_project: Project, #porject có id = target_id
    update_data: schemas_project.UpdateTextForm,
    update_data_fetch: schemas_project.UpdateFetchRepo,
):
    """
    - Func cập nhật thông tin dự án. Nhận các input:
        +) db, target_id: id dự án cần update
        +) schema update_data: Class Pydantic chứa các thông tin có thể cập nhật
        +) schema update_data_fetch: Class Pydantic các thông tin fetch repo info nếu như thay đổi project url
    ** Tách ra 1 patch nhỏ thay vì put cùng với ảnh)
    ** Giải quyết triệt để để None hoặc "" là update hay ko. Do có list[str] ko thể xử lý như cách gộp
        - Gửi none là ko cập nhật vậy muốn xóa hết trong list thì làm sao ???

    1. Không cần kiểm tra có trong db ko do logic ktra rồi
    2. Duyệt qua từng key, value --> dùng setattr(object, key, value)
    3. Trả về bd Object để router lấy. 
    """

    update_data_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_data_dict.items():
        setattr(db_project, key, value)
    if update_data.project_url is not None:
        update_data_fetch_dict = update_data_fetch.model_dump(exclude_unset=True)
        for key, value in update_data_fetch_dict.items():
            setattr(db_project, key, value)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project

# update img 
def update_img_file(
    db: Session, db_project: Project,
    new_secure_url: str, new_public_id: str
):
    """
    ## Nhận đầu vào: db, db_project (đối tượng được trỏ trong db), secure_url, public_id
        + gán lần lượt các giá trị 
        + return (ko làm gì cả hoặc trả về db_project)
    """
    db_project.img_url = new_secure_url
    db_project.img_public_id = new_public_id

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project

# sync (update)
def sync(
    db: Session,
    sync_data: schemas_project.UpdateFetchRepo,
    db_project: Project
):
    """
    - func update thông tin mới được fetch từ github repo nếu có thay đổi trên đó
    - Nhận vào các thông tin cần fetch trong github service (core.github_service.py), đối tượng object cần update
    """
    sync_data_dict = sync_data.model_dump(exclude_unset=True)
    for key,value in sync_data_dict.items():
        setattr(db_project, key, value)

    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    return db_project

# delete
def delete(
    db: Session, db_project: Project
):
    """
    Func xóa project theo db_project
    - Nhận db_project từ bên logic (logic gọi hàm xóa)
    - xóa xong return (logic làm việc tiếp: xóa ảnh, folder trên cloudinary)
    """
    db.delete(db_project)
    db.commit()
    return
  