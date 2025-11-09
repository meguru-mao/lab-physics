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
def plot_fiber_iu(user_id: int, U: List[float], I: List[float]) -> str:
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
    _, url = _save_fig(user_id, 'fiber', 'I-U')
    return url


def plot_fiber_pi(user_id: int, I: List[float], P: List[float]) -> str:
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
    _, url = _save_fig(user_id, 'fiber', 'P-I')
    return url


def plot_photodiode_iv(user_id: int, V: List[float], I0: List[float], I1: List[float], I2: List[float]) -> str:
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
    _, url = _save_fig(user_id, 'fiber', 'photodiode-IV')
    return url


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


def plot_frank_hertz(user_id: int, VG2K: List[float], groups: List[Tuple[List[float], str]]) -> List[str]:
    _set_chinese_font()
    urls: List[str] = []
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
        _, url = _save_fig(user_id, 'frank-hertz', f'frank_group{idx}')
        urls.append(url)
    return urls


# -------------------------- 密里根油滴 --------------------------
def plot_millikan(user_id: int, ni: List[float], qi: List[float]) -> str:
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
    _, url = _save_fig(user_id, 'millikan', 'millikan_qi_ni')
    return url


# -------------------------- 力学实验 --------------------------
def plot_mech_t2_m(user_id: int, m0_g: float, weights_g: List[float], T10_avg_s: List[float]) -> Tuple[str, float]:
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
    _, url = _save_fig(user_id, 'mechanics', 'mech_T2_M')
    return url, k


def plot_mech_v2_x2(user_id: int, x_cm: List[float], v_avg_cms: List[float]) -> Tuple[str, float, float]:
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
    _, url = _save_fig(user_id, 'mechanics', 'mech_v2_x2')
    return url, omega, T_calc