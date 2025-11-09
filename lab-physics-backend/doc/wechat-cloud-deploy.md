# 微信云托管部署指南（FastAPI 后端，WSL + Docker）

本文面向没有 Docker 经验的初学者，手把手教你将本项目后端部署到「微信云托管」。所有命令均给出在 WSL(Ubuntu) 下的实际可执行形式。

本项目后端位置：`/mnt/e/lab-physics/lab-physics/lab-physics-backend`（Windows 路径 `e:\lab-physics\lab-physics\lab-physics-backend`）

---

## 1. 前置准备

1) 注册并开通「微信云托管」
- 在微信公众平台创建小程序，并在「云开发/云托管」中开通「云托管」。
- 记下你的小程序 `AppID`（后端将使用）。

2) 准备 WSL 与 Docker 环境
- Windows 下安装 WSL（推荐 Ubuntu）：
  - 管理员 PowerShell：`wsl --install -d Ubuntu`
- 安装 Docker（推荐 Docker Desktop 并开启 WSL 集成）：
  - https://www.docker.com/products/docker-desktop/
  - 安装后在 Docker Desktop 设置里启用「WSL Integration」并选择 Ubuntu。
- 在 WSL(Ubuntu) 验证 docker 是否可用：
  ```bash
  docker version
  docker info
  ```
  若提示权限问题，重启 Docker Desktop 或 WSL，再执行一次。

3) 准备数据库（生产）
- 生产环境推荐使用云 MySQL（腾讯云或其他云服务），拿到连接串：
  `mysql+pymysql://<user>:<pass>@<host>:3306/lab_physics?charset=utf8mb4`
- 若暂时无 MySQL，后端会自动使用 SQLite（仅适合开发，不建议正式使用）。

---

## 2. 后端运行与环境变量

项目后端（FastAPI）读取以下环境变量：
- `WECHAT_APPID`：小程序 AppID
- `WECHAT_APP_SECRET`：小程序 Secret（生产环境必须设置，避免使用 mock）
- `MYSQL_URL`：MySQL 连接串（生产环境建议设置，避免 SQLite）
- `JWT_SECRET`：任意强随机字符串（用于签名 Token）
- `CORS_ORIGINS`：H5 调试或正式域名（如有 H5 入口，否则可留默认）
- `WECHAT_MOCK`：生产设为 `0`，开发可设为 `1` 以模拟登录
- `PORT`：服务监听端口，默认 `8000`

静态资源说明：后端挂载了 `/static` 指向容器内工作目录下的 `data`，所有生成的图片保存在 `data/plots/...`。生产环境需要给 `data` 挂载持久化存储，以避免容器重启后数据丢失（见第 6 步）。

---

## 3. 准备 Docker 文件（在后端根目录）

在 `e:\lab-physics\lab-physics\lab-physics-backend` 目录新建 `Dockerfile`（名字严格大小写一致），内容如下：

```Dockerfile
# 使用 Debian bullseye 的 Python 镜像，兼顾体积与科学计算库兼容性
FROM python:3.10-slim-bullseye

# 避免 Python 生成 .pyc 文件，统一日志
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 工作目录
WORKDIR /app

# 可选：安装中文字体，避免图像中文乱码（如不需要可删除）
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件（仅后端）
COPY . /app

# 安装依赖（包含 numpy、matplotlib、scipy 等）
RUN pip install --no-cache-dir -r requirements.txt

# 容器对外暴露端口（云托管会将外部流量映射到这里）
EXPOSE 8000

# 默认启动：使用 server.py（内部调用 uvicorn 启动 app.main:app）
ENV PORT=8000
CMD ["python", "server.py"]
```

推荐同时新建 `.dockerignore`（减少镜像体积）：

```gitignore
# 忽略本地临时文件与数据文件
__pycache__/
*.log
*.tmp
*.sqlite
.env
.env.*
.data
venv/
.venv/
.data/
data/
.git/
```

---

## 4. 在 WSL 中构建镜像

进入后端目录（WSL 路径）：
```bash
cd /mnt/e/lab-physics/lab-physics/lab-physics-backend
```

构建镜像：
```bash
# 给镜像起一个本地名称（可自定义）
docker build -t lab-physics-backend:prod .
```

查看本地镜像：
```bash
docker images | grep lab-physics-backend
```

本地测试运行（可选）：
```bash
# 注意：仅测试后端是否能启动；实际云托管会用到云数据库、域名等。
docker run --rm -p 8000:8000 \
  -e WECHAT_MOCK=1 \
  -e JWT_SECRET="ChangeMeStrongSecret" \
  -e CORS_ORIGINS="http://localhost:5173" \
  lab-physics-backend:prod
# 打开 http://localhost:8000/docs 或 curl http://localhost:8000/api/ping
```

---

## 5. 推送镜像到微信云托管

「微信云托管」会在控制台为你创建一个「容器镜像仓库」（TCR）。不同账号/环境的仓库地址不同，请按控制台提示为准。典型地址类似：
```
<REGISTRY>/<NAMESPACE>/<REPO>:<TAG>
```

示例步骤（在 WSL 中执行）：
```bash
# 1) 控制台获取仓库地址与登录指令（包含 REGISTRY 与用户名/密码），然后在 WSL 登录：
# 例如：docker login ccr.ccs.tencentyun.com -u <USERNAME> -p <PASSWORD>
docker login <REGISTRY> -u <USERNAME> -p <PASSWORD>

# 2) 给本地镜像打上远端标签（按控制台给出的完整路径）
docker tag lab-physics-backend:prod <REGISTRY>/<NAMESPACE>/<REPO>:v1

# 3) 推送到云托管镜像仓库
docker push <REGISTRY>/<NAMESPACE>/<REPO>:v1
```

推送成功后，在微信云托管控制台的镜像仓库页面可以看到新镜像版本。

---

## 6. 在微信云托管控制台创建服务

1) 创建服务（选择「从镜像部署」）
- 服务名：`lab-physics-backend`
- 部署来源：选择刚才推送的镜像（`<REGISTRY>/<NAMESPACE>/<REPO>:v1`）
- 端口：`8000`（与 Dockerfile 中 `EXPOSE 8000`、应用的 `PORT` 一致）

2) 环境变量（按需填写）
- `WECHAT_APPID`：小程序 AppID
- `WECHAT_APP_SECRET`：小程序 Secret
- `MYSQL_URL`：`mysql+pymysql://<user>:<pass>@<host>:3306/lab_physics?charset=utf8mb4`
- `JWT_SECRET`：强随机字符串
- `CORS_ORIGINS`：如 `https://你的正式域名`
- `WECHAT_MOCK`：`0`
- `PORT`：`8000`

3) 存储卷挂载（保证生成图片持久化）
- 在「云托管 -> 存储/磁盘」创建一个「数据卷」，大小 1~10GB（视需求）。
- 在服务的「挂载配置」中将该数据卷挂载到容器路径：`/app/data`
  - 这样后端中的 `/static`（指向 `data`）会映射到持久化存储。

4) 并发与伸缩（可选）
- 初始实例数：1
- 资源规格：根据预算与压力选择（小规格即可）
- 自动伸缩：可先关闭，后续根据访问量再开启。

5) 启动服务
- 点击「部署/发布」，等待实例启动成功。
- 在服务详情中可以看到「外网访问地址」。

---

## 7. 小程序合法域名与联调

1) 在小程序后台（公众平台）中配置「request 合法域名」：
- 将云托管服务的外网地址（如 `https://<your-wx-cloud-domain>`）加入合法域名列表。

2) 前端联调时（如 H5 Vite），在 `.env.production` 或运行时填入后端地址：
- `VITE_API_BASE_URL=https://<your-wx-cloud-domain>`
- 后端 `CORS_ORIGINS` 中也需包含该域名。

---

## 8. 部署后自检（WSL 命令）

```bash
# 替换为你的云托管服务外网地址
BASE=https://<your-wx-cloud-domain>

# 1) 健康检查
curl -s $BASE/api/ping

# 2) 登录流程（开发可使用 mock 登录）
# 注意：生产环境 WECHAT_MOCK=0 时需要从小程序端获取 code 后再调用
curl -s -X POST $BASE/api/auth/wechat -H 'Content-Type: application/json' \
  -d '{"code":"DEV_CODE"}'

# 3) 访问文档（浏览器）
# 打开：$BASE/docs
```

---

## 9. 常见问题排查（FAQ）

1) 服务启动失败
- 检查环境变量是否完整（尤其是 `WECHAT_APP_SECRET`、`JWT_SECRET`）。
- 查看服务日志（控制台），确认端口是否为 `8000`，并且应用没有报错。

2) 生成图片无法持久化
- 确认数据卷已挂载到 `/app/data`，并且容器有写入权限。
- 若忘记挂载，容器重启后图片会丢失。

3) SciPy/Matplotlib 安装失败
- 使用 `python:3.10-slim-bullseye` 可大概率直接安装 wheel；仍失败可改用 `python:3.10`（非 slim）或在 Dockerfile 中增加必要系统库。
- 中文字体显示异常时，在 Dockerfile 中安装 `fonts-noto-cjk` 并在后端采用字体回退（本项目已处理）。

4) 接口跨域（CORS）问题
- 小程序端一般不受 CORS 限制，但 H5 端需设置后端 `CORS_ORIGINS` 包含你的前端域名。

5) MySQL 连接失败
- 检查云数据库安全组/白名单是否允许云托管出口 IP。
- 在 `MYSQL_URL` 中确保字符集为 `charset=utf8mb4`。

6) 静态资源访问路径 404
- 确认服务已挂载 `/static` 到容器内 `data/`（本项目通过 FastAPI 的 StaticFiles 已挂载）。
- 访问示例：`https://<your-wx-cloud-domain>/static/plots/<user_id>/<experiment>/<file>.png`

---

## 10. 更新与回滚

1) 在 WSL 中重新构建新版本镜像：
```bash
cd /mnt/e/lab-physics/lab-physics/lab-physics-backend
# 修改代码后重新构建
docker build -t lab-physics-backend:prod .
```

2) 推送新 tag：
```bash
docker tag lab-physics-backend:prod <REGISTRY>/<NAMESPACE>/<REPO>:v2
docker push <REGISTRY>/<NAMESPACE>/<REPO>:v2
```

3) 在云托管控制台切换部署版本到 `v2`，观察服务健康后再删除旧版本。

4) 回滚：若新版本异常，可快速切回旧版本 `v1`。

---

## 11. 小结与建议

- 生产环境务必使用 MySQL，并将 `WECHAT_MOCK` 设为 0。
- 为避免生成图片丢失，必须挂载持久化存储到 `/app/data`。
- 部署前最好在本地使用 Docker 运行一次，确保镜像可正常启动。
- 遇到问题优先查看服务日志与镜像构建日志，定位错误后再调整。

祝部署顺利！如需我为你生成 Dockerfile 或协助在控制台创建服务和挂载，请告诉我你的云托管控制台信息（仓库地址、服务名等）。