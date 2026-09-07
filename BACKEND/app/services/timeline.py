from app.core.exception import AppException
from sqlalchemy.orm import Session
from fastapi import status, UploadFile
from typing import Optional
from fastapi import Form, File

from app.core import cloudinary_config as cloudinary 
from app.schemas import timeline as schemas_timeline
from app.crud import timeline as crud_timeline

from app.models.models import TimeLine

# Code cũ thì upload và tạo 1 folder con trong Timeline theo "title" 
# nhưng nó sẽ gây răc rối rất rất nhiều cho logic update. Nên bỏ
# Lưu ý: sau TimeLine nếu có "/" sẽ tạo 1 thư mục con None
BASE_FOLDER="Portfolio/TimeLines"

def check_conflict(
    db: Session, title: str, sort_order: int,  
    exclude_id: Optional[int] = None, # Id loại trừ, nếu cập nhật thì phải loại TH id mình đang update.
):
    """
    Func check trùng lặp dữ liệu. 
    - Duyệt qua từng lớp lọc và trả về lỗi tương ứng với từng field trùng, giúp Admin debug tốt hơn. 
    """
    db_query = db.query(TimeLine)
    if exclude_id: 
        db_query = db_query.filter(TimeLine.id!=exclude_id)
    check_dict = { 
        "title": title, "sort_order": sort_order, 
    }
    for key, value in check_dict.items():
        if value and value is not None:
            column = getattr(TimeLine, key)
            conflict = db_query.filter(column == value).first()
            if conflict:
                raise AppException(
                    status_code=status.HTTP_409_CONFLICT,
                    error_code="CONFLICT_DATA",
                    message= f"There is a Timeline object that has this {key} value in the database. Please check and try again."
                )

    
# Xử lý tạo timeline
def create_timeline(
    db: Session,
    title: str, organization: str,
    desc: str, start_end: str,
    sort_order: int,
    img_file: UploadFile
):
    """
    Hàm xử lý logic tạo Timeline:
    - Nhận vào db, các input field (text, file)
    - Check trùng lặp ?
    - 1. Tải ảnh ImageFile lên Cloud, lấy giá trị secure_url và public_id về.- Check lỗi trùng lặp 
    - 2. Parse các giá trị đầy đủ qua class Pydantic CreteTimeline
    - 3. Gọi hàm create bên Crud với các đầu vào 
    --> Bên kia chỉ cần trả về object Timeline khi đã tạo thành công hoặc Raise App Exception (nếu cần) cho Router.
    """
    # Note tại sao .file vui lòng đọc file trong DOCS pharse-3
    check_conflict(
        db = db, title=title, sort_order = sort_order, 
        exclude_id = None,
    )

    img_data = cloudinary.upload_image(
        file= img_file.file,
        folder_name=BASE_FOLDER
    )

    data_create = schemas_timeline.Create(
        title=title, organization=organization, desc=desc, 
        start_end=start_end, sort_order=sort_order
    )

    return crud_timeline.create(
        db=db, data_create=data_create,
        img_url=img_data["secure_url"],
        img_public_id=img_data["public_id"]
    )

    
# Xử lý cập nhật timeline 
    # - Với model bình thường như Info thì nó dạng là Dict key-value parse sang class Pydantic sẵn. 
    # Nên khi update bằng cách gửi Dict key-value thì có thể tùy chọn CHỈ CẬP NHẬT CÁI GÌ. 
    # (Các pydantic sẽ có dạng Optional là không bắt buộc phải có trường này trong cập nhật)
    # - Còn đối với như Timeline do nó vừa chứa ảnh và text thường nên 1 class Pydantic thì không thể đáp ứng, phải tách lẻ và gán thủ công.
    # Mỗi field là một input form dạng text hoặc File. TUY NHIÊN, khi test update thì mặc định không nhập gì - tưởng là None 
    # nhưng thực ra là str - "", kể cả gán trường là File hay int.
    # Do đó nó vẫn được tính là CÓ GỬI  như TH Dict key-value bên trên; tức là "key":"", vô tình thay thế dữ liệu. 
    # - Hàm này sẽ có nhiệm vụ là loại bỏ các trường gửi đến có giá trị None hoặc "", chỉ thêm các trường thay đổi vào trong Dict key-value tổng. 
    # Từ đó parse sang Pydantic class.
def update_timeline(
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
    - 0. Check có trong DB? Kiểm tra trùng lặp first. 
    (Cập nhật logic cũng to đấy, thế đã check trùng lặp chưa ?)
    - 1. Parse từ các giá trị ở các Field Text qua thành dict để ánh xạ qua Pydantic class UpdateTimeline
    - 2. Khai báo None các biến liên quan ảnh. Nếu có ảnh thì upload ảnh, lấy thông số. 
    - 3. Gọi hàm crud Update để update
    - 4. Xóa ảnh cũ và trả về đối tượng timeline đã cập nhật cho Router
    """
    # 0
    db_timeline = crud_timeline.get_by_id(db=db, timeline_id= target_id)
    check_conflict(db=db, title=title, sort_order=sort_order, exclude_id=target_id)
    # 1
    # Pydantic này chỉ chứa các thông tin text thuần,
    # không chứa liên quan ảnh (url, public id) - cloudinary lo
    update_data = schemas_timeline.Update()
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
        setattr(update_data, key, value)
    # 2
    new_secure_url = None
    new_public_id = None
    old_public_id = None
    if img_file:
        db_timeline = crud_timeline.get_by_id(db=db, timeline_id=target_id)
        old_public_id = db_timeline.img_public_id
        print(f"old: {old_public_id}")

        new_img = cloudinary.upload_image(
            folder_name=BASE_FOLDER,
            file=img_file.file
        )
        new_secure_url = new_img["secure_url"]
        new_public_id = new_img["public_id"]
    # 3
    updated_timeline = crud_timeline.update(
        db=db, db_timeline=db_timeline,
        update_data=update_data,
        img_url=new_secure_url,
        img_public_id=new_public_id
    )
    # 4
    if img_file and old_public_id:
        cloudinary.destroy_image(old_public_id)
    
    return updated_timeline


# Xử lý xóa timeline 
def delete_timeline(
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
    db_timeline = crud_timeline.get_by_id(db=db, timeline_id=target_id)
    deleted_img_public_id = db_timeline.img_public_id

    crud_timeline.delete(db=db, db_timeline=db_timeline)

    cloudinary.destroy_image(deleted_img_public_id)

    return 

