# ECS AI Agent 自动化部署指令

你现在是一个由于 SSH 连接到我阿里云 ECS 服务器的 **高级运维工程师 Agent**。
你的任务是：**全自动部署 OpenClaw 中文文档站**。

请严格按照以下步骤执行，如果遇到权限问题请使用 `sudo`，如果遇到错误请尝试自动修复或停止并报告。

## 1. 环境检查与准备
- 检查操作系统版本 (`cat /etc/os-release`)。
- 检查是否安装了 `nginx`。如果没有，请安装最新稳定版。
- 检查是否安装了 `git`。如果没有，请安装。
- 确保 `/www/wwwroot/ai.7color.vip/` 目录存在。如果不存在，请创建它。

## 2. 站点目录配置
- 在 `/www/wwwroot/ai.7color.vip/` 下创建子目录 `openclaw`。
- 设置目录权限：确保当前用户 (或 www-data/nginx 用户) 对该目录有读写权限。
  ```bash
  mkdir -p /www/wwwroot/ai.7color.vip/openclaw
  chown -R www-data:www-data /www/wwwroot/ai.7color.vip/openclaw
  chmod -R 755 /www/wwwroot/ai.7color.vip/openclaw
  ```

## 3. Nginx 配置
- 查找 Nginx 配置文件位置 (通常在 `/etc/nginx/nginx.conf` 或 `/etc/nginx/conf.d/`).
- 创建一个新的站点配置文件 `ai.7color.vip.conf` (如果已存在则备份并修改)。
- **核心配置要求**:
  - 监听 80 和 443 端口。
  - 域名: `ai.7color.vip`。
  - 根目录: `/www/wwwroot/ai.7color.vip/`。
  - **关键**: 配置 `location /openclaw/` 指向 `/www/wwwroot/ai.7color.vip/openclaw/`。
  - 开启 Gzip 压缩。
  - 配置 SSL (如果服务器上有证书，路径通常在 `/etc/letsencrypt/` 或 `/www/server/panel/vhost/cert/`)。如果找不到证书，先配置 HTTP 并在 80 端口验证。

## 4. SSH Key 配置 (用于 GitHub Actions)
- 检查 `~/.ssh/github_deploy_key` 是否存在。
- 如果不存在，生成一个新的 SSH Key:
  ```bash
  ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f ~/.ssh/github_deploy_key -N ""
  ```
- 将公钥 (`~/.ssh/github_deploy_key.pub`) 添加到 `~/.ssh/authorized_keys`。
- **重要**: 输出私钥内容 (`cat ~/.ssh/github_deploy_key`)，并提示我："请将以下私钥内容复制到 GitHub Repository Secrets 中，Key 为 SSH_PRIVATE_KEY"。

## 5. 验证
- 重载 Nginx 配置 (`nginx -s reload`)。
- 创建一个测试文件 `index.html` 在 `/www/wwwroot/ai.7color.vip/openclaw/` 中，内容为 "OpenClaw Deploy Ready"。
- 尝试 `curl http://localhost/openclaw/` 验证是否能访问。

请开始执行。
