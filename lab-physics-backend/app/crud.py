from sqlalchemy.orm import Session
from typing import Optional
from .models import User


def get_user_by_openid(db: Session, openid: str) -> Optional[User]:
    return db.query(User).filter(User.openid == openid).first()


def create_user(db: Session, openid: str, role: str = "normal") -> User:
    user = User(openid=openid, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user