## Phân bổ cấu trúc các file seed data (cre: Claude)

**Nguyên tắc:** file logic của từng model chỉ nên làm đúng 1 việc — nhận vào 1 `db: Session` có sẵn, rồi thêm data. Không tự mở session, không tự try/except, không tự commit.

```
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

## Runner dùng chung khi đang test riêng từng model

Vì bạn đang trong giai đoạn "mỗi chặng test 1 file riêng", thay vì mỗi file tự viết lại try/except/session, làm 1 script runner nhỏ dùng chung tạm thời:

```python
# run_seed.py  (script tạm để test 1 seed function trong lúc dev)
from app.db_connection import SessionLocal

def run(seed_func):
    db = SessionLocal()
    try:
        seed_func(db)
        db.commit()
        print(f"✅ {seed_func.__name__} chạy thành công!")
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    from app.seed.seed_info import seed_info  # đổi tên khi muốn test model khác
    run(seed_info)
```

Vậy là chỉ có **1 chỗ** viết logic try/except/session, dùng lại được cho bất kỳ model nào.

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

## Về phần "reset database"

Khi cần reset mà không đổi cấu trúc bảng, hướng đi thường dùng là `TRUNCATE ... RESTART IDENTITY CASCADE` cho từng bảng (hoặc tất cả), rồi chạy lại `seed_data.py`.
