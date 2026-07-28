from app.core.exception import AppException
from fastapi import status
from typing import Optional
from fastapi import Form, File
from app.schemas.timeline import TimelineUpdate 

# Logic
from app.core.cloudinary_config import upload_image, destroy_image
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.schemas.timeline import TimelineCreate, TimelineUpdate
from app.crud.timeline import create_timeline, update_timeline, get_timeline_by_id, delete_timeline
from app.schemas.response import ResponseModel

from app.models.models import TimeLine

# Code cũ thì upload và tạo 1 folder con trong Timeline theo "title" 
# nhưng nó sẽ gây răc rối rất rất nhiều cho logic update. Nên bỏ
# Lưu ý: sau TimeLine nếu có "/" sẽ tạo 1 thư mục con None
BASE_FOLDER="Portfolio/TimeLine"

# Xử lý phần None hoặc "" từ các field -> dict --> Pydantic class
def parse_field_text_to_pydantic_class(
    title: Optional[str] = Form(None), 
    organization: Optional[str] = Form(None),
    desc: Optional[str] = Form(None), 
    start_end: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
):
    """
    Func này: 
    - Với model bình thường như Info thì nó dạng là Dict key-value parse sang class Pydantic sẵn. 
    Nên khi update bằng cách gửi Dict key-value thì có thể tùy chọn CHỈ CẬP NHẬT CÁI GÌ. 
    (Các pydantic sẽ có dạng Optional là không bắt buộc phải có trường này trong cập nhật)
    - Còn đối với như Timeline do nó vừa chứa ảnh và text thường nên 1 class Pydantic thì không thể đáp ứng, phải tách lẻ và gán thủ công.
    Mỗi field là một input form dạng text hoặc File. TUY NHIÊN, khi test update thì mặc định không nhập gì - tưởng là None 
    nhưng thực ra là str - "", kể cả gán trường là File hay int.
    Do đó nó vẫn được tính là CÓ GỬI  như TH Dict key-value bên trên; tức là "key":"", vô tình thay thế dữ liệu. 
    - Hàm này sẽ có nhiệm vụ là loại bỏ các trường gửi đến có giá trị None hoặc "", chỉ thêm các trường thay đổi vào trong Dict key-value tổng. 
    Từ đó parse sang Pydantic class.
    """
    
    pydantic_class = TimelineUpdate()
    dict_attr = {
        "title": title,
        "organization": organization,
        "desc":desc,
        "start_end": start_end,
        "sort_order": sort_order
    }
    for key, value in dict_attr.items():
        if value is None:
            continue
        if isinstance(value, str) and value == "":
            continue
        setattr(pydantic_class, key, value)

    return pydantic_class

# Hàm check lỗi trùng sort_order  --> Lỗi chnung chung, khó debug 

# def check_conflict(db: Session, current_id:int, sort_order:int, title:str ):
#     """
#     Func kiểm tra trùng lặp dữ liệu khi tạo mới đối tượng timeline hoặc cập nhật!
#     - Tạo 1 list chứa các điều kiện lặp: model.id == id,....
#     - Nếu như list trống thì return 
#     - Nếu ko có current_id tức là tạo mới thì chỉ cần lấy first và != None thì => trùng.
#     - Nếu như cập nhật thì filter thêm - loại bỏ đối tượng có current_id. Sau đó lấy first, nếu != None tức là đã có sẵn trong DB. Không thể cập nhật thêm!
#     """
#     condition_conflict = []
#     if sort_order and sort_order is not None:
#         condition_conflict.append(TimeLine.sort_order == sort_order)
#     if title and title is not None:
#         condition_conflict.append(TimeLine.title == title)
#     if not condition_conflict:
#         return
#     if not current_id:
#         db_conflict = db.query(TimeLine).filter(*condition_conflict).first()
#         if db_conflict:
#             raise AppException( )
#         return

#     # thêm đi=k lọc bỏ id hiện tại
#     condition_conflict.append(TimeLine.id!= current_id)
#     db_conflict = db.query(TimeLine).filter(*condition_conflict).first()
#     if db_conflict:
#         raise AppException( )
#     return

def check_conflict(
    db: Session, 
    title: str,
    sort_order: int, # Id loại trừ, nếu cập nhật thì phải loại TH id mình đang update. 
    exclude_id: Optional[int] = None
):
    """
    Func check trùng lặp dữ liệu. 
    - Duyệt qua từng lớp lọc và trả về lỗi tương ứng với từng field trùng, giúp Admin debug tốt hơn. 
    """
    db_query = db.query(TimeLine)
    if exclude_id: db_query.filter(TimeLine.id!=exclude_id)
    if title and title is not None:
        conflict = db_query.filter(TimeLine.title == title).first()
        if conflict:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                error_code="CONFLICT_DATA",
                message="There is a timeline object that has this title value in the database. Please check and try again."
            )
    if sort_order and sort_order is not None:
        conflict = db_query.filter(TimeLine.sort_order == sort_order).first()
        if conflict:
            raise AppException(
                status_code=status.HTTP_409_CONFLICT,
                error_code="CONFLICT_DATA",
                message="There is a timeline object that has this sort_order value in the database. Please check and try again."
            )

# Xử lý tạo timeline
def logic_create_timeline(
    db: Session,
    title: str, organization: str,
    desc: str, start_end: str,
    sort_order: int,
    img_file: UploadFile
):
    """
    Hàm xử lý logic tạo Timeline:
    - Check lỗi trùng lặp sort_order
    - Nhận vào db, các input field (text, file)
    - 1. Tải ảnh ImageFile lên Cloud, lấy giá trị secure_url và public_id về.
    - 2. Parse các giá trị đầy đủ qua class Pydantic CreteTimeline
    - 3. Gọi hàm create bên Crud với các đầu vào 
    --> Bên kia chỉ cần trả về object Timeline khi đã tạo thành công hoặc Raise App Exception (nếu cần) cho Router.
    """
    # Note tại sao .file vui lòng đọc file trong DOCS pharse-3
    check_conflict(db = db, title=title, sort_order = sort_order, exclude_id = None)

    img_data = upload_image(
        file= img_file.file,
        folder_name=BASE_FOLDER
    )

    data_create = TimelineCreate(
        title=title, organization=organization, desc=desc, 
        start_end=start_end, sort_order=sort_order
    )

    return create_timeline(
        db=db, data_create=data_create,
        img_url=img_data["secure_url"],
        img_public_id=img_data["public_id"]
    )
    
# Xử lý cập nhật timeline 
def logic_update_timeline(
    db:Session, target_id: int,
    title: Optional[str] = Form(None), 
    organization: Optional[str] = Form(None),
    desc: Optional[str] = Form(None), 
    start_end: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    img_file: Optional[UploadFile] = File(None)
):
    """
    Hàm xử lý logic cập nhật timeline
    - Nhận vào: db, target_id, các field form (text, file)
    - Kiểm tra trùng lặp first. Cập nhật logic cũng to đấy, thế đã check trùng lặp chưa ?
    - 1. Parse từ các giá trị ở các Field Text qua thành dict để ánh xạ qua Pydantic class UpdateTimeline
    - 2. Khai báo None các biến liên quan ảnh. Nếu có ảnh thì upload ảnh, lấy thông số. 
    - 3. Gọi hàm crud Update để update
    - 4. Xóa ảnh cũ và trả về đối tượng timeline đã cập nhật cho Router
    """
    check_conflict(db=db, title=title, sort_order=sort_order, exclude_id=target_id)

    # Pydantic này chỉ chứa các thông tin text thuần,
    # không chứa liên quan ảnh (url, public id) - cloudinary lo
    # Đọc func trên để hiểu rõ hơn
    update_data = parse_field_text_to_pydantic_class(
        title=title, organization=organization, 
        desc=desc, start_end=start_end, 
        sort_order= sort_order
    )

    new_secure_url = None
    new_public_id = None
    old_public_id = None
    if img_file:
        db_timeline = get_timeline_by_id(db=db, timeline_id=target_id)
        old_public_id = db_timeline.img_public_id
        print(f"old: {old_public_id}")

        new_img = upload_image(
            folder_name=BASE_FOLDER,
            file=img_file.file
        )
        new_secure_url = new_img["secure_url"]
        new_public_id = new_img["public_id"]

    updated_timeline = update_timeline(
        db=db, target_id=target_id,
        update_data=update_data,
        img_url=new_secure_url,
        img_public_id=new_public_id
    )

    if img_file and old_public_id:
        destroy_image(old_public_id)
    
    return updated_timeline

# Xử lý xóa timeline 
def logic_delete_timeline(
    db: Session,
    target_id: int
):
    """
    Func nhận vào là id timeline cần xóa 
    - Tìm Timeline 
    - gọi hàm delete bên crud (return)
    - Xóa ảnh dựa theo id_public
    - Trả về Message thông báo
    """
    db_timeline = get_timeline_by_id(db=db, timeline_id=target_id)
    img_public_id = db_timeline.img_public_id

    delete_timeline(db=db, target_id=target_id, db_timeline=db_timeline)

    destroy_image(img_public_id)

    return ResponseModel(
        message=f"Đã xóa thành công TimeLine có id: {target_id}",
        data=None
    )
