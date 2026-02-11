# Docker 方案 (The Ultimate Solution)

## 1. 原理
既然你已经安装了 Docker，我们就不用折腾 Python 或 Go 环境了。
直接运行一个 **临时的 Linux 容器** (Alpine)，在里面安装 SSH 客户端，生成密钥，并把公钥写入宿主机的 `authorized_keys`。

## 2. 操作步骤 (One-Liner)

请直接复制以下命令在 ECS 终端执行：

```bash
# 运行一个一次性的 alpine 容器，挂载宿主机的 ssh 目录
docker run --rm -v ~/.ssh:/root/.ssh alpine sh -c "
  apk add --no-cache openssh-client && \
  ssh-keygen -t rsa -b 4096 -C 'github-actions-deploy' -f /root/.ssh/github_deploy_key -N '' && \
  cat /root/.ssh/github_deploy_key.pub >> /root/.ssh/authorized_keys && \
  chmod 600 /root/.ssh/authorized_keys && \
  echo '=== 部署私钥 (请复制到 GitHub Secrets) ===' && \
  cat /root/.ssh/github_deploy_key && \
  echo '=== 部署结束 ==='
"
```

## 3. 结果验证
执行完毕后，屏幕上会直接打印出私钥内容 (`-----BEGIN OPENSSH PRIVATE KEY...`)。
复制这段内容，填入 GitHub 仓库的 `SSH_PRIVATE_KEY` 变量中即可。

## 4. 目录权限配置 (补充)
Docker 做不到宿主机文件权限修改 (除非特权模式)，所以目录创建还是手动执行一下最稳：

```bash
mkdir -p /www/wwwroot/ai.7color.vip/openclaw/
chown -R www:www /www/wwwroot/ai.7color.vip/openclaw/
chmod -R 755 /www/wwwroot/ai.7color.vip/openclaw/
```
