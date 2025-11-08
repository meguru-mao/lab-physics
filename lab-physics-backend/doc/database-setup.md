# 数据库创建与接入完整指南（超详细，新手友好）

本项目后端（FastAPI + SQLAlchemy）支持两种数据库模式：

- 开发最快：SQLite（无需安装数据库服务，自动生成 `data/dev.sqlite`）
- 开发/生产：MySQL（推荐用于正式环境）

本文将一步步教你：

1. 使用 SQLite 作为开发数据库（最快上手）
2. 在 WSL 中安装与配置 MySQL，并创建数据库与用户（含所有命令）
3. 用 Navicat 连接 SQLite 或 WSL 的 MySQL（详细步骤）
4. 生产环境数据库搭建与上线思路（云数据库或自建 MySQL）
5. 常见问题排查与优化建议

---

## 0. 前置说明

- 后端代码路径：`e:\lab-physics\lab-physics\lab-physics-backend`
- 环境变量文件：`e:\lab-physics\lab-physics\lab-physics-backend\.env`
- 自动建表：后端在启动时会执行 `Base.metadata.create_all(bind=engine)`，即若数据库为空，会自动创建所需的表。
- 主要表结构（users）：
  - `user_id` INT 主键自增
  - `created_at` DATETIME 非空，默认当前时间（由应用侧或数据库侧设置）
  - `openid` VARCHAR(64) 非空唯一
  - `role` VARCHAR(20) 非空（默认 `normal`）

---

## 1. 开发环境最快上手：使用 SQLite

SQLite 是一个单文件数据库，最适合本地快速开发与联调，无需安装数据库服务。

步骤：

1) 确认 `.env` 未设置 `MYSQL_URL`（或者注释掉），这样后端会自动回退到 SQLite。

2) 启动后端（WSL 中执行）：

```bash
cd /mnt/e/lab-physics/lab-physics/lab-physics-backend
python3 server.py
```

3) 启动后会自动创建目录与数据库文件：`data/dev.sqlite`

4) 使用 SQLite 命令行查看表（WSL）：

```bash
sudo apt update
sudo apt install -y sqlite3

cd /mnt/e/lab-physics/lab-physics/lab-physics-backend
sqlite3 data/dev.sqlite

-- 在 sqlite3 交互环境中，输入：
.tables               -- 查看已有表
PRAGMA table_info(users); -- 查看 users 表结构
SELECT * FROM users;  -- 查看数据
.quit                 -- 退出
```

5) 用 Navicat 连接 SQLite（Windows）：

- 打开 Navicat -> 新建连接 -> 选择 “SQLite”
- 连接名任意（如：`lab_sqlite_dev`）
- 数据库文件选择：`e:\lab-physics\lab-physics\lab-physics-backend\data\dev.sqlite`
- 点击 “测试连接”，再保存 -> 即可浏览表与数据。

> 提示：SQLite 适用于本机开发与联调。正式上线建议使用 MySQL。

---

## 2. 在 WSL 中安装与配置 MySQL（开发/生产推荐）

以下步骤以 WSL Ubuntu 为例（其他发行版类似）。

### 2.1（可选）启用 systemd（便于使用 systemctl）

在较新版本 WSL 上可以启用 systemd：

```bash
sudo nano /etc/wsl.conf
```

填入以下内容并保存：

```
[boot]
systemd=true
```

重启 WSL：在 Windows PowerShell 中执行：

```powershell
wsl --shutdown
```

重新打开 WSL 终端。

### 2.2 安装 MySQL Server（WSL）

```bash
sudo apt update
sudo apt install -y mysql-server
```

检查并启动服务：

```bash
# 如果启用了 systemd：
sudo systemctl enable --now mysql
sudo systemctl status mysql

# 如果未启用 systemd：
sudo service mysql start
sudo service mysql status
```

### 2.3 安全初始化（设置 root 密码、清理匿名用户等）

```bash
sudo mysql_secure_installation
```

交互过程中推荐选择：

- 设置 root 密码：是
- 移除匿名用户：是
- 禁止 root 远程登录：是（安全起见）
- 移除测试数据库：是
- 重新加载权限表：是

### 2.4 调整字符集与监听地址（便于导航与中文支持）

编辑 MySQL 主配置：

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

在 `[mysqld]` 段添加/修改以下配置（若不存在则新增）：

```
bind-address = 0.0.0.0
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

保存后重启 MySQL：

```bash
sudo service mysql restart
# 或
sudo systemctl restart mysql
```

> 说明：`bind-address=0.0.0.0` 允许外部（包括 Windows 宿主机）连接到 WSL 中的 MySQL。若仅在 WSL 内连接可保持默认。

### 2.5 创建数据库与用户（含全部 SQL）

进入 MySQL：

```bash
mysql -u root -p
```

输入 root 密码后，执行以下 SQL：

```sql
-- 1) 创建数据库（使用 utf8mb4 避免中文或 Emoji 问题）
CREATE DATABASE lab_physics DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2) 创建专用应用用户（生产环境请使用更强的密码）
CREATE USER 'labuser'@'%' IDENTIFIED BY 'StrongPassword123!';

-- 3) 赋权（仅对 lab_physics 库）
GRANT ALL PRIVILEGES ON lab_physics.* TO 'labuser'@'%';
FLUSH PRIVILEGES;

-- 4) 可选：若你仅允许 Windows 宿主机访问，可根据实际 IP 限制：
-- CREATE USER 'labuser'@'172.%' IDENTIFIED BY 'StrongPassword123!';
-- GRANT ALL PRIVILEGES ON lab_physics.* TO 'labuser'@'172.%';
-- FLUSH PRIVILEGES;
```

退出：

```sql
EXIT;
```

> 提示：应用启动时会自动建表，无需手动执行建表 SQL。但如需手动建表，见下文「附录：手动建表 SQL」。

### 2.6 获取 WSL 的 IP（供 Navicat 或后端使用）

```bash
hostname -I
# 或
ip addr show eth0 | grep 'inet '
```

记下形如 `172.xx.xx.xx` 的地址（WSL2 的 IP 在每次重启后可能变化）。

### 2.7 配置后端连接 MySQL（修改 .env）

编辑 `e:\lab-physics\lab-physics\lab-physics-backend\.env`，新增/修改：

```
MYSQL_URL=mysql+pymysql://labuser:StrongPassword123!@<WSL_IP>:3306/lab_physics?charset=utf8mb4
```

例如：

```
MYSQL_URL=mysql+pymysql://labuser:StrongPassword123!@172.24.32.10:3306/lab_physics?charset=utf8mb4
```

保存后，重启后端服务：

```bash
cd /mnt/e/lab-physics/lab-physics/lab-physics-backend
python3 server.py
```

第一次启动时，后端会自动在 `lab_physics` 数据库中创建所需表。

### 2.8 用 Navicat 连接 WSL 的 MySQL（Windows）

1) 打开 Navicat -> 新建连接 -> 选择 “MySQL”。

2) 按以下信息填写：

- 连接名：`lab_mysql_dev`
- 主机：填写上一步获取的 WSL IP（如：`172.24.32.10`）
- 端口：`3306`
- 用户名：`labuser`
- 密码：`StrongPassword123!`

3) 点击 “测试连接”，若成功则保存连接并打开库 `lab_physics` -> 浏览 `users` 表。

若连接失败，排查：

- 确认 MySQL 已启动：`sudo service mysql status`
- 确认 MySQL 正在监听端口：`sudo netstat -tlnp | grep 3306`
- 确认 `mysqld.cnf` 的 `bind-address` 为 `0.0.0.0` 并已重启服务
- WSL IP 每次重启可能变化，重新获取并更新 Navicat 配置
- 如报 `Access denied`，检查用户/主机匹配与权限（`SELECT host,user FROM mysql.user;`）

> 可选：为了避免 WSL IP 变化影响连接，可在 Windows 设置端口转发：

```powershell
# 在 Windows PowerShell 中执行，将本机 127.0.0.1:3306 转发到当下 WSL IP（需替换为实际 WSL_IP）
netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=3306 connectaddress=<WSL_IP> connectport=3306

# 查看已配置的转发
netsh interface portproxy show v4tov4
```

之后 Navicat 主机可填写 `127.0.0.1`，但注意：每次 WSL IP 变化后需更新该端口转发规则。

---

## 3. 附录：手动建表 SQL（MySQL）

若你希望手动创建 `users` 表（一般不需要，因为应用会自动建表）：

```sql
USE lab_physics;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  openid VARCHAR(64) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'normal',
  UNIQUE KEY uq_user_openid (openid),
  KEY idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

> 注意：ORM 模型中 `created_at` 默认值由应用侧设置为 `datetime.utcnow()`；如果你使用数据库侧默认 `CURRENT_TIMESTAMP`，也完全可行，二者效果一致。

---

## 4. 生产环境数据库上线方案

生产建议使用云数据库或云主机自建 MySQL。下面给出两种方案：

### 方案 A：云数据库（推荐，如腾讯云 MySQL / 阿里云 RDS）

1) 在云厂商控制台创建 MySQL 实例（选择公网访问或通过同 VPC 内访问）。
2) 创建数据库与用户：

```sql
CREATE DATABASE lab_physics DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'labuser'@'%' IDENTIFIED BY '更强的生产密码';
GRANT ALL PRIVILEGES ON lab_physics.* TO 'labuser'@'%';
FLUSH PRIVILEGES;
```

3) 在实例安全组/白名单中，放行你的后端服务器出口 IP（或云托管所在网络）。
4) 在后端生产环境的 `.env`（或云托管环境变量）中设置：

```
MYSQL_URL=mysql+pymysql://labuser:生产密码@云数据库地址:3306/lab_physics?charset=utf8mb4
WECHAT_MOCK=0
CORS_ORIGINS=https://你的前端正式域名
```

5) 启动后端，应用会自动建表。Navicat 使用云数据库地址连接即可。

### 方案 B：云主机自建 MySQL（Ubuntu）

1) 购买云服务器（Ubuntu），安全组开放 3306/TCP。
2) SSH 登录云服务器，安装 MySQL：

```bash
sudo apt update
sudo apt install -y mysql-server
sudo systemctl enable --now mysql
```

3) 配置字符集与监听地址：编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`，设置：

```
bind-address = 0.0.0.0
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci
```

并重启：

```bash
sudo systemctl restart mysql
```

4) 初始化数据库与用户（参考 2.5 的 SQL）。
5) 在后端 `.env` 配置 `MYSQL_URL` 指向云主机地址，启动后端自动建表。

### 生产补充建议

- 禁止 root 远程登录，仅使用业务账号（如 `labuser`）。
- 开启自动备份：示例命令（在 Linux 上定时执行）：

```bash
mysqldump -h <DB_HOST> -u labuser -p'生产密码' --databases lab_physics \
  --routines --events --triggers \
  --set-gtid-purged=OFF \
  | gzip > /path/to/backup/lab_physics_$(date +%F).sql.gz
```

- 数据库只开放给后端所在网络（VPC/白名单），不要直接暴露到全网。
- 后端连接建议开启长连接池（SQLAlchemy 默认即可），避免频繁连接。
- 若未来表结构演进，建议引入迁移工具 Alembic。

---

## 5. 常见问题排查（FAQ）

1) Navicat 连接 WSL MySQL 报错 “Can't connect”
   - 检查 MySQL 服务是否启动：`sudo service mysql status`
   - 检查端口监听：`sudo netstat -tlnp | grep 3306`
   - 检查 `bind-address` 是否为 `0.0.0.0`，修改后重启服务
   - 重新获取 WSL IP：`hostname -I`，并在 Navicat 中更新主机地址

2) 报错 “Access denied for user”
   - 确认用户是否创建在正确的 host 模式（`'%'` 或具体网段）
   - 查看用户列表：`SELECT host,user FROM mysql.user;`
   - 重新赋权并执行 `FLUSH PRIVILEGES;`

3) 中文或 Emoji 显示为问号
   - 确认库/表/连接均使用 `utf8mb4`
   - 配置 `character-set-server = utf8mb4` 与 `collation-server = utf8mb4_unicode_ci`

4) 开发时手机/真机无法访问本机数据库
   - 手机与电脑必须在同一局域网，且数据库必须允许局域网访问（安全风险大，不建议）
   - 开发期建议模拟器 + SQLite 或云数据库临时实例
   - 正式环境使用云数据库，并通过后端 API 访问数据库，不让前端直接连库

---

## 6. 后端配置速查

编辑 `e:\lab-physics\lab-physics\lab-physics-backend\.env`，根据环境选择：

开发（SQLite）：

```
# 不设置 MYSQL_URL，自动回退到 SQLite
SQLITE_URL=sqlite:///./data/dev.sqlite
CORS_ORIGINS=http://localhost:5173
WECHAT_MOCK=1
```

开发/生产（MySQL）：

```
MYSQL_URL=mysql+pymysql://labuser:StrongPassword123!@<HOST>:3306/lab_physics?charset=utf8mb4
CORS_ORIGINS=http://localhost:5173,https://你的前端正式域名
WECHAT_MOCK=0
```

启动后端（WSL）：

```bash
cd /mnt/e/lab-physics/lab-physics/lab-physics-backend
python3 server.py
```

测试接口：

```bash
curl http://localhost:8000/api/ping
curl -X POST http://localhost:8000/api/auth/wechat -H 'Content-Type: application/json' -d '{"code":"DEV_CODE"}'
```

---

如需我协助将生产环境迁移到云数据库（或加上 Alembic 迁移与备份脚本），告诉我你的云厂商与计划上线时间，我可以继续帮你完成后续步骤。