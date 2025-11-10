from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from .models import User, PlotRecord


def get_user_by_openid(db: Session, openid: str) -> Optional[User]:
    return db.query(User).filter(User.openid == openid).first()


def create_user(db: Session, openid: str, role: str = "normal") -> User:
    user = User(openid=openid, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_plot_records(db: Session, user_id: int, experiment: str, files_and_urls: List[Tuple[str, str]]):
    """批量插入绘图记录。
    :param files_and_urls: [(file_path, url), ...]
    """
    items = [PlotRecord(user_id=user_id, experiment=experiment, file_path=fp, url=url) for fp, url in files_and_urls]
    if not items:
        return
    try:
        db.add_all(items)
        db.commit()
    except Exception:
        db.rollback()