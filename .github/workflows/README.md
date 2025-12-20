# GitHub Actions 工作流说明

本仓库包含以下 CI/CD 工作流：

## 1. CI 工作流 (`ci.yml`)

**触发条件：**
- 推送到 `main` 或 `develop` 分支
- 创建 Pull Request 到 `main` 或 `develop` 分支

**执行任务：**
- 代码检查和格式化验证
- 导入验证
- Docker 镜像构建测试

## 2. CD 工作流 - GitHub Container Registry (`cd.yml`)

**触发条件：**
- 推送到 `main` 分支
- 创建版本标签（如 `v1.0.0`）
- 手动触发（workflow_dispatch）

**执行任务：**
- 构建 Docker 镜像
- 推送到 GitHub Container Registry (ghcr.io)
- 支持多平台构建（amd64, arm64）

**镜像标签规则：**
- 分支名（如 `main`）
- 语义版本（如 `v1.0.0`）
- 主.次版本（如 `v1.0`）
- SHA 前缀（如 `main-abc123`）
- `latest`（仅 main 分支）

## 3. CD 工作流 - Docker Hub (`docker-hub.yml`)

**触发条件：**
- 推送到 `main` 分支
- 创建版本标签（如 `v1.0.0`）
- 手动触发（workflow_dispatch）

**执行任务：**
- 构建 Docker 镜像
- 推送到 Docker Hub
- 支持多平台构建（amd64, arm64）

**所需 Secrets：**
- `DOCKER_HUB_USERNAME`: Docker Hub 用户名
- `DOCKER_HUB_PASSWORD`: Docker Hub 访问令牌

## 使用说明

### 设置 GitHub Container Registry（自动）

GitHub Container Registry 使用 `GITHUB_TOKEN`，无需额外配置。推送后镜像位于：
```
ghcr.io/<username>/<repository>:<tag>
```

### 设置 Docker Hub（可选）

1. 在 GitHub 仓库设置中添加 Secrets：
   - `DOCKER_HUB_USERNAME`: 你的 Docker Hub 用户名
   - `DOCKER_HUB_PASSWORD`: Docker Hub 访问令牌（不是密码）

2. 访问令牌创建步骤：
   - 登录 Docker Hub
   - 进入 Account Settings > Security
   - 创建新的 Access Token
   - 复制令牌并添加到 GitHub Secrets

### 手动触发部署

1. 进入 GitHub Actions 页面
2. 选择对应的工作流
3. 点击 "Run workflow"
4. 输入标签（可选）
5. 点击 "Run workflow"

### 版本发布

创建版本标签以触发自动构建：

```bash
git tag v1.0.0
git push origin v1.0.0
```

这将自动构建并推送带版本标签的镜像。

## 拉取镜像

### GitHub Container Registry

```bash
docker pull ghcr.io/<username>/<repository>:latest
```

### Docker Hub

```bash
docker pull <username>/captcha-api:latest
```

## 故障排查

### 工作流失败

1. 检查 Actions 标签页中的错误日志
2. 确认所有必需的 Secrets 已配置
3. 验证 Dockerfile 语法正确
4. 检查依赖项是否可用

### 镜像构建失败

1. 检查 Dockerfile 中的路径是否正确
2. 确认所有依赖文件已提交到仓库
3. 验证 `.dockerignore` 配置正确

