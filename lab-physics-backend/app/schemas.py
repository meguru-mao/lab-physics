from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal


class UserOut(BaseModel):
    user_id: int
    openid: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class WechatLoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    token: str
    user: UserOut


class UsersOut(BaseModel):
    items: List[UserOut]


# -------------------------- 绘图接口 Schemas --------------------------

# 光纤传感与通讯：根据 plot_type 选择不同的字段
class FiberPlotRequest(BaseModel):
    plot_type: Literal['iu', 'pi', 'photodiode'] = Field(..., description="绘图类型：iu|pi|photodiode")
    # iu
    U: Optional[List[float]] = Field(None, description="I-U 图：电压数组")
    I: Optional[List[float]] = Field(None, description="I-U/P-I 图：电流数组 或 输出特性电流")
    # pi
    P: Optional[List[float]] = Field(None, description="P-I 图：光功率数组")
    # photodiode
    V: Optional[List[float]] = Field(None, description="光电二极管：反向偏置电压数组")
    I0: Optional[List[float]] = Field(None, description="光电二极管：P=0 mW 光电流")
    I1: Optional[List[float]] = Field(None, description="光电二极管：P=0.100 mW 光电流")
    I2: Optional[List[float]] = Field(None, description="光电二极管：P=0.200 mW 光电流")
    # 是否返回 data URI（用于云托管下图片外网不可直接访问的场景）
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")


class FrankHertzGroup(BaseModel):
    currents: List[float]
    label: str


class FrankHertzRequest(BaseModel):
    # 若未提供，则在接口层默认使用 1..82 的序列
    VG2K: Optional[List[float]] = None
    groups: List[FrankHertzGroup]
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")


class MillikanRequest(BaseModel):
    ni: List[float]
    qi: List[float]
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")


class MechanicsT2M(BaseModel):
    m0_g: float
    weights_g: List[float]
    T10_avg_s: List[float]


class MechanicsV2X2(BaseModel):
    x_cm: List[float]
    v_avg_cms: List[float]


class MechanicsRequest(BaseModel):
    t2m: MechanicsT2M
    v2x2: MechanicsV2X2
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")


class PlotImagesResponse(BaseModel):
    images: List[str]
    images_data: Optional[List[str]] = None
    message: Optional[str] = None

class TaskStartResponse(BaseModel):
    task_id: str
    status: Literal['pending']

class TaskStatusResponse(BaseModel):
    status: Literal['pending','completed','failed']
    images: Optional[List[str]] = None
    images_data: Optional[List[str]] = None
    message: Optional[str] = None

# -------------------------- 新增：四个实验的输入 Schemas --------------------------

class ThermalRequest(BaseModel):
    # 温度允许不传，后端默认使用 55,60,65,70,75,80
    temperatures: Optional[List[float]] = Field(None, description="温度数组（°C），不传则使用默认 [55,60,65,70,75,80]")
    pt100_resistance: List[float] = Field(..., description="Pt100 电阻数组（Ω）")
    ntc_resistance: List[float] = Field(..., description="NTC 热敏电阻数组（Ω）")
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")


class PhotoDevicesRequest(BaseModel):
    # LED
    led_I: List[float] = Field(..., description="LED 电流 (mA)")
    led_V: List[float] = Field(..., description="LED 电压 (V)")
    led_P: List[float] = Field(..., description="LED 光功率 (μW)")
    # LD
    ld_I: List[float] = Field(..., description="LD 电流 (mA)")
    ld_V: List[float] = Field(..., description="LD 电压 (V)")
    ld_P: List[float] = Field(..., description="LD 光功率 (μW)")
    ld_linear_start_idx: Optional[int] = Field(4, description="LD P-I 线性拟合起始索引（默认4）")
    # 光敏二极管
    pd_L: List[float] = Field(..., description="照度 (Lx)")
    pd_I_L: List[float] = Field(..., description="光敏二极管电流 (μA) - 光照特性")
    pd_V: List[float] = Field(..., description="电压 (V) - 伏安特性")
    pd_I_V: List[float] = Field(..., description="电流 (μA) - 伏安特性")
    pd_wl: List[float] = Field(..., description="波长 (nm) - 光谱特性")
    pd_I_wl: List[float] = Field(..., description="电流 (μA) - 光谱特性")
    # 光敏三极管
    pt_L: List[float] = Field(..., description="照度 (Lx)")
    pt_I_L: List[float] = Field(..., description="电流 (mA) - 光照特性")
    pt_V: List[float] = Field(..., description="电压 (V) - 伏安特性")
    pt_I_V: List[float] = Field(..., description="电流 (mA) - 伏安特性")
    pt_wl: List[float] = Field(..., description="波长 (nm) - 光谱特性")
    pt_I_wl: List[float] = Field(..., description="电流 (mA) - 光谱特性")
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")


class SolarCellRequest(BaseModel):
    # 图1：全暗伏安特性
    dark_voltage: List[float] = Field(..., description="外加偏压 (V)")
    dark_current: List[float] = Field(..., description="电流 (mA)")
    # 图2：光照输出伏安特性
    light_voltage: List[float] = Field(..., description="输出电压 (V)")
    light_current: List[float] = Field(..., description="输出电流 (mA)")
    # 图3/图4/图5/图6：光照特性
    relative_intensity: List[float] = Field(..., description="相对光强")
    light_power: List[float] = Field(..., description="光功率 (mW)")
    short_circuit_current: List[float] = Field(..., description="短路电流 (mA)")
    open_circuit_voltage: List[float] = Field(..., description="开路电压 (V)")
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")


class UltrasoundRequest(BaseModel):
    # 自由落体（至少 1 组速度，最多 4 组）
    t_free_fall: List[float] = Field(..., description="时间数组 (s)")
    v_free_fall_1: List[float] = Field(..., description="第1组速度 (m/s)")
    v_free_fall_2: Optional[List[float]] = Field(None, description="第2组速度 (m/s)")
    v_free_fall_3: Optional[List[float]] = Field(None, description="第3组速度 (m/s)")
    v_free_fall_4: Optional[List[float]] = Field(None, description="第4组速度 (m/s)")
    # 匀变速运动（3组，每组 1..4 次测量）
    t1: List[float] = Field(..., description="第1组时间 (s)")
    v1_1: List[float] = Field(..., description="第1组第1次速度 (m/s)")
    v1_2: List[float] = Field(..., description="第1组第2次速度 (m/s)")
    v1_3: List[float] = Field(..., description="第1组第3次速度 (m/s)")
    v1_4: List[float] = Field(..., description="第1组第4次速度 (m/s)")
    t2: List[float] = Field(..., description="第2组时间 (s)")
    v2_1: List[float] = Field(..., description="第2组第1次速度 (m/s)")
    v2_2: List[float] = Field(..., description="第2组第2次速度 (m/s)")
    v2_3: List[float] = Field(..., description="第2组第3次速度 (m/s)")
    v2_4: List[float] = Field(..., description="第2组第4次速度 (m/s)")
    t3: List[float] = Field(..., description="第3组时间 (s)")
    v3_1: List[float] = Field(..., description="第3组第1次速度 (m/s)")
    v3_2: List[float] = Field(..., description="第3组第2次速度 (m/s)")
    v3_3: List[float] = Field(..., description="第3组第3次速度 (m/s)")
    v3_4: List[float] = Field(..., description="第3组第4次速度 (m/s)")
    # 牛顿第二定律验证
    m: List[float] = Field(..., description="砝码质量 (kg)")
    a_measured: List[float] = Field(..., description="测量加速度 (m/s²)")
    return_data_uri: Optional[bool] = Field(False, description="是否返回 data URI 以便前端直接显示")
