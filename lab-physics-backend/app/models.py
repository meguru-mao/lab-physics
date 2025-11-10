from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, ForeignKey
from .database import Base


class User(Base):
    # 线上环境要求使用表名 user_info
    __tablename__ = "user_info"
    __table_args__ = (
        UniqueConstraint("openid", name="uq_user_openid"),
    )

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    openid = Column(String(64), nullable=False, index=True)
    role = Column(String(20), default="normal", nullable=False)


class PlotRecord(Base):
    __tablename__ = "plot_records"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user_info.user_id"), nullable=False, index=True)
    experiment = Column(String(64), nullable=False)
    file_path = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)