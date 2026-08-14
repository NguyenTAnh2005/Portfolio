"""seed data

Revision ID: d5a1c4c307c1
Revises: 0e761ad3da53
Create Date: 2026-08-14 15:11:06.141837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime, timezone, timedelta

from app.core.config import settings
from app.core.security import get_password_hash



# revision identifiers, used by Alembic.
revision: str = 'd5a1c4c307c1'
down_revision: Union[str, Sequence[str], None] = '0e761ad3da53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _seed_user():
    user_table = sa.table(
        'users',
        sa.column('username', sa.String),
        sa.column('password', sa.String),
        sa.column('email', sa.String),
        sa.column('role', sa.Enum('ADMIN', 'CLIENT', name='roletype', create_type=False)),
    )
    op.bulk_insert(user_table,[
        {
            "username":"Admin Nguyen", 
            "password":get_password_hash(settings.ST_ADMIN_PASSWORD),
            "email": settings.ST_ADMIN_EMAIL,
            "role": "ADMIN"
        }
    ])

def _seed_info():
    info_table = sa.table(
        'info',
        sa.column('fullname', sa.String),
        sa.column('hometown', sa.String),
        sa.column('gender', sa.Boolean),
        sa.column('major', sa.String),
        sa.column('language', sa.ARRAY(sa.String)),
        sa.column('framework', sa.ARRAY(sa.String)),
        sa.column('intro', sa.Text),
        sa.column('contact', postgresql.JSONB(astext_type=sa.Text())),
        sa.column('bio', sa.String),
    )
    intro = """I am an Information Technology student at Binh Duong University, Vietnam. I aspire to become a Software Engineer in the future. Although I am still building my knowledge and skills, I am always eager to learn new technologies and continuously improve myself to achieve my career goals."""

    op.bulk_insert(info_table,[
        {
            "fullname":"Nguyen Tuan Anh",
            "hometown":"Ha Tinh, Vietnam",

            "gender":True, # Male
            "major":"Software Engineering",
            "language":["Python", "C#", "C++", "JavaScript"],
            "framework":["Bootstrap", "React", "Tailwind", ".NET", "FastAPI"],
            "intro":intro,
            "contact":[
                {"name": "phone", "url": "0328884320"},
                {"name": "github", "url": "https://github.com/NguyenTAnh2005"},
                {"name": "email1", "url": "23050118@student.bdu.edu.vn"},
                {"name": "email2", "url": "anhnguyentaun@gmail.com"},
                {"name": "facebook", "url": "https://www.facebook.com/share/14QaznFt8ZF"},
                {"name": "instagram", "url": "https://www.instagram.com/tanh_2005_"}
            ],
            "bio":"I may have limited experience, but I am always willing to learn.",
        }
    ])

def _seed_timeline():
    timeline_table = sa.table(
        'timeline',
        sa.column('title', sa.String),
        sa.column('organization', sa.String),
        sa.column('desc', sa.Text),
        sa.column('start_end', sa.String),
        sa.column('sort_order', sa.Integer),
        sa.column('img_url', sa.String),
        sa.column('img_public_id', sa.String),
    )
    list_timneline = [
        {
            "title": "Primary school student",
            "organization": "Cam Quang Primary School",
            "desc": "I studied here from age 6. I started 1st grade later than my classmate. I didn't learn English until 4th grade. I got the 'good student' award all 5 years!",
            "start_end": "2011 - 2016",
            "sort_order": 1,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805458/Portfolio/TimeLines/cam-quang-primary-school_y081lv.jpg",
            "img_public_id": "Portfolio/TimeLines/cam-quang-primary-school_y081lv",
        },
        {
            "title": "Secondary school student",
            "organization": "Nguyen Huu Thai Secondary School",
            "desc": "I studied here from age 11. Not much happened during this time. My English got worse starting in 8th grade. In 9th grade I learned a bit of Pascal, but I didn't take it seriously, and I still knew nothing about computers.",
            "start_end": "2016 - 2020",
            "sort_order": 2,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805459/Portfolio/TimeLines/nguyen-huu-thai-secondary-school_hqdw4f.jpg",
            "img_public_id": "Portfolio/TimeLines/nguyen-huu-thai-secondary-school_hqdw4f",
        },
        {
            "title": "High school student",
            "organization": "Cam Binh High School",
            "desc": "I studied here from age 15. I spent most of my time studying, but my grades were just average. In 11th grade I learned Pascal, but only with pen and paper — I didn't have a laptop to practice on. I got a total score of 24.3 on the National High School Graduation Exam to apply for an IT major.",
            "start_end": "2020 - 2023",
            "sort_order": 3,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805458/Portfolio/TimeLines/cam-binh-high-school_zpq2cx.jpg",
            "img_public_id": "Portfolio/TimeLines/cam-binh-high-school_zpq2cx",
        },
        {
            "title": "The first Part-time job",
            "organization": "GS25",
            "desc": "I had a part-time job at GS25, a convenience store chain from South Korea. I learned a lot there, and it made me value money more. But I only worked there for 6 months during my second year of university, because I had a lot of school projects around that time. The projects weren't hard, but since I had just started learning, I still struggled and couldn't manage the minimum hours per week that the job required.",
            "start_end": "12/2024 - 06/2025",
            "sort_order": 4,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805458/Portfolio/TimeLines/gs25_syxdoy.jpg",
            "img_public_id": "Portfolio/TimeLines/gs25_syxdoy",
        },
        {
            "title": "University student",
            "organization": "Binh Duong University",
            "desc": "I've studied here since age 18, in the IT program. Studying here was very different from before. In 1/2025 I learned HTML and CSS. In 4/2025 I learned basic JS. In 8/2025 I started using Bootstrap CSS. In 9/2025 I started learning React through React.dev, plus TailwindCSS. Right now I'm focusing on Software Engineering.",
            "start_end": "9/2023 - Now",
            "sort_order": 5,
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785805459/Portfolio/TimeLines/binh-duong-university_vmt2fm.jpg",
            "img_public_id": "Portfolio/TimeLines/binh-duong-university_vmt2fm",
        }
    ]
    op.bulk_insert(timeline_table,list_timneline)

def _seed_project():
    project_table = sa.table(
        'project',
        sa.column('title', sa.String),
        sa.column('desc', sa.Text),
        sa.column('project_url', sa.String),
        sa.column('list_tech', sa.ARRAY(sa.String)),
        sa.column('list_lang', sa.ARRAY(sa.String)),
        sa.column('created_at', sa.DateTime),
        sa.column('last_updated', sa.DateTime),
        sa.column('img_url', sa.String),
        sa.column('img_public_id', sa.String),
    )
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
            "img_public_id": "Portfolio/Projects/4/let-cook_u7jtds"
        },
        # dien thoai cu
        {
            "title" : "Buying and Selling Old Phone",
            "project_url" : "https://github.com/NguyenTAnh2005/asp_sellphone",
            "list_tech" : ["SQL Server"],

            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785545525/Portfolio/Projects/5/asp-sellphone_c0dgi8.jpg",
            "img_public_id": "Portfolio/Projects/5/asp-sellphone_c0dgi8"
        },
        # theo doi thoi quen
        {
            "title" : "Habit Tracker Website",
            "project_url" : "https://github.com/NguyenTAnh2005/Habit_Tracker",
            "list_tech" : ["React", "Tailwind", "FastAPI"],

            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785545543/Portfolio/Projects/6/habit-tracker_yxo5ul.jpg",
            "img_public_id": "Portfolio/Projects/6/habit-tracker_yxo5ul"
        },
    ]
    op.bulk_insert(project_table,list_projects)

def _seed_achievement():
    achievement_table = sa.table(
        'achievement',
        sa.column('title', sa.String),
        sa.column('desc', sa.Text),
        sa.column('achieved_at', sa.DateTime),
        sa.column('img_url', sa.String),
        sa.column('img_public_id', sa.String),
    )
    vie_tz = timezone(timedelta(hours=7))
    list_achieves = [
        {
            "title": "Academic Excellence Award 2024–2025",
            "desc": "Recognized for outstanding academic performance and learning attitude during the 2024-2025 academic year.",
            "achieved_at": datetime(month=11, day=16, year=2025, tzinfo=vie_tz),
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785836962/Portfolio/Achievements/2024-2025-academic-year_amqh4e.jpg",
            "img_public_id": "Portfolio/Achievements/2024-2025-academic-year_amqh4e"
        },
        {
            "title": "Five Good Student Award (University Level) 2024–2025",
            "desc": "Awarded for excellence in academics, ethics, physical fitness, volunteering, and community engagement — recognizing well-rounded achievement beyond the classroom.",
            "achieved_at": datetime(month=3, day=24, year=2026, tzinfo=vie_tz),
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785836962/Portfolio/Achievements/five-good-student_fzz1gx.jpg",
            "img_public_id": "Portfolio/Achievements/five-good-student_fzz1gx"
        },
        {
            "title": "Runner-up, IT Faculty Chess Tournament",
            "desc": "Competed in the chess event at the IT Faculty Sports Festival and advanced to the final. Lost a close match 1.5–2.5, including a 5-minute blitz tiebreaker where, despite holding the advantage, I ran out of time. Finished as runner-up.",
            "achieved_at": datetime(month=6, day=19, year=2026, tzinfo=vie_tz),
            "img_url": "https://res.cloudinary.com/df5mtvzkn/image/upload/v1785836962/Portfolio/Achievements/it-faculty-chess-tournament_cj1dpg.jpg",
            "img_public_id": "Portfolio/Achievements/it-faculty-chess-tournament_cj1dpg"
        }
    ]

    op.bulk_insert(achievement_table, list_achieves)

def _seed_config():
    config_table = sa.table(
        'system_config',
        sa.column('name', sa.String),
        sa.column('value', postgresql.JSONB(astext_type=sa.Text())),
    )
    list_configs = [
        { "name": "resume_url","value": "have-not-done-yet"}
        ,
        { "name": "available_for_work", "value": True}
        ,
        { "name": "web_maintenance_mode","value": False}
    ]
    op.bulk_insert(config_table, list_configs)


def upgrade() -> None:
    """Thêm các dữ liệu các bảng theo LÔ"""
    _seed_user()
    _seed_info()
    _seed_timeline()
    _seed_project()
    _seed_achievement()
    _seed_config()


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM USERS;")
    op.execute("DELETE FROM INFO;")
    op.execute("DELETE FROM TIMELINE;")
    op.execute("DELETE FROM PROJECT;")
    op.execute("DELETE FROM ACHIEVEMENT;")
    op.execute("DELETE FROM SYSTEM_CONFIG;")
