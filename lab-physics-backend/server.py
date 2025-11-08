"""
后端启动入口（避免直接运行 app/main.py 导致相对导入错误）

用法：
  1) 开发环境：python3 server.py
  2) 或使用 uvicorn：uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

说明：
  - 该入口以包形式加载 app.main，从而保证相对导入（from .config 等）正常工作。
"""

import os
import uvicorn


def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "1") == "1"
    # 以包路径启动，确保相对导入不报错
    uvicorn.run("app.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    main()