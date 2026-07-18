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