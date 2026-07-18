from app.models.models import Info
from sqlalchemy.orm import Session

def seed_info(db: Session):
    intro = """I am an Information Technology student at Binh Duong University, Vietnam. I aspire to become a Software Engineer in the future. Although I am still building my knowledge and skills, I am always eager to learn new technologies and continuously improve myself to achieve my career goals."""

    db.add(Info(
        fullname="Nguyen Tuan Anh",
        hometown="Ha Tinh, Vietnam",

        gender=True, # Male
        major="Software Engineering",
        language=["Python", "C#", "C++", "JavaScript"],
        framework=["Bootstrap", "React", "Tailwind", ".NET", "FastAPI"],
        intro=intro,
        contact=[
            # {"name": "youtube", "url": "http://www.youtube.com/@ntta-05"},
            # {"name": "zalo", "url": "https://zalo.me/0328884320"},
            {"name": "phone", "url": "+84 328884320"},
            {"name": "github", "url": "https://github.com/NguyenTAnh2005"},
            {"name": "email1", "url": "23050118@student.bdu.edu.vn"},
            {"name": "email2", "url": "anhnguyentaun@gmail.com"},
            {"name": "facebook", "url": "https://www.facebook.com/share/14QaznFt8ZF"},
            {"name": "instagram", "url": "https://www.instagram.com/tanh_2005_"}
        ],
        bio="I may have limited experience, but I am always willing to learn.",
    ))

    print("✅ Dữ liệu hàm seed_info đã sẵn sàng!")

