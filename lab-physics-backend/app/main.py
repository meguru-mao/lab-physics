from fastapi import FastAPI, Depends, HTTPException
import base64
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from .config import settings
from .database import Base, engine, get_db
from .schemas import (
    WechatLoginRequest, LoginResponse, UserOut, UsersOut,
    FiberPlotRequest, FrankHertzRequest, MillikanRequest, MechanicsRequest,
    PlotImagesResponse,
    ThermalRequest, PhotoDevicesRequest, SolarCellRequest, UltrasoundRequest,
    TaskStartResponse, TaskStatusResponse,
)
from .crud import get_user_by_openid, create_user, create_plot_records
from .auth import wechat_code2session
from .security import create_access_token
from .deps import get_current_user, get_current_admin_user
from .plots import (
    plot_fiber_iu, plot_fiber_pi, plot_photodiode_iv,
    plot_frank_hertz, plot_millikan,
    plot_mech_t2_m, plot_mech_v2_x2,
    plot_thermal, plot_photo_devices, plot_solar_cell, plot_ultrasound,
)
from .tasks import (
    start_fiber_task, start_frank_hertz_task, start_thermal_task,
    start_photo_devices_task, start_solar_cell_task, start_ultrasound_task,
    start_millikan_task, start_mechanics_task, get_task_for_user,
)

from . import models

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
    # 若历史环境中存在旧表名 users 而非 user_info，则在启动时自动重命名
    try:
        insp = inspect(engine)
        tables = insp.get_table_names()
        if "users" in tables and "user_info" not in tables:
            with engine.begin() as conn:
                backend = engine.url.get_backend_name()
                if backend.startswith("mysql"):
                    conn.exec_driver_sql("RENAME TABLE users TO user_info")
                else:
                    # SQLite 等其他后端的重命名语句
                    conn.exec_driver_sql("ALTER TABLE users RENAME TO user_info")
    except Exception:
        # 启动阶段重命名失败不阻塞服务，后续依然尝试建表
        pass

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


# -------------------------- 新增绘图接口 --------------------------

@app.post("/api/plots/thermal", response_model=PlotImagesResponse)
def api_plot_thermal(payload: ThermalRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # 默认温度序列：55,60,65,70,75,80（若前端未提供）
    temperatures = payload.temperatures if payload.temperatures else [55.0, 60.0, 65.0, 70.0, 75.0, 80.0]
    # 基本校验
    if not (payload.pt100_resistance and payload.ntc_resistance):
        raise HTTPException(status_code=400, detail="pt100_resistance / ntc_resistance 不能为空")
    if not (len(temperatures) == len(payload.pt100_resistance) == len(payload.ntc_resistance)):
        raise HTTPException(status_code=400, detail="三个数组长度需一致")
    results = plot_thermal(user.user_id, temperatures, payload.pt100_resistance, payload.ntc_resistance)
    try:
        create_plot_records(db, user.user_id, 'thermal', results)
    except Exception:
        pass
    images = [u for _, u in results]
    resp = PlotImagesResponse(images=images, message=f"共生成{len(images)}张图像")
    if payload.return_data_uri:
        imgs = []
        for fp, _ in results:
            with open(fp, 'rb') as f:
                imgs.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
        resp.images_data = imgs
    return resp


@app.post("/api/plots/photo-devices", response_model=PlotImagesResponse)
def api_plot_photo_devices(payload: PhotoDevicesRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # 基本非空校验（长度不做强制一致，按各自曲线绘制）
    for name in [
        'led_I','led_V','led_P','ld_I','ld_V','ld_P','pd_L','pd_I_L','pd_V','pd_I_V','pd_wl','pd_I_wl','pt_L','pt_I_L','pt_V','pt_I_V','pt_wl','pt_I_wl'
    ]:
        arr = getattr(payload, name, None)
        if not arr:
            raise HTTPException(status_code=400, detail=f"字段 {name} 不能为空")
    fpath, url = plot_photo_devices(
        user.user_id,
        payload.led_I, payload.led_V, payload.led_P,
        payload.ld_I, payload.ld_V, payload.ld_P, payload.ld_linear_start_idx or 4,
        payload.pd_L, payload.pd_I_L, payload.pd_V, payload.pd_I_V, payload.pd_wl, payload.pd_I_wl,
        payload.pt_L, payload.pt_I_L, payload.pt_V, payload.pt_I_V, payload.pt_wl, payload.pt_I_wl
    )
    try:
        create_plot_records(db, user.user_id, 'photo-devices', [(fpath, url)])
    except Exception:
        pass
    resp = PlotImagesResponse(images=[url], message="生成完成")
    if payload.return_data_uri:
        with open(fpath, 'rb') as f:
            resp.images_data = ['data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8')]
    return resp


@app.post("/api/plots/solar-cell", response_model=PlotImagesResponse)
def api_plot_solar_cell(payload: SolarCellRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # 基本校验
    for name in [
        'dark_voltage','dark_current','light_voltage','light_current','relative_intensity','light_power','short_circuit_current','open_circuit_voltage'
    ]:
        arr = getattr(payload, name, None)
        if not arr:
            raise HTTPException(status_code=400, detail=f"字段 {name} 不能为空")
    results = plot_solar_cell(
        user.user_id,
        payload.dark_voltage, payload.dark_current,
        payload.light_voltage, payload.light_current,
        payload.relative_intensity, payload.light_power, payload.short_circuit_current, payload.open_circuit_voltage
    )
    try:
        create_plot_records(db, user.user_id, 'solar-cell', results)
    except Exception:
        pass
    images = [u for _, u in results]
    resp = PlotImagesResponse(images=images, message=f"共生成{len(images)}张图像")
    if payload.return_data_uri:
        imgs = []
        for fp, _ in results:
            with open(fp, 'rb') as f:
                imgs.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
        resp.images_data = imgs
    return resp


@app.post("/api/plots/ultrasound", response_model=PlotImagesResponse)
def api_plot_ultrasound(payload: UltrasoundRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    # 校验必填数组非空
    required_groups = [
        't_free_fall','v_free_fall_1',
        't1','v1_1','v1_2','v1_3','v1_4',
        't2','v2_1','v2_2','v2_3','v2_4',
        't3','v3_1','v3_2','v3_3','v3_4',
        'm','a_measured'
    ]
    for name in required_groups:
        arr = getattr(payload, name, None)
        if not arr:
            raise HTTPException(status_code=400, detail=f"字段 {name} 不能为空")
    # 长度一致性：自由落体 1..4 组速度需与 t_free_fall 一致
    n_free = len(payload.t_free_fall)
    for vname in ['v_free_fall_1','v_free_fall_2','v_free_fall_3','v_free_fall_4']:
        v = getattr(payload, vname, None)
        if v is not None and len(v) != n_free:
            raise HTTPException(status_code=400, detail=f"{vname} 长度需与 t_free_fall 一致")
    # 三组匀变速：各组 4 次测量长度需与对应 t 数组一致
    for tname, vnames in [
        ('t1', ['v1_1','v1_2','v1_3','v1_4']),
        ('t2', ['v2_1','v2_2','v2_3','v2_4']),
        ('t3', ['v3_1','v3_2','v3_3','v3_4']),
    ]:
        n = len(getattr(payload, tname))
        for vn in vnames:
            v = getattr(payload, vn)
            if len(v) != n:
                raise HTTPException(status_code=400, detail=f"{vn} 长度需与 {tname} 一致")

    results = plot_ultrasound(
        user.user_id,
        payload.t_free_fall, payload.v_free_fall_1, payload.v_free_fall_2, payload.v_free_fall_3, payload.v_free_fall_4,
        payload.t1, payload.v1_1, payload.v1_2, payload.v1_3, payload.v1_4,
        payload.t2, payload.v2_1, payload.v2_2, payload.v2_3, payload.v2_4,
        payload.t3, payload.v3_1, payload.v3_2, payload.v3_3, payload.v3_4,
        payload.m, payload.a_measured
    )
    try:
        create_plot_records(db, user.user_id, 'ultrasound', results)
    except Exception:
        pass
    images = [u for _, u in results]
    resp = PlotImagesResponse(images=images, message=f"共生成{len(images)}张图像")
    if payload.return_data_uri:
        imgs = []
        for fp, _ in results:
            with open(fp, 'rb') as f:
                imgs.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
        resp.images_data = imgs
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

@app.post("/api/plots/mechanics/start", response_model=TaskStartResponse)
def api_plot_mechanics_start(payload: MechanicsRequest, user=Depends(get_current_user)):
    if not (payload.t2m and payload.t2m.weights_g and payload.t2m.T10_avg_s):
        raise HTTPException(status_code=400, detail="t2m 字段缺失或为空")
    if len(payload.t2m.weights_g) != len(payload.t2m.T10_avg_s):
        raise HTTPException(status_code=400, detail="weights_g 与 T10_avg_s 需长度一致")
    if not (payload.v2x2 and payload.v2x2.x_cm and payload.v2x2.v_avg_cms):
        raise HTTPException(status_code=400, detail="v2x2 字段缺失或为空")
    if len(payload.v2x2.x_cm) != len(payload.v2x2.v_avg_cms):
        raise HTTPException(status_code=400, detail="x_cm 与 v_avg_cms 需长度一致")
    tid = start_mechanics_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')
@app.post("/api/plots/fiber/start", response_model=TaskStartResponse)
def api_plot_fiber_start(payload: FiberPlotRequest, user=Depends(get_current_user)):
    if payload.plot_type == 'iu':
        if not (payload.U and payload.I):
            raise HTTPException(status_code=400, detail="I-U 图需提供 U 与 I 数组")
    elif payload.plot_type == 'pi':
        if not (payload.I and payload.P):
            raise HTTPException(status_code=400, detail="P-I 图需提供 I 与 P 数组")
    elif payload.plot_type == 'photodiode':
        if not (payload.V and payload.I0 and payload.I1 and payload.I2):
            raise HTTPException(status_code=400, detail="光电二极管图需提供 V、I0、I1、I2 数组")
    else:
        raise HTTPException(status_code=400, detail="未知的 plot_type")
    tid = start_fiber_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')

@app.get("/api/plots/status/{task_id}", response_model=TaskStatusResponse)
def api_plot_status(task_id: str, user=Depends(get_current_user)):
    t = get_task_for_user(task_id, user.user_id)
    if not t:
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskStatusResponse(status=t.status, images=t.images or None, images_data=t.images_data, message=t.message)
@app.post("/api/plots/frank-hertz/start", response_model=TaskStartResponse)
def api_plot_frank_hertz_start(payload: FrankHertzRequest, user=Depends(get_current_user)):
    if not payload.groups:
        raise HTTPException(status_code=400, detail="请至少提供一组数据")
    VG2K = payload.VG2K if payload.VG2K else [float(i) for i in range(1, 83)]
    for g in payload.groups:
        if not g.currents or len(g.currents) != len(VG2K):
            raise HTTPException(status_code=400, detail="每组 currents 需与 VG2K 长度一致（默认 82 项）")
    tid = start_frank_hertz_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')
@app.post("/api/plots/thermal/start", response_model=TaskStartResponse)
def api_plot_thermal_start(payload: ThermalRequest, user=Depends(get_current_user)):
    temperatures = payload.temperatures if payload.temperatures else [55.0, 60.0, 65.0, 70.0, 75.0, 80.0]
    if not (payload.pt100_resistance and payload.ntc_resistance):
        raise HTTPException(status_code=400, detail="pt100_resistance / ntc_resistance 不能为空")
    if not (len(temperatures) == len(payload.pt100_resistance) == len(payload.ntc_resistance)):
        raise HTTPException(status_code=400, detail="三个数组长度需一致")
    tid = start_thermal_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')
@app.post("/api/plots/photo-devices/start", response_model=TaskStartResponse)
def api_plot_photo_devices_start(payload: PhotoDevicesRequest, user=Depends(get_current_user)):
    for name in [
        'led_I','led_V','led_P','ld_I','ld_V','ld_P','pd_L','pd_I_L','pd_V','pd_I_V','pd_wl','pd_I_wl','pt_L','pt_I_L','pt_V','pt_I_V','pt_wl','pt_I_wl'
    ]:
        arr = getattr(payload, name, None)
        if not arr:
            raise HTTPException(status_code=400, detail=f"字段 {name} 不能为空")
    tid = start_photo_devices_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')
@app.post("/api/plots/solar-cell/start", response_model=TaskStartResponse)
def api_plot_solar_cell_start(payload: SolarCellRequest, user=Depends(get_current_user)):
    for name in [
        'dark_voltage','dark_current','light_voltage','light_current','relative_intensity','light_power','short_circuit_current','open_circuit_voltage'
    ]:
        arr = getattr(payload, name, None)
        if not arr:
            raise HTTPException(status_code=400, detail=f"字段 {name} 不能为空")
    tid = start_solar_cell_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')
@app.post("/api/plots/ultrasound/start", response_model=TaskStartResponse)
def api_plot_ultrasound_start(payload: UltrasoundRequest, user=Depends(get_current_user)):
    required_groups = [
        't_free_fall','v_free_fall_1',
        't1','v1_1','v1_2','v1_3','v1_4',
        't2','v2_1','v2_2','v2_3','v2_4',
        't3','v3_1','v3_2','v3_3','v3_4',
        'm','a_measured'
    ]
    for name in required_groups:
        arr = getattr(payload, name, None)
        if not arr:
            raise HTTPException(status_code=400, detail=f"字段 {name} 不能为空")
    n_free = len(payload.t_free_fall)
    for vname in ['v_free_fall_1','v_free_fall_2','v_free_fall_3','v_free_fall_4']:
        v = getattr(payload, vname, None)
        if v is not None and len(v) != n_free:
            raise HTTPException(status_code=400, detail=f"{vname} 长度需与 t_free_fall 一致")
    for tname, vnames in [
        ('t1', ['v1_1','v1_2','v1_3','v1_4']),
        ('t2', ['v2_1','v2_2','v2_3','v2_4']),
        ('t3', ['v3_1','v3_2','v3_3','v3_4']),
    ]:
        n = len(getattr(payload, tname))
        for vn in vnames:
            v = getattr(payload, vn)
            if len(v) != n:
                raise HTTPException(status_code=400, detail=f"{vn} 长度需与 {tname} 一致")
    tid = start_ultrasound_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')
@app.post("/api/plots/millikan/start", response_model=TaskStartResponse)
def api_plot_millikan_start(payload: MillikanRequest, user=Depends(get_current_user)):
    if not payload.ni or not payload.qi or len(payload.ni) != len(payload.qi):
        raise HTTPException(status_code=400, detail="ni 与 qi 数组长度需一致且均非空")
    tid = start_millikan_task(user.user_id, payload)
    return TaskStartResponse(task_id=tid, status='pending')
