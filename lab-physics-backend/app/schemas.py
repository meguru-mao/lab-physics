from pydantic import BaseModel
from typing import Optional, List


class UserOut(BaseModel):
    user_id: int
    openid: str
    role: str
    created_at: str

    class Config:
        from_attributes = True


class WechatLoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    token: str
    user: UserOut


class UsersOut(BaseModel):
    items: List[UserOut]