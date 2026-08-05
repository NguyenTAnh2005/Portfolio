from sqlalchemy.orm import Session
from app.models.models import Achievement 
from datetime import datetime, timezone, timedelta

vie_tz = timezone(timedelta(hours=7))

list_achieves = [
    {
        "title": "Academic Excellence Award 2024–2025",
        "desc": "Recognized for outstanding academic performance and learning attitude during the 2024-2025 academic year.",
        "achieved_at": datetime(month=11, day=16, year=2025, tzinfo=vie_tz),
        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785836962/Portfolio/Achievements/2024-2025-academic-year_amqh4e.jpg",
        "img_public_id": "/Portfolio/Achievements/2024-2025-academic-year_amqh4e"
    },
    {
        "title": "Five Good Student Award (University Level) 2024–2025",
        "desc": "Awarded for excellence in academics, ethics, physical fitness, volunteering, and community engagement — recognizing well-rounded achievement beyond the classroom.",
        "achieved_at": datetime(month=3, day=24, year=2026, tzinfo=vie_tz),
        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785836962/Portfolio/Achievements/five-good-student_fzz1gx.jpg",
        "img_public_id": "/Portfolio/Achievements/five-good-student_fzz1gx"
    },
    {
        "title": "Runner-up, IT Faculty Chess Tournament",
        "desc": "Competed in the chess event at the IT Faculty Sports Festival and advanced to the final. Lost a close match 1.5–2.5, including a 5-minute blitz tiebreaker where, despite holding the advantage, I ran out of time. Finished as runner-up.",
        "achieved_at": datetime(month=6, day=19, year=2026, tzinfo=vie_tz),
        "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785836962/Portfolio/Achievements/it-faculty-chess-tournament_cj1dpg.jpg",
        "img_public_id": "/Portfolio/Achievements/it-faculty-chess-tournament_cj1dpg"
    }
]

def seed_achieve(db: Session):
    for ach in list_achieves:
        db_ach = Achievement(
            title = ach["title"], 
            desc = ach["desc"], 
            achieved_at = ach["achieved_at"], 
            img_url = ach["img_url"], 
            img_public_id = ach["img_public_id"], 
        )
        db.add(db_ach)
    print(f"⚠️  Added achievements seed data ....... waiting commit .............")

# list_achieves_vi = [
#     {
#         "title": "Danh hiệu Học sinh Giỏi năm học 2024-2025",
#         "desc": "Được đánh giá đạt loại giỏi về kết quả học tập và thái độ học tập trong năm học 2024-2025.",
#     },
#     {
#         "title": "Sinh viên 5 tốt cấp Trường năm học 2024-2025",
#         "desc": "Đạt danh hiệu Sinh viên 5 tốt cấp trường, ghi nhận thành tích toàn diện về học tập, đạo đức, thể lực, tình nguyện và hội nhập.",
#     },
#     {
#         "title": "Á quân Cờ vua - Đại hội Thể thao Khoa CNTT",
#         "desc": "Tham gia nội dung cờ vua tại Đại hội Thể thao Khoa CNTT và lọt vào chung kết. Thua tiếc nuối với tỷ số 1.5-2.5, trong đó ván cờ chớp 5 phút dù đang chiếm ưu thế nhưng tôi để hết thời gian và thua chung cuộc. Giành giải Nhì.",
#     }
# ]