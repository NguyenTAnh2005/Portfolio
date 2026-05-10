from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    FRONTEND_URL: str
    DATABASE_URL: str
    # Mã key để thực thi JWT
    SECRET_KEY: str
    # Thời hạn tồn tại tối đa của một lần cấp JWT (3 ngày)
    ACCESS_TOKEN_EXPRIE_MINUTES: int = 4320
    # Tài khoản Admin seed data
    ST_ADMIN_EMAIL:str
    ST_ADMIN_PASSWORD: str
    #...

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        case_sensitive = True

settings = Settings()