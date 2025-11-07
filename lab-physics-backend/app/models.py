from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from .database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("openid", name="uq_user_openid"),
    )

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    openid = Column(String(64), nullable=False, index=True)
    role = Column(String(20), default="normal", nullable=False)