# Docker + AI Agent: 终极运维方案 (The Ultimate Ops Solution)

## 1. 方案核心 (Core Concept)
既然你不熟悉 Docker，我会给你一个**“复制粘贴即用”**的命令。
我们将运行一个 **特权模式 (Privileged)** 的 AI 容器。
- **特权模式**: 让容器内的 AI 有权限直接操作宿主机的 Docker、文件系统和网络。
- **持久化**: 容器重启后数据还在。
- **AI 工具**: 使用 `aichat` (Rust编写，轻量高效，支持 DeepSeek)。

## 2. 一键安装命令 (One-Liner Install)

请在 ECS 终端**直接复制并执行**以下命令：

```bash
# 1. 创建 AI 配置目录
mkdir -p /root/ai-ops-config

# 2. 启动 AI 运维容器 (特权模式 + 挂载宿主机关键目录)
docker run -d \
  --name ai-ops-agent \
  --restart always \
  --privileged \
  --net host \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /:/host-root \
  -e OPENAI_API_KEY="sk-d9603427c72f40d1b8a97e9881a1bcd6" \
  -e OPENAI_API_BASE="https://api.deepseek.com/v1" \
  ghcr.io/sigoden/aichat \
  tail -f /dev/null
```
*(解释: 这个命令会在后台启动一个叫 `ai-ops-agent` 的容器，它挂载了宿主机的根目录 `/` 到容器内的 `/host-root`，这样 AI 就能修改宿主机的文件了)*

## 3. 如何使用 AI (How to Use)

### 3.1 进入 AI 终端
每次想让 AI 干活时，执行：
```bash
docker exec -it ai-ops-agent aichat
```
你会进入一个交互式对话界面 `>>>`。

### 3.2 发送指令 (Prompt)
在 `>>>` 提示符后直接输入中文需求。例如：

**场景一：部署 Nginx**
> "我需要修改宿主机的 Nginx 配置。宿主机根目录挂载在 /host-root。请帮我在 /host-root/www/server/nginx/conf/vhost/ 下创建一个 ai.7color.vip.conf 文件，内容是标准静态站点配置，根目录指向 /www/wwwroot/ai.7color.vip/openclaw。"

**场景二：查看系统负载**
> "请帮我查看宿主机的 CPU 和内存占用情况 (提示: 你在特权容器里，可以直接运行 top)"

**场景三：自动生成 SSH Key**
> "请帮我生成一个 SSH Key 用于 GitHub 部署，保存在 /host-root/root/.ssh/github_deploy_key，并将公钥追加到 /host-root/root/.ssh/authorized_keys。"

---

## 4. 常用运维指令 (Cheat Sheet)

### 退出 AI
输入 `.exit` 或按 `Ctrl+D`。

### 查看日志
```bash
docker logs ai-ops-agent
```

### 重启 AI
```bash
docker restart ai-ops-agent
```
