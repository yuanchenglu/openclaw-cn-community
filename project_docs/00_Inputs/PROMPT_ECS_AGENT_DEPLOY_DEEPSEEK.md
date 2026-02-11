# ECS AI Agent 自动化部署指令 (ShellGPT Edition)

你现在是一个由于 SSH 连接到我阿里云 ECS 服务器的 **高级运维工程师 Agent**。
你的任务是：**全自动部署 OpenClaw 中文文档站**。

## 1. 认证配置 (Run Once)
请先在终端执行以下命令配置 ShellGPT 使用 DeepSeek API：

```bash
# 配置 API Key
export OPENAI_API_KEY="sk-d9603427c72f40d1b8a97e9881a1bcd6"
# 配置 DeepSeek API 地址
export OPENAI_API_HOST="https://api.deepseek.com"
# 设置默认模型 (DeepSeek V3 兼容 chat 接口)
export OPENAI_MODEL="deepseek-chat"
```

## 2. 验证连接
执行测试命令：
```bash
sgpt "你好，请告诉我当前服务器的操作系统版本"
```
如果返回了系统信息，说明 AI 已就绪。

## 3. 执行部署任务
请复制以下 Prompt 发送给 `sgpt --shell`，让它生成自动化运维命令：

```bash
sgpt --shell "
我需要部署一个静态网站到 Nginx。请生成一系列 Linux 命令完成以下任务：
1. 检查并安装 nginx, git (如果不存在)。
2. 创建目录 /www/wwwroot/ai.7color.vip/openclaw/ 并赋予 755 权限，所有者设为 www (宝塔默认用户)。
3. 生成一个 SSH Key (用于 GitHub Deploy)，文件路径 ~/.ssh/github_deploy_key，无密码。
4. 将生成的公钥 (~/.ssh/github_deploy_key.pub) 追加到 ~/.ssh/authorized_keys 中。
5. 修改 Nginx 配置 (假设在 /www/server/nginx/conf/nginx.conf 或 /www/server/panel/vhost/nginx/ai.7color.vip.conf)，
   添加 location /openclaw/ { alias /www/wwwroot/ai.7color.vip/openclaw/; index index.html; }。
   注意：如果只会用 sed 修改比较危险，可以提示我手动修改 Nginx。
6. 最后输出私钥内容 (cat ~/.ssh/github_deploy_key)，并提示我复制。
"
```

## 4. 人工确认
AI 会生成一串命令，仔细检查无误后，输入 `y` 执行。
执行完毕后，记得复制私钥配置到 GitHub。
