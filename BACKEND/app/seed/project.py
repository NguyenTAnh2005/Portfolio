from sqlalchemy.orm import Session
from app.core import github_service
from app.models.models import Project

list_projects = [
    # qly sieu thi
    {
        "title" : "Managing Buying and Selling in a Supermarket using OOP",
        "project_url" : "https://github.com/NguyenTAnh2005/Manage_supermarket_OOP",
        "list_tech" : [],

        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785545465/Portfolio/Projects/1/manage_supermarket_oop_xewwlz.jpg",
        "img_public_id": "Portfolio/Projects/1/manage_supermarket_oop_xewwlz"
    },
    # cv
    {
        "title" : "The first Curriculum Vitae (CV)", 
        "project_url" : "https://github.com/NguyenTAnh2005/My_First_CV",
        "list_tech" : [],

        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785545481/Portfolio/Projects/2/my-cv_h234vk.jpg",
        "img_public_id": "Portfolio/Projects/2/my-cv_h234vk"
    },
    # nghe nhac truc tuyen
    {
        "title" : "Online website Music - STAP Music",
        "project_url" : "https://github.com/NguyenTAnh2005/STAP_Music",
        "list_tech" : [],

        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785297023/Portfolio/Projects/3/stap-music_if1ij6.jpg",
        "img_public_id": "Portfolio/Projects/3/stap-music_if1ij6"
    },
    # nau an
    {
        "title" : "Cooking Guide - Let's Cook",
        "project_url" : "https://github.com/NguyenTAnh2005/Let-Cook",
        "list_tech" : [],

        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785545511/Portfolio/Projects/4/let-cook_u7jtds.jpg",
        "img_public_id": "Projects/4/let-cook_u7jtds"
    },
    # dien thoai cu
    {
        "title" : "Buying and Selling Old Phone",
        "project_url" : "https://github.com/NguyenTAnh2005/asp_sellphone",
        "list_tech" : ["SQL Server"],

        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785545525/Portfolio/Projects/5/asp-sellphone_c0dgi8.jpg",
        "img_public_id": "Projects/5/asp-sellphone_c0dgi8"
    },
    # theo doi thoi quen
    {
        "title" : " Habit Tracker Website",
        "project_url" : "https://github.com/NguyenTAnh2005/Habit_Tracker",
        "list_tech" : ["React", "Tailwind", "FastAPI"],

        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785545543/Portfolio/Projects/6/habit-tracker_yxo5ul.jpg",
        "img_public_id": "Portfolio/Projects/6/habit-tracker_yxo5ul"
    },
]

async def seed_project(db: Session):
    """
    Func chạy seed data cho project model. 
    Mỗi objet sẽ có: title, project_url, list_tech, img_url, img_public_id.
    Các thuộc tính còn lại thì async get bằng hàm get_repo_info ( thiết kế trả lỗi rồi nên gọi bt là đc.).
    1. Tạo 1 danh sách chứa các đối tượng cần thêm
    2. Dùng vòng lặp duyệt qua từng đối tượng: 
        +) get_repo_url thông qua project_url
        +) Gán đầy đủ thông tin sang models
        +) db.add
    3. print state: Chuẩn bị thông tin seed_data thành công.
    """

    for p in list_projects:
        # responmodels.data
        info_response = await github_service.get_repo_info(p["project_url"])
        repo_info = info_response.data
        added_project = Project(
            title = p["title"], list_tech = p["list_tech"], project_url = p["project_url"],
            img_url = p["img_url"], img_public_id = p["img_public_id"],
            desc = repo_info["desc"],
            list_lang = repo_info["list_lang"],
            created_at = repo_info["created_at"],
            last_updated = repo_info["last_updated"]
        )
        db.add(added_project)
    print(f"⚠️  Added projects seed data ....... waiting commit .............")



