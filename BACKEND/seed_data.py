from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import User, RoleType
from app.core.security import get_password_hash
from app.db_connection import SessionLocal


# Theo kế hoạch thì DB sẽ có 1 biến là seed_data --> true hoặc false để kiểm tra có thêm 
# hay chưa nhưng hiện tại thì chưa làm ngay. Sẽ làm lại phần seed data khi đã có đấy đủ thông tin cần thêm hơn. 

def seed_data_user(db: Session):
    """ Tạo tài khoản Amdin đầu tiên!"""
    email = settings.ST_ADMIN_EMAIL
    password = settings.ST_ADMIN_PASSWORD
    if not email or not password:
        print("⚠️ Lỗi! Không tìm thấy mật khẩu hoặc email trong pydantic settings. Vui lòng kiếm tra lại file .env!")
        return
    hashed_password = get_password_hash(password=password)
    new_admin = User(
        email = email,
        username = "Anh Admin",
        password = hashed_password,
        role = RoleType.ADMIN
    )
    db.add(new_admin)
    db.commit()
    print("✅ Khởi tạo tài khoản Admin thành công!")


def seed_data():
    """ Hàm tổng chạy nhiều func seed data cho từng bảng khác nhau!"""
    db= SessionLocal()
    try:
        seed_data_user(db=db)
    except Exception as e:
        print(f"❌ Lỗi khi seed data: {e}")
        db.rollback()
    finally:
        db.close()
        print("🏁 Hoàn tất!")

if __name__=="__main__":
    seed_data()

