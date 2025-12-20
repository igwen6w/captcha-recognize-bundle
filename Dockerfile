# 使用 Python 3.12 作为基础镜像
FROM python:3.12-slim as base

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 设置环境变量
ENV UV_SYSTEM_PYTHON=1 \
    UV_NO_CACHE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# 复制依赖文件（利用 Docker 缓存层）
COPY pyproject.toml uv.lock ./

# 安装依赖（这层会被缓存，除非依赖文件改变）
RUN uv sync --frozen --no-dev

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p data resources

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# 运行应用
CMD ["uv", "run", "python", "main.py"]

