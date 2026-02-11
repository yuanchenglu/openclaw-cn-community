# AI 自动部署指令 (v1.0)

你现在是我的 **首席 Linux 运维工程师**。
你的任务是：**全自动准备 GitHub Actions 部署环境**。

请生成并执行以下任务的 Shell 脚本：

## 1. 创建站点目录
- 检查 `/www/wwwroot/ai.7color.vip/openclaw/` 目录是否存在。
- 如果不存在，创建它。
- 将该目录的所有者设为 `www:www` (这是宝塔面板默认的 Web 用户)。
- 赋予目录 `755` 权限。

## 2. 检查 Nginx 配置
- 检查 Nginx 是否已经配置了 `/openclaw/` 的访问规则。
- 如果没有，请在 `/www/server/panel/vhost/nginx/ai.7color.vip.conf` (假设这是宝塔站点配置文件路径) 中**追加**以下 location 规则：
  ```nginx
  location /openclaw/ {
      alias /www/wwwroot/ai.7color.vip/openclaw/;
      index index.html;
      try_files $uri $uri/ /openclaw/index.html;
  }
  ```
- **注意**: 如果你不确定文件路径，请先帮我 `find / -name ai.7color.vip.conf` 查找一下。
- 修改配置后，重载 Nginx (`nginx -s reload`)。

## 3. SSH 密钥部署 (已完成，仅验证)
- 我刚刚已经生成了密钥 `~/.ssh/github_deploy_key`。
- 请帮我再次确认 `~/.ssh/authorized_keys` 中是否包含该密钥的公钥内容。
- 如果包含，输出 "✅ SSH Key Ready"。
- 如果不包含，请把 `~/.ssh/github_deploy_key.pub` 追加进去。

## 4. 输出最终信息
请以 Markdown 格式输出以下信息，方便我复制：
- **服务器 IP**: (自动获取公网 IP)
- **SSH 用户**: root
- **私钥内容**: (自动 `cat ~/.ssh/github_deploy_key`)
- **站点 URL**: http://ai.7color.vip/openclaw/

请开始执行。
