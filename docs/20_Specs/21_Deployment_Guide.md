# 部署指南 (Deployment Guide)

> **目标**: 将 OpenClaw 中文文档站部署至阿里云 ECS，并启用 GitHub Actions 自动构建。
> **前提**: 拥有 GitHub 账号、阿里云 ECS 服务器（已安装宝塔面板）。

## 1. 阿里云 ECS 准备工作

### 1.1 创建站点目录
登录宝塔面板或通过 SSH 连接服务器，执行以下命令：
```bash
# 确保存放文档的目录存在
mkdir -p /www/wwwroot/ai.7color.vip/openclaw/
# 确保目录权限正确 (假设 web 用户为 www)
chown -R www:www /www/wwwroot/ai.7color.vip/openclaw/
```

### 1.2 配置 Nginx
在宝塔面板中，找到 `ai.7color.vip` 站点的配置文件，添加或确保以下配置存在（通常宝塔默认静态配置即可，无需额外 location，除非有特殊需求）：
- 只要 `/www/wwwroot/ai.7color.vip/` 目录下有 `openclaw` 文件夹，Nginx 就能自动服务 `http://ai.7color.vip/openclaw/`。
- **注意**: 确保 `openclaw` 目录下有 `index.html` (部署后会自动生成)。

### 1.3 生成 SSH 密钥对
为了让 GitHub 能免密登录你的 ECS，需要生成一对 SSH Key。
在 **ECS 服务器** 上执行：
```bash
ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key -N ""
```
- 私钥: `~/.ssh/github_deploy_key` (复制内容，稍后填入 GitHub)
- 公钥: `~/.ssh/github_deploy_key.pub`

### 1.4 安装公钥
将公钥追加到 `authorized_keys` 中，允许通过该密钥登录：
```bash
cat ~/.ssh/github_deploy_key.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

---

## 2. GitHub 仓库配置

### 2.1 创建仓库
1. 在 GitHub 上新建一个仓库，例如 `openclaw-cn-docs`。
2. 将本地代码推送到该仓库：
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/openclaw-cn-docs.git
git push -u origin main
```

### 2.2 配置 Secrets
进入 GitHub 仓库页面 -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**。
添加以下 3 个变量：

| Name | Value | 说明 |
|------|-------|------|
| `SSH_HOST` | `1.2.3.4` | 你的阿里云 ECS 公网 IP |
| `SSH_USER` | `root` | 登录用户名 (通常是 root) |
| `SSH_PRIVATE_KEY` | `-----BEGIN OPENSSH PRIVATE KEY...` | 步骤 1.3 中生成的**私钥**内容 |

---

## 3. 验证部署

### 3.1 触发构建
- 只要你执行了 `git push` 到 `main` 分支，GitHub Actions 就会自动触发。
- 进入仓库的 **Actions** 标签页，查看 `Deploy to Aliyun ECS` 工作流的运行状态。

### 3.2 访问站点
- 等待构建成功（通常 1-2 分钟）。
- 访问 `http://ai.7color.vip/openclaw/`。
- 如果能看到文档首页，说明部署成功！

---

## 4. 故障排除

- **权限被拒绝 (Permission denied)**: 检查 `SSH_PRIVATE_KEY` 是否复制完整，ECS 上的 `authorized_keys` 权限是否为 600。
- **404 Not Found**: 检查 Nginx 根目录是否指向 `/www/wwwroot/ai.7color.vip/`，且该目录下存在 `openclaw` 文件夹。
- **样式丢失**: 检查 `docs/.vitepress/config.mts` 中的 `base` 是否正确配置为 `/openclaw/`。
