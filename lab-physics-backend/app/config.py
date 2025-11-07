import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "lab-physics-backend")

    # WeChat
    WECHAT_APPID: Optional[str] = os.getenv("WECHAT_APPID")
    WECHAT_APP_SECRET: Optional[str] = os.getenv("WECHAT_APP_SECRET")
    WECHAT_MOCK: Optional[str] = os.getenv("WECHAT_MOCK")  # '1' 表示启用模拟

    # Database
    MYSQL_URL: Optional[str] = os.getenv("MYSQL_URL")
    SQLITE_URL: str = os.getenv("SQLITE_URL", "sqlite:///./data/dev.sqlite")

    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "43200"))  # 30天

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")


settings = Settings()