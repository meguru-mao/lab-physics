# Lab Physics 物理实验平台

本项目旨在为大学物理实验提供统一的前后端支撑：
- 前端（H5/多端）用于实验流程展示、数据录入与图像/曲线可视化。
- 后端（FastAPI）提供实验数据管理、计算分析与接口服务。

## 目标与特色
- 覆盖常见物理实验模块（力学、热学、光学/光电、声学等）。
- 统一的数据结构与 API，便于扩展新实验项目与复用算法。
- 前端采用 Vue3 + Vite + Uni-App 插件，支持 H5 与小程序（需 HBuilderX 编译）。
- 后端采用 FastAPI，结合 NumPy/Matplotlib/SciPy 等科学计算库进行分析与绘图。

## 项目结构
```
lab-physics/
  ├─ lab-physics-frontend/     # 前端（Vue3 + Vite + Uni-App）
  │  ├─ pages/                 # 页面与路由（Uni-App）
  │  ├─ static/                # 静态资源
  │  ├─ utils/                 # 工具函数
  │  ├─ manifest.json          # Uni-App 应用配置
  │  ├─ pages.json             # 页面路由与窗口配置
  │  ├─ vite.local.config.js   # 本地 Vite 配置（H5 开发）
  │  └─ package.json           # 前端依赖与脚本
  ├─ lab-physics-backend/      # 后端（FastAPI）
  │  ├─ app/                   # FastAPI 应用代码（路由、模型、服务等）
  │  ├─ db/                    # 数据库相关（连接、迁移等）
  │  ├─ data/                  # 示例/临时数据（已在 .gitignore 中忽略）
  │  ├─ server.py              # 后端入口（uvicorn 启动 app.main:app）
  │  ├─ requirements.txt       # 后端依赖
  │  └─ Dockerfile             # 后端容器构建文件
  └─ .gitignore                # 已配置忽略 node_modules、dist、build、unpackage 等
```

## 运行环境
- Node.js ≥ 18（Vite 6 推荐），npm ≥ 9（仓库存在 package-lock.json，建议使用 npm）。
- Python ≥ 3.10（科学计算库版本与 Dockerfile 对齐）。
- 可选：Docker（用于后端容器化部署）。

## 快速开始（开发环境）

### 启动后端（FastAPI）
1. 切换到后端目录：
   ```bash
   cd lab-physics-backend
   ```
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置环境变量（复制示例并按需修改）：
   ```bash
   copy .env.example .env  # Windows
   # 或
   cp .env.example .env    # macOS/Linux
   ```
4. 启动开发服务：
   ```bash
   python server.py
   # 或
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. 默认后端地址：http://localhost:8000

### 启动前端（H5 开发）
1. 切换到前端目录并安装依赖：
   ```bash
   cd lab-physics-frontend
   npm install
   ```
2. 启动 H5 开发服务器（Vite，默认端口 5173）：
   ```bash
   npm run dev:h5
   ```
3. 访问：http://localhost:5173

> 说明：当前 package.json 提供 H5 脚本（dev:h5 / build:h5）。如需编译到小程序或 App，请使用 HBuilderX 打开前端工程并按 Uni-App 官方流程编译。

## 构建与部署

### 前端（H5）
1. 构建：
   ```bash
   cd lab-physics-frontend
   npm run build:h5
   ```
2. 构建产物位于 `lab-physics-frontend/dist/`，可通过任意静态服务器/容器/Nginx 部署。
3. 示例：使用 `serve` 快速预览静态文件：
   ```bash
   npx serve -s dist -p 8080
   ```
4. Nginx 典型配置（前端为单页应用，后端反向代理至 8000）：
   ```nginx
   server {
     listen 80;
     server_name your-domain;

     root /var/www/lab-physics-frontend/dist;
     index index.html;

     location / {
       try_files $uri $uri/ /index.html;
     }

     location /api/ {
       proxy_pass http://backend:8000/;  # 请按实际后端地址修改
       proxy_http_version 1.1;
       proxy_set_header Upgrade $http_upgrade;
       proxy_set_header Connection "upgrade";
       proxy_set_header Host $host;
     }
   }
   ```

### 后端（Docker 部署）
1. 进入后端目录：
   ```bash
   cd lab-physics-backend
   ```
2. 构建镜像：
   ```bash
   docker build -t lab-physics-backend:latest .
   ```
3. 运行容器（映射端口并加载环境变量）：
   ```bash
   docker run -d --name lab-physics-api -p 8000:8000 --env-file .env lab-physics-backend:latest
   ```
4. 后端将监听 8000 端口，内部通过 `server.py` 启动 `uvicorn app.main:app`。

## 环境变量与配置
- 后端 `.env`：请参考 `lab-physics-backend/.env.example`，通常包含数据库连接、JWT 密钥、CORS 允许来源等。
- 前端多端配置：`manifest.json`（应用信息）与 `pages.json`（页面路由）。H5 端开发使用 `vite.local.config.js`（端口 5173）。

## 常见问题
- 若出现 JSON 文件语法飘红，请确保 `manifest.json`、`pages.json` 不包含注释（或在编辑器中将其关联为 JSONC）。
- 科学计算库在部分平台可能需要系统依赖（如字体/图形库）。Dockerfile 已包含中文字体安装，部署时可按需调整。

## 许可
- 本仓库遵循MIT开源许可，未经授权严禁任何商业用途
- 由错误使用或滥用造成的学术问题与作者本人无关

## 贡献
欢迎提交 Issue 与 Pull Request。建议在提交前：
- 为新增实验模块补充对应的文档说明与示例数据。
- 尽量保持代码风格一致。
- 前端构建产物与依赖目录请勿提交至仓库。
