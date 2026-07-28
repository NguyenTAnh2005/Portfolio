import enum
from sqlalchemy import Integer, Column, String, Boolean, ARRAY, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db_connection import Base

# ================================
#  1. Enum Role 
# ================================
class RoleType(str, enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"

# ================================
# 2. Bảng User
# ================================
class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key = True, index = True)
    username = Column(String, unique = True, nullable = False)
    password = Column(String, nullable = False)
    email = Column(String, unique = True, nullable = False)

    # Map enum role type vào user model, mặc định là CLIENT
    role = Column(SQLEnum(RoleType), default=RoleType.CLIENT, nullable=False)


# ================================
# 3. Bảng Info
# ================================
class Info(Base):
    __tablename__="info"
    # id fullname hometown gender major languages framework intro bio contact
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hometown: Mapped[str] = mapped_column(String(50))
    # true for male, false for female.
    # CÁc dự án sau nên dùng enum định nghĩa giới tính riêng hẳn hoi nhé!
    gender: Mapped[bool] = mapped_column(Boolean, default=True)
    major: Mapped[str] = mapped_column(String(30))
    language: Mapped[list] = mapped_column(ARRAY(String(50)))
    framework: Mapped[list] = mapped_column(ARRAY(String(50)))
    intro: Mapped[str] = mapped_column(Text)
    # [ { "type": "facebook", "url": "https://facebook.com/...", "visible": true}, {..}]
    contact: Mapped[dict] = mapped_column(JSONB, default=list)
    bio: Mapped[str] = mapped_column(String(500))

# ================================
# 4. Bảng TimeLine
# ================================
class TimeLine(Base):
    __tablename__="timeline"
    #id, title, organization, desc, start_end, sort_order, img_url, img_public_id

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    organization: Mapped[str] = mapped_column(String(100), nullable=False)
    desc: Mapped[str] = mapped_column(Text, nullable = False)
    # Time start - end : Dùng chuỗi để gán cứng, ko phải xử lý chuỗi thời gian -> String. 
    start_end: Mapped[str] = mapped_column(String(50), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    # Thông số cần thiết để lưu ảnh trực tiếp lên Cloudinary 
    # Các chuỗi link của ảnh cloudinary thường hay rất dài. 
    img_url: Mapped[str] = mapped_column(String(1024), nullable=True, unique=True)
    img_public_id: Mapped[str] = mapped_column(String(255), nullable=True, unique=True)



