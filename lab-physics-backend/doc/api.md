# 接口文档（登录与实验绘图）

后端基础地址：

- 开发环境（默认）：`http://localhost:8000`
- 静态资源（图片预览）：`http://localhost:8000/static/...`

所有生成图像的接口均需要在请求头携带登录获得的 `Authorization: Bearer <token>`。

## 1. 健康检查

- 方法：GET `/api/ping`
- 响应：`{"message":"pong"}`

## 2. 微信登录（模拟可用）

- 方法：POST `/api/auth/wechat`
- 请求体：

```json
{ "code": "<wx.login 获取的 code，开发环境可传 DEV_CODE>" }
```

- 响应：

```json
{
  "token": "<JWT Token>",
  "user": { "user_id": 1, "openid": "mock_DEV_CODE", "role": "normal", "created_at": "2024-01-01T00:00:00" }
}
```

> 说明：开发环境或未配置 `WECHAT_APPID/WECHAT_APP_SECRET` 时会返回 mock openid，便于联调。

## 3. 光纤传感与通讯绘图

- 方法：POST `/api/plots/fiber`
- 请求头：`Authorization: Bearer <token>`
- 请求体（三选一）：

1) I-U 图
```json
{
  "plot_type": "iu",
  "U": [0, 0.75, 1.0, 1.1],
  "I": [0, 0.2, 5, 10]
}
```

2) P-I 图
```json
{
  "plot_type": "pi",
  "I": [0, 5, 10, 15],
  "P": [0, 0.001, 0.167, 0.411]
}
```

3) 光电二极管 I-V 图
```json
{
  "plot_type": "photodiode",
  "V": [0, 1, 2, 3, 4, 5],
  "I0": [0, 0, 0, 0, 0, 0],
  "I1": [98, 99, 99, 100, 98, 99],
  "I2": [200, 200, 199, 200, 200, 200]
}
```

- 响应：

```json
{ "images": ["/static/plots/<user_id>/fiber/<file>.png"], "message": "生成完成" }
```

## 4. 弗兰克-赫兹绘图

- 方法：POST `/api/plots/frank-hertz`
- 请求头：`Authorization: Bearer <token>`
- 请求体：

```json
{
  "VG2K": [1.0, 2.0, 3.0],
  "groups": [
    { "currents": [0.0, 0.014, 0.045], "label": "VG1=2.3V, VG2A=1.5V, VG2P=9V" },
    { "currents": [0.0, 0.010, 0.043], "label": "VG1=2.5V, VG2A=1.5V, VG2P=9V" }
  ]
}
```

> 说明：请求体中的 `VG2K` 可省略，后端将默认使用 1..82（浮点）作为 x 轴；此时每组 `currents` 需提供 82 项。

> 拟合方法：弗兰克-赫兹曲线使用 SciPy 的 `CubicSpline` 进行三次样条拟合，生成的图像与项目示例代码一致。

- 响应：

```json
{ "images": ["/static/plots/<user_id>/frank-hertz/<file1>.png", 
              "/static/plots/<user_id>/frank-hertz/<file2>.png"],
  "message": "共生成2张图像" }
```

> 说明：本实现使用多项式拟合近似样条平滑，无 SciPy 依赖，适合快速部署。

## 5. 密立根油滴绘图

- 方法：POST `/api/plots/millikan`
- 请求头：`Authorization: Bearer <token>`
- 请求体：

```json
{ "ni": [2, 2, 5, 6], "qi": [3.214, 3.191, 8.167, 9.302] }
```

- 响应：

```json
{ "images": ["/static/plots/<user_id>/millikan/<file>.png"], "message": "生成完成" }
```

## 6. 力学实验绘图（T²-M 与 v²-x²）

- 方法：POST `/api/plots/mechanics`
- 请求头：`Authorization: Bearer <token>`
- 请求体：

```json
{
  "t2m": {
    "m0_g": 241.68,
    "weights_g": [20, 40, 50, 70, 100],
    "T10_avg_s": [17.0158, 17.6387, 17.9340, 18.5316, 19.3818]
  },
  "v2x2": {
    "x_cm": [0, 4, 6, 8, 10, 12, 14, 16, 18],
    "v_avg_cms": [77.34, 72.47, 71.17, 69.17, 63.92, 57.30, 49.67, 41.67, 29.70]
  }
}
```

- 响应：

```json
{ "images": ["/static/plots/<user_id>/mechanics/<t2m_file>.png", 
              "/static/plots/<user_id>/mechanics/<v2x2_file>.png"],
  "message": "生成完成" }
```

---

### 统一错误响应格式

当请求参数缺失或校验失败时，返回：

```json
{ "detail": "错误原因说明" }
```

### 预览与下载

- 预览：前端直接使用 `<image src="http://localhost:8000/static/..." />` 或 H5 `<img />` 标签显示即可。
- 下载：
  - H5：使用 `<a href="..." download="...">` 或通过 `fetch + blob` 触发保存；
  - 微信小程序：`uni.downloadFile` + `wx.saveImageToPhotosAlbum` 保存到相册（需申请权限）。