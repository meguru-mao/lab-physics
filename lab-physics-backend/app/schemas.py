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


class FrankHertzGroup(BaseModel):
    currents: List[float]
    label: str


class FrankHertzRequest(BaseModel):
    # 若未提供，则在接口层默认使用 1..82 的序列
    VG2K: Optional[List[float]] = None
    groups: List[FrankHertzGroup]


class MillikanRequest(BaseModel):
    ni: List[float]
    qi: List[float]


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


class PlotImagesResponse(BaseModel):
    images: List[str]
    message: Optional[str] = None