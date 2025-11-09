from fastapi import FastAPI, Depends, HTTPException
import base64
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .config import settings
from .database import Base, engine, get_db
from .schemas import (
    WechatLoginRequest, LoginResponse, UserOut, UsersOut,
    FiberPlotRequest, FrankHertzRequest, MillikanRequest, MechanicsRequest,
    PlotImagesResponse,
)
from .crud import get_user_by_openid, create_user
from .auth import wechat_code2session
from .security import create_access_token
from .deps import get_current_user, get_current_admin_user
from .plots import (
    plot_fiber_iu, plot_fiber_pi, plot_photodiode_iv,
    plot_frank_hertz, plot_millikan,
    plot_mech_t2_m, plot_mech_v2_x2,
)


app = FastAPI(title=settings.APP_NAME)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态目录（用于访问生成的图片）
app.mount("/static", StaticFiles(directory="data"), name="static")


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


# -------------------------- 绘图接口 --------------------------

@app.post("/api/plots/fiber", response_model=PlotImagesResponse)
def api_plot_fiber(payload: FiberPlotRequest, user=Depends(get_current_user)):
    images = []
    images_data = []
    if payload.plot_type == 'iu':
        if not (payload.U and payload.I):
            raise HTTPException(status_code=400, detail="I-U 图需提供 U 与 I 数组")
        fpath, url = plot_fiber_iu(user.user_id, payload.U, payload.I)
        images.append(url)
        if payload.return_data_uri:
            with open(fpath, 'rb') as f:
                images_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
    elif payload.plot_type == 'pi':
        if not (payload.I and payload.P):
            raise HTTPException(status_code=400, detail="P-I 图需提供 I 与 P 数组")
        fpath, url = plot_fiber_pi(user.user_id, payload.I, payload.P)
        images.append(url)
        if payload.return_data_uri:
            with open(fpath, 'rb') as f:
                images_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
    elif payload.plot_type == 'photodiode':
        if not (payload.V and payload.I0 and payload.I1 and payload.I2):
            raise HTTPException(status_code=400, detail="光电二极管图需提供 V、I0、I1、I2 数组")
        fpath, url = plot_photodiode_iv(user.user_id, payload.V, payload.I0, payload.I1, payload.I2)
        images.append(url)
        if payload.return_data_uri:
            with open(fpath, 'rb') as f:
                images_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
    else:
        raise HTTPException(status_code=400, detail="未知的 plot_type")
    resp = PlotImagesResponse(images=images, message="生成完成")
    if images_data:
        resp.images_data = images_data
    return resp


@app.post("/api/plots/frank-hertz", response_model=PlotImagesResponse)
def api_plot_frank_hertz(payload: FrankHertzRequest, user=Depends(get_current_user)):
    if not payload.groups:
        raise HTTPException(status_code=400, detail="请至少提供一组数据")
    # 默认 VG2K：1..82（共 82 个点）
    VG2K = payload.VG2K if payload.VG2K else [float(i) for i in range(1, 83)]
    # 将 groups 转换为 (List[float], str) 列表
    groups = []
    for g in payload.groups:
        if not g.currents or len(g.currents) != len(VG2K):
            raise HTTPException(status_code=400, detail="每组 currents 需与 VG2K 长度一致（默认 82 项）")
        groups.append((g.currents, g.label))
    results = plot_frank_hertz(user.user_id, VG2K, groups)
    images = []
    images_data = []
    for fpath, url in results:
        images.append(url)
        if payload.return_data_uri:
            with open(fpath, 'rb') as f:
                images_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
    resp = PlotImagesResponse(images=images, message=f"共生成{len(images)}张图像")
    if images_data:
        resp.images_data = images_data
    return resp


@app.post("/api/plots/millikan", response_model=PlotImagesResponse)
def api_plot_millikan(payload: MillikanRequest, user=Depends(get_current_user)):
    if not payload.ni or not payload.qi or len(payload.ni) != len(payload.qi):
        raise HTTPException(status_code=400, detail="ni 与 qi 数组长度需一致且均非空")
    fpath, url = plot_millikan(user.user_id, payload.ni, payload.qi)
    images = [url]
    resp = PlotImagesResponse(images=images, message="生成完成")
    if payload.return_data_uri:
        with open(fpath, 'rb') as f:
            resp.images_data = ['data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')]
    return resp


@app.post("/api/plots/mechanics", response_model=PlotImagesResponse)
def api_plot_mechanics(payload: MechanicsRequest, user=Depends(get_current_user)):
    # T2-M
    if not (payload.t2m and payload.t2m.weights_g and payload.t2m.T10_avg_s):
        raise HTTPException(status_code=400, detail="t2m 字段缺失或为空")
    if len(payload.t2m.weights_g) != len(payload.t2m.T10_avg_s):
        raise HTTPException(status_code=400, detail="weights_g 与 T10_avg_s 需长度一致")
    fpath1, url1, k = plot_mech_t2_m(user.user_id, payload.t2m.m0_g, payload.t2m.weights_g, payload.t2m.T10_avg_s)

    # v2-x2
    if not (payload.v2x2 and payload.v2x2.x_cm and payload.v2x2.v_avg_cms):
        raise HTTPException(status_code=400, detail="v2x2 字段缺失或为空")
    if len(payload.v2x2.x_cm) != len(payload.v2x2.v_avg_cms):
        raise HTTPException(status_code=400, detail="x_cm 与 v_avg_cms 需长度一致")
    fpath2, url2, omega, T_calc = plot_mech_v2_x2(user.user_id, payload.v2x2.x_cm, payload.v2x2.v_avg_cms)

    resp = PlotImagesResponse(images=[url1, url2], message="生成完成")
    if payload.return_data_uri:
        imgs = []
        for fp in [fpath1, fpath2]:
            with open(fp, 'rb') as f:
                imgs.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
        resp.images_data = imgs
    return resp