from typing import Dict, Optional, List, Tuple
import uuid
from threading import Thread, Lock
import base64
from .plots import (
    plot_fiber_iu, plot_fiber_pi, plot_photodiode_iv,
    plot_frank_hertz, plot_millikan,
    plot_mech_t2_m, plot_mech_v2_x2,
    plot_thermal, plot_photo_devices, plot_solar_cell, plot_ultrasound,
)

class PlotTask:
    def __init__(self, user_id: int, experiment: str):
        self.task_id = uuid.uuid4().hex
        self.user_id = user_id
        self.experiment = experiment
        self.status = 'pending'
        self.images: List[str] = []
        self.images_data: Optional[List[str]] = None
        self.message: Optional[str] = None
        self.error: Optional[str] = None

TASKS: Dict[str, PlotTask] = {}
_lock = Lock()

def _save(task: PlotTask):
    with _lock:
        TASKS[task.task_id] = task

def start_fiber_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'fiber')
    _save(task)
    def run():
        try:
            imgs: List[str] = []
            imgs_data: List[str] = []
            if payload.plot_type == 'iu':
                fpath, url = plot_fiber_iu(user_id, payload.U, payload.I)
                imgs.append(url)
                if payload.return_data_uri:
                    with open(fpath, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            elif payload.plot_type == 'pi':
                fpath, url = plot_fiber_pi(user_id, payload.I, payload.P)
                imgs.append(url)
                if payload.return_data_uri:
                    with open(fpath, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            elif payload.plot_type == 'photodiode':
                fpath, url = plot_photodiode_iv(user_id, payload.V, payload.I0, payload.I1, payload.I2)
                imgs.append(url)
                if payload.return_data_uri:
                    with open(fpath, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = '生成完成'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id

def get_task_for_user(task_id: str, user_id: int) -> Optional[PlotTask]:
    with _lock:
        t = TASKS.get(task_id)
        if not t:
            return None
        if t.user_id != user_id:
            return None
        return t

def start_frank_hertz_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'frank-hertz')
    _save(task)
    def run():
        try:
            results = plot_frank_hertz(user_id, payload.VG2K if payload.VG2K else [float(i) for i in range(1, 83)], [(g.currents, g.label) for g in payload.groups])
            imgs = [u for _, u in results]
            imgs_data: List[str] = []
            if payload.return_data_uri:
                for fp, _ in results:
                    with open(fp, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = f'共生成{len(imgs)}张图像'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id

def start_thermal_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'thermal')
    _save(task)
    def run():
        try:
            temperatures = payload.temperatures if payload.temperatures else [55.0, 60.0, 65.0, 70.0, 75.0, 80.0]
            results = plot_thermal(user_id, temperatures, payload.pt100_resistance, payload.ntc_resistance)
            imgs = [u for _, u in results]
            imgs_data: List[str] = []
            if payload.return_data_uri:
                for fp, _ in results:
                    with open(fp, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = f'共生成{len(imgs)}张图像'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id

def start_photo_devices_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'photo-devices')
    _save(task)
    def run():
        try:
            fpath, url = plot_photo_devices(
                user_id,
                payload.led_I, payload.led_V, payload.led_P,
                payload.ld_I, payload.ld_V, payload.ld_P, payload.ld_linear_start_idx or 4,
                payload.pd_L, payload.pd_I_L, payload.pd_V, payload.pd_I_V, payload.pd_wl, payload.pd_I_wl,
                payload.pt_L, payload.pt_I_L, payload.pt_V, payload.pt_I_V, payload.pt_wl, payload.pt_I_wl
            )
            imgs = [url]
            imgs_data: List[str] = []
            if payload.return_data_uri:
                with open(fpath, 'rb') as f:
                    imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = '生成完成'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id

def start_solar_cell_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'solar-cell')
    _save(task)
    def run():
        try:
            results = plot_solar_cell(
                user_id,
                payload.dark_voltage, payload.dark_current,
                payload.light_voltage, payload.light_current,
                payload.relative_intensity, payload.light_power, payload.short_circuit_current, payload.open_circuit_voltage
            )
            imgs = [u for _, u in results]
            imgs_data: List[str] = []
            if payload.return_data_uri:
                for fp, _ in results:
                    with open(fp, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = f'共生成{len(imgs)}张图像'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id

def start_ultrasound_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'ultrasound')
    _save(task)
    def run():
        try:
            results = plot_ultrasound(
                user_id,
                payload.t_free_fall, payload.v_free_fall_1, payload.v_free_fall_2, payload.v_free_fall_3, payload.v_free_fall_4,
                payload.t1, payload.v1_1, payload.v1_2, payload.v1_3, payload.v1_4,
                payload.t2, payload.v2_1, payload.v2_2, payload.v2_3, payload.v2_4,
                payload.t3, payload.v3_1, payload.v3_2, payload.v3_3, payload.v3_4,
                payload.m, payload.a_measured
            )
            imgs = [u for _, u in results]
            imgs_data: List[str] = []
            if payload.return_data_uri:
                for fp, _ in results:
                    with open(fp, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = f'共生成{len(imgs)}张图像'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id

def start_millikan_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'millikan')
    _save(task)
    def run():
        try:
            fpath, url = plot_millikan(user_id, payload.ni, payload.qi)
            imgs = [url]
            imgs_data: List[str] = []
            if payload.return_data_uri:
                with open(fpath, 'rb') as f:
                    imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = '生成完成'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id

def start_mechanics_task(user_id: int, payload) -> str:
    task = PlotTask(user_id, 'mechanics')
    _save(task)
    def run():
        try:
            fpath1, url1, _k = plot_mech_t2_m(user_id, payload.t2m.m0_g, payload.t2m.weights_g, payload.t2m.T10_avg_s)
            fpath2, url2, _omega, _T_calc = plot_mech_v2_x2(user_id, payload.v2x2.x_cm, payload.v2x2.v_avg_cms)
            imgs = [url1, url2]
            imgs_data: List[str] = []
            if payload.return_data_uri:
                for fp in [fpath1, fpath2]:
                    with open(fp, 'rb') as f:
                        imgs_data.append('data:image/png;base64,' + base64.b64encode(f.read()).decode('utf-8'))
            task.images = imgs
            task.images_data = imgs_data if imgs_data else None
            task.status = 'completed'
            task.message = '生成完成'
        except Exception as e:
            task.status = 'failed'
            task.error = str(e)
            task.message = '生成失败'
        finally:
            _save(task)
    Thread(target=run, daemon=True).start()
    return task.task_id
