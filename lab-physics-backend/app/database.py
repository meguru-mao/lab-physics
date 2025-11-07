import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings


def _get_database_url() -> str:
    # 优先 MySQL，其次 SQLite 回退，保证开发环境可启动
    if settings.MYSQL_URL:
        return settings.MYSQL_URL
    # 自动创建本地目录
    os.makedirs("data", exist_ok=True)
    return settings.SQLITE_URL


DATABASE_URL = _get_database_url()

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()