import enum
from sqlalchemy import Integer, Column, String, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
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