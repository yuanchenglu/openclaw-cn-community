# Linux

来源: https://clawd.org.cn/platforms/linux.html

# Linux 应用

Gateway 在 Linux 上得到完全支持。**推荐使用 Node 作为运行时**。不建议将 Bun 用于 Gateway（存在 WhatsApp/Telegram bug）。

原生 Linux 配套应用正在计划中。如果您想帮忙构建，欢迎贡献。

## 初学者快速路径 (VPS)

1. 安装 Node 22+
2. `npm i -g clawdbot@latest`
3. `openclaw-cn onboard --install-daemon`
4. 从您的笔记本电脑：`ssh -N -L 18789:127.0.0.1:18789 <user>@<host>`
5. 打开 `http://127.0.0.1:18789/` 并粘贴您的令牌

分步 VPS 指南：[exe.dev](/platforms/exe-dev.html)

## 安装

* [入门](/start/getting-started.html)
* [安装与更新](/install/updating.html)
* 可选流程：[Bun (实验性)](/install/bun.html), [Nix](/install/nix.html), [Docker](/install/docker.html)

## Gateway

* [Gateway 运行手册](/gateway.html)
* [配置](/gateway/configuration.html)

## Gateway 服务安装 (CLI)

使用以下命令之一：

```
openclaw-cn onboard --install-daemon
```

或者：

```
clawdbot gateway install
```

或者：

```
clawdbot configure
```

在提示时选择 **Gateway service**。

修复/迁移：

```
clawdbot doctor
```

## 系统控制 (systemd 用户单元)

Clawdbot 默认安装 systemd **user** 服务。对于共享或始终在线的服务器，请使用 **system** 服务。完整的单元示例和指南位于 [Gateway 运行手册](/gateway.html) 中。

最小设置：

创建 `~/.config/systemd/user/clawdbot-gateway[-<profile>].service`：

```
[Unit]
Description=Clawdbot Gateway (profile: <profile>, v<version>)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/clawdbot gateway --port 18789
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

启用它：

```
systemctl --user enable --now clawdbot-gateway[-<profile>].service
```
