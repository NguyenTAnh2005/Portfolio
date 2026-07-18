from app.db_connection import SessionLocal

from app.seed.user import seed_user
from app.seed.info import seed_info

def seed_data():
    db = SessionLocal()
    try:
        seed_user(db=db)
        seed_info(db=db)

        db.commit()
        print("✅ Seed toàn bộ dữ liệu thành công!")
    except Exception as e:
        db.rollback()
        print(f"❌ Lỗi khi seed data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()