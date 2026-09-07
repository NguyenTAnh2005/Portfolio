# `🎯 Note về cấu trúc các file seed data`

**Nguyên tắc:** file logic của từng model chỉ nên làm đúng 1 việc — nhận vào 1 `db: Session` có sẵn, rồi thêm data. Không tự mở session, không tự try/except, không tự commit.

```bash
BACKEND/
├── app/
│   └── seed/
│       ├── __init__.py
│       ├── seed_user.py        # def seed_user(db): ...
│       ├── seed_info.py        # def seed_info(db): ...
│       ├── seed_timeline.py
│       ├── seed_project.py
│       └── seed_achievement.py
└── seed_data.py                 # entrypoint tổng (giữ nguyên vị trí như hiện tại)
```

`app/seed/seed_user.py` sau khi tách — chỉ còn phần "thịt":

```python
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import User, RoleType
from app.core.security import get_password_hash

def seed_user(db: Session):
    email = settings.ST_ADMIN_EMAIL
    password = settings.ST_ADMIN_PASSWORD
    if not email or not password:
        print("⚠️ Thiếu ST_ADMIN_EMAIL / ST_ADMIN_PASSWORD trong .env")
        return
    db.add(User(
        email=email,
        username="Anh Admin",
        password=get_password_hash(password),
        role=RoleType.ADMIN,
    ))
```

Chú ý: **không có `db.commit()` ở đây nữa** — commit sẽ do lớp runner quyết định (1 chỗ duy nhất, atomic cho toàn bộ).

## Khi gộp thành `seed_data.py` tổng (sau này)

```python
from app.db_connection import SessionLocal
from app.seed.seed_user import seed_user
from app.seed.seed_info import seed_info
# from app.seed.seed_timeline import seed_timeline ...

def seed_data():
    db = SessionLocal()
    try:
        seed_user(db)
        seed_info(db)
        # gọi tiếp các seed khác theo đúng thứ tự phụ thuộc (FK)
        db.commit()
        print("✅ Seed toàn bộ dữ liệu thành công!")
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi seed data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
```

Cấu trúc này về sau chỉ cần chạy `python seed_data.py` là seed hết, và nếu 1 bước lỗi giữa chừng thì rollback toàn bộ (atomic) — tránh tình trạng data nửa vời.
