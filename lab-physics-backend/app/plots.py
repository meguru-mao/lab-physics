"""
绘图服务模块：封装四个实验的绘图函数。

注意：
- 弗兰克-赫兹曲线采用 SciPy CubicSpline 进行三次样条拟合；
- 输出目录统一为 data/plots/{user_id}/{experiment}/；
- 返回可通过 /static 路径访问的相对 URL（例如 /static/plots/1/millikan/xxx.png）。
"""

import os
import uuid
from typing import List, Tuple

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import glob
from scipy.interpolate import CubicSpline
from scipy import optimize, stats


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _set_chinese_font():
    """尽量设置可用中文字体，保证中文标题/标签在不同环境下可读。
    优先使用 Noto Sans CJK / Source Han Sans（容器中通过 fonts-noto-cjk 安装），并在找不到时回退。
    """
    try:
        # 主动加载系统中的 CJK 字体文件，避免 Matplotlib 未扫描到导致缺字
        candidate_files = []
        for root in [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "/app/fonts",
        ]:
            for pattern in [
                "**/NotoSansCJK*.ttc",
                "**/NotoSansCJK*.otf",
                "**/SourceHanSans*.otf",
                "**/SourceHanSans*.ttc",
            ]:
                candidate_files.extend(glob.glob(os.path.join(root, pattern), recursive=True))
        for f in candidate_files:
            try:
                fm.fontManager.addfont(f)
            except Exception:
                pass

        # 收集可用字体名称
        font_names = [f.name for f in fm.fontManager.ttflist]
        preferred = []
        for name in [
            'Noto Sans CJK SC',
            'Noto Sans CJK',
            'Source Han Sans CN',
            'Noto Sans SC',
            'WenQuanYi Micro Hei',
            'SimHei',
            'Microsoft YaHei',
        ]:
            if name in font_names:
                preferred.append(name)

        fallback = ['DejaVu Sans', 'Arial Unicode MS', 'Arial', 'Liberation Sans']
        fonts = preferred + fallback
        if not fonts:
            fonts = fallback

        matplotlib.rcParams['font.sans-serif'] = fonts
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['axes.unicode_minus'] = False
    except Exception:
        matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Liberation Sans']
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['axes.unicode_minus'] = False


def _new_fig_size_cm(width_cm: float = 15.0, height_cm: float = 8.0) -> Tuple[float, float]:
    return (width_cm / 2.54, height_cm / 2.54)


def _save_fig(user_id: int, experiment: str, filename_prefix: str) -> Tuple[str, str]:
    """保存当前 plt 图像到标准目录，返回 (文件绝对路径, 访问URL)。"""
    base_dir = os.path.join('data', 'plots', str(user_id), experiment)
    _ensure_dir(base_dir)
    fname = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.png"
    fpath = os.path.join(base_dir, fname)
    plt.savefig(fpath, dpi=300, bbox_inches='tight')
    plt.close()
    url = f"/static/plots/{user_id}/{experiment}/{fname}"
    return fpath, url


# -------------------------- 光纤传感与通讯 --------------------------
def plot_fiber_iu(user_id: int, U: List[float], I: List[float]) -> Tuple[str, str]:
    _set_chinese_font()
    fig, ax = plt.subplots(figsize=_new_fig_size_cm(), dpi=300)
    U_arr = np.array(U, dtype=float)
    I_arr = np.array(I, dtype=float)
    ax.scatter(U_arr, I_arr, color='red', s=50, label='测量数据点', zorder=5)
    ax.plot(U_arr, I_arr, color='blue', linewidth=1.5, alpha=0.7, label='趋势线')
    ax.set_title('半导体激光器伏安特性（I-U）图', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('正向偏压 U (V)', fontsize=12)
    ax.set_ylabel('发射管电流 I (mA)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fpath, url = _save_fig(user_id, 'fiber', 'I-U')
    return fpath, url


def plot_fiber_pi(user_id: int, I: List[float], P: List[float]) -> Tuple[str, str]:
    _set_chinese_font()
    fig, ax = plt.subplots(figsize=_new_fig_size_cm(), dpi=300)
    I_arr = np.array(I, dtype=float)
    P_arr = np.array(P, dtype=float)
    ax.scatter(I_arr, P_arr, color='darkorange', s=50, label='测量数据点', zorder=5)
    ax.plot(I_arr, P_arr, color='green', linewidth=1.5, alpha=0.7, label='趋势线')
    ax.set_title('半导体激光器输出特性（P-I）图', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('发射管电流 I (mA)', fontsize=12)
    ax.set_ylabel('光功率 P (mW)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fpath, url = _save_fig(user_id, 'fiber', 'P-I')
    return fpath, url


def plot_photodiode_iv(user_id: int, V: List[float], I0: List[float], I1: List[float], I2: List[float]) -> Tuple[str, str]:
    _set_chinese_font()
    fig, ax = plt.subplots(figsize=_new_fig_size_cm(), dpi=300)
    V_arr = np.array(V, dtype=float)
    I0_arr = np.array(I0, dtype=float)
    I1_arr = np.array(I1, dtype=float)
    I2_arr = np.array(I2, dtype=float)
    ax.scatter(V_arr, I0_arr, color='black', s=50, label='P=0 mW', zorder=5)
    ax.plot(V_arr, I0_arr, color='black', linewidth=1.5, alpha=0.7)
    ax.scatter(V_arr, I1_arr, color='blue', s=50, label='P=0.100 mW', zorder=5)
    ax.plot(V_arr, I1_arr, color='blue', linewidth=1.5, alpha=0.7)
    ax.scatter(V_arr, I2_arr, color='red', s=50, label='P=0.200 mW', zorder=5)
    ax.plot(V_arr, I2_arr, color='red', linewidth=1.5, alpha=0.7)
    ax.set_title('光电二极管伏安特性图', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('反向偏置电压 V (V)', fontsize=12)
    ax.set_ylabel('光电流 I (μA)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fpath, url = _save_fig(user_id, 'fiber', 'photodiode-IV')
    return fpath, url


# -------------------------- 弗兰克-赫兹 --------------------------
def _r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0


def _polyfit_smooth(x: np.ndarray, y: np.ndarray, deg: int = 5) -> Tuple[np.ndarray, np.ndarray]:
    """保留旧方法（未使用），避免破坏已有导入；实际绘图改用 CubicSpline。"""
    deg = max(1, min(deg, max(1, len(x) // 3)))
    coefs = np.polyfit(x, y, deg=deg)
    poly = np.poly1d(coefs)
    x_fit = np.linspace(float(np.min(x)), float(np.max(x)), 200)
    y_fit = poly(x_fit)
    y_pred_orig = poly(x)
    return x_fit, y_fit, y_pred_orig


def plot_frank_hertz(user_id: int, VG2K: List[float], groups: List[Tuple[List[float], str]]) -> List[Tuple[str, str]]:
    _set_chinese_font()
    results: List[Tuple[str, str]] = []
    x = np.array(VG2K, dtype=float)
    for idx, (current_list, label) in enumerate(groups, start=1):
        y = np.array(current_list, dtype=float)
        fig, ax = plt.subplots(figsize=_new_fig_size_cm(), dpi=300)
        ax.scatter(x, y, color='#1f77b4', s=30, alpha=0.7, label='实验数据')
        # 三次样条拟合（与示例一致）
        spline = CubicSpline(x, y)
        x_fit = np.linspace(float(np.min(x)), float(np.max(x)), 200)
        y_fit = spline(x_fit)
        # 用原始点的拟合值计算 R²
        y_pred_orig = spline(x)
        r2 = _r2_score(y, y_pred_orig)
        ax.plot(x_fit, y_fit, color='#ff7f0e', linewidth=2, label=f'三次样条拟合\nR²={r2:.4f}')
        ax.set_title(f'第{idx}组参数 {label}\n弗兰克-赫兹实验 I-VG2K 曲线', fontsize=14, pad=15)
        ax.set_xlabel('加速电压 VG2K (V)', fontsize=12)
        ax.set_ylabel('板极电流 I (μA)', fontsize=12)
        ax.legend(loc='center left', fontsize=10, framealpha=0.9, bbox_to_anchor=(0.02, 0.5))
        ax.grid(True, color='#e0e0e0', linestyle='--', linewidth=0.5, alpha=0.7)
        plt.tight_layout()
        fpath, url = _save_fig(user_id, 'frank-hertz', f'frank_group{idx}')
        results.append((fpath, url))
    return results


# -------------------------- 密里根油滴 --------------------------
def plot_millikan(user_id: int, ni: List[float], qi: List[float]) -> Tuple[str, str]:
    _set_chinese_font()
    x = np.array(ni, dtype=float)
    y = np.array(qi, dtype=float)
    # 线性拟合（强制过原点）：最小二乘 k = sum(x*y)/sum(x^2)
    denom = float(np.sum(x * x))
    k = float(np.sum(x * y) / denom) if denom > 0 else 0.0
    # R^2
    y_pred = k * x
    r2 = _r2_score(y, y_pred)

    fig, ax = plt.subplots(figsize=_new_fig_size_cm(), dpi=300)
    ax.scatter(x, y, color='darkred', s=60, marker='o', edgecolor='black', label='实验数据点')
    x_fit = np.linspace(float(np.min(x)) - 0.2, float(np.max(x)) + 0.2, 100)
    y_fit = k * x_fit
    ax.plot(x_fit, y_fit, color='darkblue', linewidth=2, label=f'拟合直线: qi = {k:.4f} x ni')
    ax.set_title('密立根油滴实验 qi-ni 关系图', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('倍数估计 ni（无单位）', fontsize=12, fontweight='bold')
    ax.set_ylabel('油滴电荷量 qi (x10^-19 C)', fontsize=12, fontweight='bold')
    text_str = (
        f'实验测得电子电荷量 e = {k:.4f} x10^-19 C\n'
        f'R^2 = {r2:.4f}\n'
        '理论参考值 e理论 = 1.6022 x10^-19 C'
    )
    ax.text(0.02, 0.98, text_str, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.85))
    ax.grid(True, linestyle='--', alpha=0.6, color='gray')
    ax.legend(loc='lower right', fontsize=10, frameon=True)
    plt.tight_layout()
    fpath, url = _save_fig(user_id, 'millikan', 'millikan_qi_ni')
    return fpath, url


# -------------------------- 力学实验 --------------------------
def plot_mech_t2_m(user_id: int, m0_g: float, weights_g: List[float], T10_avg_s: List[float]) -> Tuple[str, str, float]:
    _set_chinese_font()
    m0_g = float(m0_g)
    w = np.array(weights_g, dtype=float)
    T10 = np.array(T10_avg_s, dtype=float)
    M_kg = (m0_g + w) / 1000.0
    T_s = T10 / 10.0
    T2 = T_s ** 2
    coef = np.polyfit(M_kg, T2, deg=1)
    k_fit, b_fit = float(coef[0]), float(coef[1])
    T2_fit = np.poly1d(coef)(M_kg)
    r2 = _r2_score(T2, T2_fit)
    k = 4 * (np.pi ** 2) / k_fit if k_fit != 0 else 0.0
    fig, ax = plt.subplots(figsize=_new_fig_size_cm(), dpi=300)
    ax.scatter(M_kg, T2, color='blue', s=50, label='实验数据', zorder=5)
    ax.plot(M_kg, T2_fit, color='red', linewidth=2, label=f'线性拟合：T²={k_fit:.2f}M + {b_fit:.4f}', zorder=3)
    ax.set_title('T²-M曲线图（振子周期平方与质量关系）', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('振子质量M (kg)', fontsize=12)
    ax.set_ylabel('周期平方T² (s²)', fontsize=12)
    ax.legend(loc='lower right', fontsize=10)
    ax.text(0.05, 0.95, f'劲度系数k={k:.2f} N/m\n截距b={b_fit:.4f} s²\nR²={r2:.6f}',
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fpath, url = _save_fig(user_id, 'mechanics', 'mech_T2_M')
    return fpath, url, k


def plot_mech_v2_x2(user_id: int, x_cm: List[float], v_avg_cms: List[float]) -> Tuple[str, str, float, float]:
    _set_chinese_font()
    x_cm = np.array(x_cm, dtype=float)
    v_avg = np.array(v_avg_cms, dtype=float)
    x2 = x_cm ** 2
    v2 = v_avg ** 2
    coef = np.polyfit(x2, v2, deg=1)
    k_v, b_v = float(coef[0]), float(coef[1])
    v2_fit = np.poly1d(coef)(x2)
    r2 = _r2_score(v2, v2_fit)
    # ω = sqrt(-k_v)；若 k_v 为正则无法计算，取 0 以避免 NaN
    omega = np.sqrt(abs(-k_v)) if k_v < 0 else 0.0
    T_calc = (2 * np.pi / omega) if omega > 0 else 0.0
    fig, ax = plt.subplots(figsize=_new_fig_size_cm(), dpi=300)
    ax.scatter(x2, v2, color='green', marker='^', s=50, label='实验数据', zorder=5)
    ax.plot(x2, v2_fit, color='orange', linewidth=2, label=f'线性拟合：v²={k_v:.4f}x² + {b_v:.2f}', zorder=3)
    ax.set_title('v²-x²曲线图（振子速度平方与位移平方关系）', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('位移平方x² (cm²)', fontsize=12)
    ax.set_ylabel('速度平方v² (cm²/s²)', fontsize=12)
    ax.legend(loc='upper right', fontsize=10)
    annot_text = (f'角频率ω={omega:.2f} rad/s\n计算周期T_calc={T_calc:.4f} s\nR²={r2:.6f}')
    ax.text(0.05, 0.05, annot_text, transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fpath, url = _save_fig(user_id, 'mechanics', 'mech_v2_x2')
    return fpath, url, omega, T_calc


# -------------------------- 新增：热学综合实验 --------------------------
def plot_thermal(user_id: int, temperatures: List[float], pt100_resistance: List[float], ntc_resistance: List[float]) -> List[Tuple[str, str]]:
    """根据前端传入数据绘制 Pt100 与 NTC 两张曲线图。"""
    _set_chinese_font()
    results: List[Tuple[str, str]] = []

    # Pt100 电阻-温度
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    t_arr = np.array(temperatures, dtype=float)
    pt_arr = np.array(pt100_resistance, dtype=float)
    plt.plot(t_arr, pt_arr, 'b-o', linewidth=2, markersize=6, label='Pt100电阻')
    plt.xlabel('温度 (℃)')
    plt.ylabel('电阻 (Ω)')
    plt.title('Pt100金属电阻随温度变化曲线', fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.xticks(t_arr)
    plt.tight_layout()
    results.append(_save_fig(user_id, 'thermal', 'Pt100_电阻温度变化'))

    # NTC 电阻-温度
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    ntc_arr = np.array(ntc_resistance, dtype=float)
    plt.plot(t_arr, ntc_arr, 'r-s', linewidth=2, markersize=6, label='NTC热敏电阻')
    plt.xlabel('温度 (℃)')
    plt.ylabel('电阻 (Ω)')
    plt.title('NTC热敏电阻随温度变化曲线', fontweight='bold')
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=10)
    plt.xticks(t_arr)
    plt.tight_layout()
    results.append(_save_fig(user_id, 'thermal', 'NTC_电阻温度变化'))

    return results


# -------------------------- 新增：光电器件性能 --------------------------
def plot_photo_devices(
    user_id: int,
    led_I: List[float], led_V: List[float], led_P: List[float],
    ld_I: List[float], ld_V: List[float], ld_P: List[float], ld_linear_start_idx: int,
    pd_L: List[float], pd_I_L: List[float], pd_V: List[float], pd_I_V: List[float], pd_wl: List[float], pd_I_wl: List[float],
    pt_L: List[float], pt_I_L: List[float], pt_V: List[float], pt_I_V: List[float], pt_wl: List[float], pt_I_wl: List[float]
) -> Tuple[str, str]:
    """生成 2x5 的十张子图合并图。包含 LD 阈值线性拟合。"""
    _set_chinese_font()
    # 强制中文字体
    font_prop = fm.FontProperties(family=matplotlib.rcParams.get('font.sans-serif')[0])
    fig, axes = plt.subplots(2, 5, figsize=(20, 8))
    fig.suptitle('光电器件性能测试实验曲线', fontsize=16, fontweight='bold', fontproperties=font_prop)

    led_I = np.array(led_I, dtype=float); led_V = np.array(led_V, dtype=float); led_P = np.array(led_P, dtype=float)
    ld_I = np.array(ld_I, dtype=float); ld_V = np.array(ld_V, dtype=float); ld_P = np.array(ld_P, dtype=float)
    pd_L = np.array(pd_L, dtype=float); pd_I_L = np.array(pd_I_L, dtype=float)
    pd_V = np.array(pd_V, dtype=float); pd_I_V = np.array(pd_I_V, dtype=float)
    pd_wl = np.array(pd_wl, dtype=float); pd_I_wl = np.array(pd_I_wl, dtype=float)
    pt_L = np.array(pt_L, dtype=float); pt_I_L = np.array(pt_I_L, dtype=float)
    pt_V = np.array(pt_V, dtype=float); pt_I_V = np.array(pt_I_V, dtype=float)
    pt_wl = np.array(pt_wl, dtype=float); pt_I_wl = np.array(pt_I_wl, dtype=float)

    # 子图1：LD P-I（含阈值线性拟合）
    axes[0,0].scatter(ld_I, ld_P, color='red', label='实验数据')
    start = max(0, min(int(ld_linear_start_idx), max(0, len(ld_I)-1)))
    ld_I_linear = ld_I[start:]
    ld_P_linear = ld_P[start:]
    if len(ld_I_linear) >= 2:
        k, b = np.polyfit(ld_I_linear, ld_P_linear, 1)
        I_th = float(-b / k) if k != 0 else 0.0
        I_fit = np.linspace(I_th, float(np.max(ld_I)) + 1, 50)
        P_fit = k * I_fit + b
        axes[0,0].plot(I_fit, P_fit, 'k--', label=f'线性拟合: P={k:.2f}I+{b:.2f}')
        axes[0,0].axvline(x=I_th, color='green', linestyle=':', label=f'阈值电流={I_th:.2f}mA')
    axes[0,0].set_xlabel('电流I (mA)'); axes[0,0].set_ylabel('功率P (μW)'); axes[0,0].set_title('LD P-I特性曲线'); axes[0,0].legend(); axes[0,0].grid(True, alpha=0.3)

    # 子图2：LD I-V
    axes[0,1].scatter(ld_V, ld_I, color='orange', label='实验数据')
    axes[0,1].plot(ld_V, ld_I, 'orange', alpha=0.6)
    axes[0,1].set_xlabel('电压V (V)'); axes[0,1].set_ylabel('电流I (mA)'); axes[0,1].set_title('LD I-V特性曲线'); axes[0,1].legend(); axes[0,1].grid(True, alpha=0.3)

    # 子图3：LED P-I
    axes[0,2].scatter(led_I, led_P, color='blue', label='实验数据')
    axes[0,2].plot(led_I, led_P, 'blue', alpha=0.6)
    axes[0,2].set_xlabel('电流I (mA)'); axes[0,2].set_ylabel('功率P (μW)'); axes[0,2].set_title('LED P-I特性曲线'); axes[0,2].legend(); axes[0,2].grid(True, alpha=0.3)

    # 子图4：LED I-V
    axes[0,3].scatter(led_V, led_I, color='purple', label='实验数据')
    axes[0,3].plot(led_V, led_I, 'purple', alpha=0.6)
    axes[0,3].set_xlabel('电压V (V)'); axes[0,3].set_ylabel('电流I (mA)'); axes[0,3].set_title('LED I-V特性曲线'); axes[0,3].legend(); axes[0,3].grid(True, alpha=0.3)

    # 子图5：光敏二极管 L-I
    axes[0,4].scatter(pd_L, pd_I_L, color='teal', label='实验数据')
    axes[0,4].plot(pd_L, pd_I_L, 'teal', alpha=0.6)
    axes[0,4].set_xlabel('照度L (Lx)'); axes[0,4].set_ylabel('电流I (μA)'); axes[0,4].set_title('光敏二极管光照特性曲线 (U=5V)'); axes[0,4].legend(); axes[0,4].grid(True, alpha=0.3)

    # 子图6：光敏二极管 V-I
    axes[1,0].scatter(pd_V, pd_I_V, color='brown', label='实验数据')
    axes[1,0].plot(pd_V, pd_I_V, 'brown', alpha=0.6)
    axes[1,0].set_xlabel('电压V (V)'); axes[1,0].set_ylabel('电流I (μA)'); axes[1,0].set_title('光敏二极管伏安特性曲线'); axes[1,0].legend(); axes[1,0].grid(True, alpha=0.3)

    # 子图7：光敏二极管 光谱
    axes[1,1].scatter(pd_wl, pd_I_wl, color='pink', label='实验数据')
    axes[1,1].plot(pd_wl, pd_I_wl, 'pink', alpha=0.6)
    axes[1,1].set_xlabel('波长λ (nm)'); axes[1,1].set_ylabel('电流I (μA)'); axes[1,1].set_title('光敏二极管光谱特性曲线 (30Lx)'); axes[1,1].legend(); axes[1,1].grid(True, alpha=0.3)

    # 子图8：光敏三极管 L-I
    axes[1,2].scatter(pt_L, pt_I_L, color='darkgreen', label='实验数据')
    axes[1,2].plot(pt_L, pt_I_L, 'darkgreen', alpha=0.6)
    axes[1,2].set_xlabel('照度L (Lx)'); axes[1,2].set_ylabel('电流I (mA)'); axes[1,2].set_title('光敏三极管光照特性曲线 (U=5V)'); axes[1,2].legend(); axes[1,2].grid(True, alpha=0.3)

    # 子图9：光敏三极管 V-I
    axes[1,3].scatter(pt_V, pt_I_V, color='darkblue', label='实验数据')
    axes[1,3].plot(pt_V, pt_I_V, 'darkblue', alpha=0.6)
    axes[1,3].set_xlabel('电压V (V)'); axes[1,3].set_ylabel('电流I (mA)'); axes[1,3].set_title('光敏三极管伏安特性曲线'); axes[1,3].legend(); axes[1,3].grid(True, alpha=0.3)

    # 子图10：光敏三极管 光谱
    axes[1,4].scatter(pt_wl, pt_I_wl, color='gray', label='实验数据')
    axes[1,4].plot(pt_wl, pt_I_wl, 'gray', alpha=0.6)
    axes[1,4].set_xlabel('波长λ (nm)'); axes[1,4].set_ylabel('电流I (mA)'); axes[1,4].set_title('光敏三极管光谱特性曲线 (30Lx)'); axes[1,4].legend(); axes[1,4].grid(True, alpha=0.3)

    plt.tight_layout()
    fpath, url = _save_fig(user_id, 'photo-devices', '光电器件性能曲线')
    return fpath, url


# -------------------------- 新增：太阳能电池特性 --------------------------
def plot_solar_cell(
    user_id: int,
    dark_voltage: List[float], dark_current: List[float],
    light_voltage: List[float], light_current: List[float],
    relative_intensity: List[float], light_power: List[float], short_circuit_current: List[float], open_circuit_voltage: List[float]
) -> List[Tuple[str, str]]:
    _set_chinese_font()
    results: List[Tuple[str, str]] = []

    # 图1：全暗伏安特性
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    dv = np.array(dark_voltage, dtype=float)
    dc = np.array(dark_current, dtype=float)
    plt.plot(dv, dc, 'b-o', linewidth=2, markersize=6, label='全暗伏安特性')
    plt.xlabel('外加偏压 (V)'); plt.ylabel('电流 (mA)'); plt.title('全暗情况下太阳能电池在外加偏压时的伏安特性曲线', fontweight='bold')
    plt.grid(True, alpha=0.3); plt.legend(fontsize=10); plt.tight_layout()
    results.append(_save_fig(user_id, 'solar-cell', '图1_全暗伏安'))

    # 图2：光照时输出伏安特性
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    lv = np.array(light_voltage, dtype=float)
    lc = np.array(light_current, dtype=float)
    plt.plot(lv, lc, 'r-o', linewidth=2, markersize=6, label='光照伏安特性')
    plt.xlabel('输出电压 (V)'); plt.ylabel('输出电流 (mA)'); plt.title('太阳能电池在光照时的输出伏安特性曲线', fontweight='bold')
    plt.grid(True, alpha=0.3); plt.legend(fontsize=10); plt.tight_layout()
    results.append(_save_fig(user_id, 'solar-cell', '图2_光照伏安'))

    # 共有数据
    ri = np.array(relative_intensity, dtype=float)
    lp = np.array(light_power, dtype=float)
    sci = np.array(short_circuit_current, dtype=float)
    ocv = np.array(open_circuit_voltage, dtype=float)

    # 图3：短路电流-相对光强
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    plt.plot(ri, sci, 'g-o', linewidth=2, markersize=6, label='短路电流-相对光强')
    plt.xlabel('相对光强'); plt.ylabel('短路电流 (mA)'); plt.title('太阳能电池短路电流与相对光强的关系曲线', fontweight='bold')
    plt.grid(True, alpha=0.3); plt.legend(fontsize=10); plt.tight_layout()
    results.append(_save_fig(user_id, 'solar-cell', '图3_短路电流相对光强'))

    # 图4：开路电压-相对光强
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    plt.plot(ri, ocv, 'm-o', linewidth=2, markersize=6, label='开路电压-相对光强')
    plt.xlabel('相对光强'); plt.ylabel('开路电压 (V)'); plt.title('太阳能电池开路电压与相对光强的关系曲线', fontweight='bold')
    plt.grid(True, alpha=0.3); plt.legend(fontsize=10); plt.tight_layout()
    results.append(_save_fig(user_id, 'solar-cell', '图4_开路电压相对光强'))

    # 图5：短路电流-光功率（线性拟合）
    def linear_func(x, a, b):
        return a * x + b
    params_i, _ = optimize.curve_fit(linear_func, lp, sci)
    a_i, b_i = float(params_i[0]), float(params_i[1])
    fit_i = linear_func(lp, a_i, b_i)
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    plt.scatter(lp, sci, c='blue', s=60, label='实验数据')
    plt.plot(lp, fit_i, 'r-', linewidth=2, label=f'拟合曲线: I = {a_i:.1f}P + {b_i:.2f}')
    plt.xlabel('光功率 (mW)'); plt.ylabel('短路电流 (mA)'); plt.title('太阳能电池短路电流与光功率的关系曲线（含拟合）', fontweight='bold')
    plt.grid(True, alpha=0.3); plt.legend(fontsize=10); plt.tight_layout()
    results.append(_save_fig(user_id, 'solar-cell', '图5_短路电流光功率'))

    # 图6：开路电压-光功率（对数拟合）
    def log_func(x, a, b):
        return a * np.log(x) + b
    params_v, _ = optimize.curve_fit(log_func, lp, ocv)
    a_v, b_v = float(params_v[0]), float(params_v[1])
    fit_v = log_func(lp, a_v, b_v)
    plt.figure(figsize=_new_fig_size_cm(20, 12))
    plt.scatter(lp, ocv, c='green', s=60, label='实验数据')
    plt.plot(lp, fit_v, 'orange', linewidth=2, label=f'拟合曲线: V = {a_v:.2f}ln(P) + {b_v:.2f}')
    plt.xlabel('光功率 (mW)'); plt.ylabel('开路电压 (V)'); plt.title('太阳能电池开路电压与光功率的关系曲线（含拟合）', fontweight='bold')
    plt.grid(True, alpha=0.3); plt.legend(fontsize=10); plt.tight_layout()
    results.append(_save_fig(user_id, 'solar-cell', '图6_开路电压光功率'))

    return results


# -------------------------- 新增：超声波实验（含自由落体/匀变速/牛顿第二定律） --------------------------
def plot_ultrasound(
    user_id: int,
    t_free_fall: List[float], v_free_fall_1: List[float], v_free_fall_2: Optional[List[float]], v_free_fall_3: Optional[List[float]], v_free_fall_4: Optional[List[float]],
    t1: List[float], v1_1: List[float], v1_2: List[float], v1_3: List[float], v1_4: List[float],
    t2: List[float], v2_1: List[float], v2_2: List[float], v2_3: List[float], v2_4: List[float],
    t3: List[float], v3_1: List[float], v3_2: List[float], v3_3: List[float], v3_4: List[float],
    m: List[float], a_measured: List[float]
) -> List[Tuple[str, str]]:
    _set_chinese_font()
    results: List[Tuple[str, str]] = []

    def linear_fit(x, y):
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        return float(slope), float(intercept), float(r_value**2)

    # 自由落体：使用可用的 1..4 组速度的平均值
    t_free = np.array(t_free_fall, dtype=float)
    v_groups = [np.array(v_free_fall_1, dtype=float)]
    for vg in [v_free_fall_2, v_free_fall_3, v_free_fall_4]:
        if vg is not None and len(vg) == len(t_free):
            v_groups.append(np.array(vg, dtype=float))
    v_avg = np.mean(np.stack(v_groups, axis=0), axis=0) if v_groups else np.array([], dtype=float)
    slope, intercept, r2 = linear_fit(t_free, v_avg)
    t_fit = np.linspace(float(np.min(t_free)), float(np.max(t_free)), 100)
    v_fit = slope * t_fit + intercept
    fig1, ax1 = plt.subplots(figsize=_new_fig_size_cm(20, 12))
    colors = ['blue','red','green','orange']
    for idx, vg in enumerate(v_groups):
        ax1.scatter(t_free, vg, label=f'第{idx+1}组数据', s=60, alpha=0.7, color=colors[idx % len(colors)])
    ax1.plot(t_fit, v_fit, 'k-', linewidth=2, label=f'拟合直线 (g={slope:.4f} m/s²)')
    ax1.set_xlabel('时间 t (s)'); ax1.set_ylabel('速度 v (m/s)'); ax1.set_title('自由落体运动速度-时间关系图', fontweight='bold')
    ax1.legend(fontsize=10); ax1.grid(True, alpha=0.3)
    ax1.text(0.05, 0.95, f'拟合方程: v = {slope:.4f}t + {intercept:.4f}\nR² = {r2:.6f}', transform=ax1.transAxes,
             fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    plt.tight_layout()
    results.append(_save_fig(user_id, 'ultrasound', '自由落体运动拟合图'))

    # 匀变速第1组
    def plot_uniform_group(t_arr, vs_arrs, group_idx: int):
        fig, ax = plt.subplots(figsize=_new_fig_size_cm(20, 12))
        colors = ['blue','red','green','orange']
        for i, v_arr in enumerate(vs_arrs):
            ax.scatter(t_arr, v_arr, label=f'第{i+1}次测量', s=50, alpha=0.7, color=colors[i % len(colors)])
        v_avg = np.mean(np.stack(vs_arrs, axis=0), axis=0)
        slope, intercept, r2 = linear_fit(t_arr, v_avg)
        t_fit = np.linspace(float(np.min(t_arr)), float(np.max(t_arr)), 100)
        v_fit = slope * t_fit + intercept
        ax.plot(t_fit, v_fit, 'k-', linewidth=2, label=f'拟合直线 (a={slope:.4f} m/s²)')
        ax.set_xlabel('时间 t (s)'); ax.set_ylabel('速度 v (m/s)'); ax.set_title(f'匀变速运动第{group_idx}组速度-时间关系图', fontweight='bold')
        ax.legend(fontsize=10); ax.grid(True, alpha=0.3)
        ax.text(0.05, 0.95, f'拟合方程: v = {slope:.4f}t + {intercept:.4f}\nR² = {r2:.6f}', transform=ax.transAxes,
                fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        plt.tight_layout()
        return _save_fig(user_id, 'ultrasound', f'匀变速第{group_idx}组拟合图')

    results.append(plot_uniform_group(np.array(t1, dtype=float), [np.array(v1_1, dtype=float), np.array(v1_2, dtype=float), np.array(v1_3, dtype=float), np.array(v1_4, dtype=float)], 1))
    results.append(plot_uniform_group(np.array(t2, dtype=float), [np.array(v2_1, dtype=float), np.array(v2_2, dtype=float), np.array(v2_3, dtype=float), np.array(v2_4, dtype=float)], 2))
    results.append(plot_uniform_group(np.array(t3, dtype=float), [np.array(v3_1, dtype=float), np.array(v3_2, dtype=float), np.array(v3_3, dtype=float), np.array(v3_4, dtype=float)], 3))

    # 牛顿第二定律验证图
    fig5, ax5 = plt.subplots(figsize=_new_fig_size_cm(20, 12))
    m_arr = np.array(m, dtype=float)
    a_arr = np.array(a_measured, dtype=float)
    slope_g, intercept_g, r2_g = linear_fit(m_arr, a_arr)
    m_fit = np.linspace(float(np.min(m_arr)), float(np.max(m_arr)), 100)
    a_fit = slope_g * m_fit + intercept_g
    ax5.scatter(m_arr, a_arr, s=100, color='red', alpha=0.8, label='实验数据点')
    ax5.plot(m_fit, a_fit, 'b-', linewidth=2, label=f'拟合直线 (斜率={slope_g:.2f})')
    ax5.set_xlabel('砝码质量 m (kg)'); ax5.set_ylabel('加速度 a (m/s²)'); ax5.set_title('牛顿第二定律验证图 (a - m 关系)', fontweight='bold')
    ax5.legend(fontsize=10); ax5.grid(True, alpha=0.3)
    ax5.text(0.05, 0.95, f'拟合方程: a = {slope_g:.2f}m + {intercept_g:.4f}\nR² = {r2_g:.6f}\n理论斜率 g = 9.8 m/s²', transform=ax5.transAxes,
             fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    plt.tight_layout()
    results.append(_save_fig(user_id, 'ultrasound', '牛顿第二定律验证图'))

    return results