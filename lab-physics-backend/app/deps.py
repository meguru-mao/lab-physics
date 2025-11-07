from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt
from typing import Optional

from .database import get_db
from .models import User
from .crud import get_user_by_openid
from .config import settings


bearer_scheme = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> Optional[str]:
    try:
        data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return data.get("sub")
    except Exception:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = _decode_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_admin_user(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    return user