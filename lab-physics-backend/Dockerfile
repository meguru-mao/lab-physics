# FastAPI 后端 Dockerfile（适用于微信云托管构建）
# 基础镜像选择 Debian slim 以兼顾体积与科学计算库兼容性
FROM python:3.10-slim-bullseye

# 避免生成 .pyc，统一日志输出；设置 matplotlib 使用无头后端
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    RELOAD=0 \
    PORT=8000

# 工作目录
WORKDIR /app

# 可选：安装中文字体，避免生成图片中文乱码（如不需要可删除）
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk \
    fontconfig \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && fc-cache -f -v \
    && rm -rf /var/lib/apt/lists/*

# 提前复制依赖文件，利用缓存加速构建
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 复制后端全部代码
COPY . /app

# 暴露端口（云托管会将外部流量映射到该端口）
EXPOSE 8000

# 启动入口：以 server.py 为入口（内部使用 uvicorn 运行 app.main:app）
CMD ["python", "server.py"]