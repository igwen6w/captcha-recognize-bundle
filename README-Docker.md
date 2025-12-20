# Docker 部署指南

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 使用 Docker 命令

```bash
# 构建镜像
docker build -t captcha-api:latest .

# 运行容器
docker run -d \
  --name captcha-api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/resources:/app/resources \
  -e JWT_SECRET_KEY=your-secret-key-here \
  captcha-api:latest
```

### 使用构建脚本

```bash
# 构建镜像（默认标签为 latest）
./docker-build.sh

# 构建指定标签
./docker-build.sh v1.0.0
```

## 环境变量

可以通过环境变量配置以下选项：

- `JWT_SECRET_KEY`: JWT 密钥（默认: your-secret-key-change-in-production）
- `PYTHONUNBUFFERED`: Python 输出缓冲（默认: 1）

## 数据持久化

容器会将以下目录挂载到宿主机：

- `./data`: 数据库文件（SQLite）
- `./resources`: 模型文件和资源

确保这些目录存在并有适当的权限。

## 健康检查

容器包含健康检查，可以通过以下命令查看：

```bash
docker ps
# 查看 STATUS 列中的健康状态
```

## 访问 API

容器启动后，可以通过以下地址访问：

- API 文档: http://localhost:8000/docs
- API 根路径: http://localhost:8000/
- 预测端点: http://localhost:8000/predict

## 故障排查

### 查看容器日志

```bash
# Docker Compose
docker-compose logs -f api

# Docker
docker logs -f captcha-api
```

### 进入容器调试

```bash
# Docker Compose
docker-compose exec api bash

# Docker
docker exec -it captcha-api bash
```

### 重建镜像

```bash
# Docker Compose
docker-compose build --no-cache

# Docker
docker build --no-cache -t captcha-api:latest .
```

## 生产环境建议

1. **设置强密码的 JWT_SECRET_KEY**
2. **使用反向代理**（如 Nginx）处理 HTTPS
3. **配置资源限制**（CPU、内存）
4. **设置日志轮转**
5. **定期备份数据库文件**

