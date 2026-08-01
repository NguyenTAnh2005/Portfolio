from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_URL: str
    DATABASE_URL: str
    #...
    BASE_API_URL:str
    # Mã key để thực thi JWT
    SECRET_KEY: str
    # Thời hạn tồn tại tối đa của một lần cấp JWT (3 ngày)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 4320
    # Tài khoản Admin seed data
    ST_ADMIN_EMAIL:str
    ST_ADMIN_PASSWORD: str


    # Cloudinary Service
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # GITHUB Fetch reposity 
    GITHUB_API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = True

settings = Settings()