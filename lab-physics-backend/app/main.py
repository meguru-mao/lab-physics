from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .schemas import WechatLoginRequest, LoginResponse, UserOut, UsersOut
from .crud import get_user_by_openid, create_user
from .auth import wechat_code2session
from .security import create_access_token
from .deps import get_current_user, get_current_admin_user


app = FastAPI(title=settings.APP_NAME)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # 自动建表（不存在则创建）
    Base.metadata.create_all(bind=engine)


@app.get("/api/ping")
def ping():
    return {"message": "pong"}


@app.post("/api/auth/wechat", response_model=LoginResponse)
def wechat_login(payload: WechatLoginRequest, db: Session = Depends(get_db)):
    data = wechat_code2session(payload.code)
    openid = data["openid"]
    user = get_user_by_openid(db, openid)
    if not user:
        user = create_user(db, openid=openid, role="normal")

    token = create_access_token(subject=str(user.user_id))
    return LoginResponse(token=token, user=UserOut.model_validate(user))


@app.get("/api/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return UserOut.model_validate(user)


@app.get("/api/admin/users", response_model=UsersOut)
def admin_list_users(admin=Depends(get_current_admin_user), db: Session = Depends(get_db)):
    from .models import User
    users = db.query(User).order_by(User.user_id.asc()).all()
    return UsersOut(items=[UserOut.model_validate(u) for u in users])