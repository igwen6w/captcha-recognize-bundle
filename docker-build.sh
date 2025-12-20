#!/bin/bash

# Docker 构建脚本

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}开始构建 Docker 镜像...${NC}"

# 镜像名称和标签
IMAGE_NAME="captcha-api"
TAG="${1:-latest}"

# 构建镜像
echo -e "${YELLOW}构建镜像: ${IMAGE_NAME}:${TAG}${NC}"
docker build -t "${IMAGE_NAME}:${TAG}" .

echo -e "${GREEN}构建完成！${NC}"
echo -e "${YELLOW}运行容器:${NC}"
echo "  docker run -p 8000:8000 -v \$(pwd)/data:/app/data -v \$(pwd)/resources:/app/resources ${IMAGE_NAME}:${TAG}"
echo ""
echo -e "${YELLOW}或使用 docker-compose:${NC}"
echo "  docker-compose up -d"

