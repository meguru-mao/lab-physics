# lab-physics-backend

本后端采用 FastAPI + SQLAlchemy + PyMySQL 搭建，负责微信登录与后续实验图像接口。

## 运行步骤（开发环境）

1. 安装依赖：
   - Windows PowerShell：
   - `pip install -r requirements.txt`

2. 配置环境变量（推荐复制 `.env.example` 为 `.env` 并填写）：
   - `WECHAT_APPID` 与 `WECHAT_APP_SECRET`：微信小程序的 AppID/Secret
   - `MYSQL_URL`：`mysql+pymysql://<user>:<pass>@localhost:3306/lab_physics?charset=utf8mb4`
   - `JWT_SECRET`：任意随机字符串
   - `CORS_ORIGINS`：前端H5调试地址，默认 `http://localhost:5173`
   - 本地无 MySQL 时，暂可不设置 `MYSQL_URL`，后端将回退到 `sqlite:///./data/dev.sqlite` 以便启动与调试。

3. 启动服务：
   - `uvicorn app.main:app --reload --port 8000`
   - 浏览器打开 `http://localhost:8000/docs` 查看接口文档。

## 生成并配置 JWT_SECRET（非常重要）

JWT_SECRET 用于签发和校验 JWT 令牌，必须是一个高强度随机字符串。推荐以下任一方式生成，然后写入 `.env`：

- Python（Windows PowerShell）
  - `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- Node.js
  - `node -e "console.log(require('crypto').randomBytes(48).toString('hex'))"`
- OpenSSL（如已安装）
  - `openssl rand -hex 48`

将生成的字符串复制到 `.env` 中：

```
JWT_SECRET=粘贴你生成的随机字符串
```

修改后无需重启数据库，但需要重启后端服务使配置生效。

## 数据库结构

仅需一个用户信息表（user_info）：

- `user_id`：主键，自增
- `created_at`：创建时间
- `openid`：微信用户 openid，唯一
- `role`：用户权限（`normal` 或 `admin`）

表结构在 `app/models.py` 中定义，应用启动时自动创建（不存在则创建）。若历史版本存在旧表名 `users`，应用会在启动时自动将其重命名为 `user_info`。

## MySQL 数据库创建详解

你可以按以下步骤在本机或服务器上创建数据库和用户（以 MySQL 8 为例）：

1. 创建数据库与用户（在 MySQL 客户端执行）

```
-- 登录 MySQL（根据你的安装选择命令或图形工具）
-- 创建数据库
CREATE DATABASE lab_physics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并设置密码（请替换 your_password）
CREATE USER 'lab_user'@'localhost' IDENTIFIED BY 'your_password';

-- 授权用户对数据库的全部权限
GRANT ALL PRIVILEGES ON lab_physics.* TO 'lab_user'@'localhost';
FLUSH PRIVILEGES;
```

2. 在 `.env` 配置 MySQL 连接地址（示例）：

```
MYSQL_URL=mysql+pymysql://lab_user:your_password@localhost:3306/lab_physics?charset=utf8mb4
```

3. 初始化数据表（两种方式）

- 方式 A：直接运行项目，SQLAlchemy 会在启动时自动创建表结构：
  - `uvicorn app.main:app --reload --port 8000`
- 方式 B：手动执行 SQL 文件（可选）：
  - 将 `db/mysql_schema.sql` 导入到数据库（使用 MySQL 客户端或图形工具），该文件包含 `users` 表的建表语句。

4. 验证数据库连接

- 启动后端，并观察启动日志中是否出现“Connected to MySQL”或无错误信息；
- 打开 `http://127.0.0.1:8000/docs`，调用 `/api/ping` 接口确认服务正常；
- 登录流程会在第一次使用时自动写入一条用户记录，可在数据库中查询：

```
SELECT user_id, created_at, openid, role FROM users LIMIT 10;
```

5. 生产环境建议

- 使用强密码与只授予必要权限的数据库用户；
- 配置数据库备份与监控；
- 将 `.env` 放在安全位置，不要提交到版本库；
- 在反向代理（如 Nginx）层启用 HTTPS 与必要的访问控制。

## 微信登录说明

前端通过 `uni.login` 拿到临时码 `code`，POST 到后端 `/api/auth/wechat`。
后端调用微信官方接口 `https://api.weixin.qq.com/sns/jscode2session` 获取 `openid`，若用户不存在则创建，并返回签发的 JWT 令牌和用户信息。

开发阶段可设置 `WECHAT_MOCK=1`，使用 `code` 生成模拟 `openid`，便于在H5或无真实小程序环境时联调。