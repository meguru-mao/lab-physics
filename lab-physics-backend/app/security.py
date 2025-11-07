from datetime import datetime, timedelta
import jwt
from typing import Optional
from .config import settings


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return token