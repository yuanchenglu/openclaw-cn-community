# Windows

Source: https://clawd.org.cn/platforms/windows.html

# Windows (WSL2)

Clawdbot 在 Windows 上推荐**通过 WSL2**（推荐 Ubuntu）。CLI + 网关在 Linux 内部运行，这保持了运行时的一致性，并使工具更加兼容（Node/Bun/pnpm、Linux 二进制文件、技能）。原生 Windows 安装未经测试且问题更多。

原生 Windows 伴侣应用已在计划中。

## 安装 (WSL2)

* [快速开始](/start/getting-started.html)（在 WSL 内部使用）
* [安装 & 更新](/install/updating.html)
* 官方 WSL2 指南 (Microsoft)：<https://learn.microsoft.com/windows/wsl/install>

## 网关

* [网关运行手册](/gateway.html)
* [配置](/gateway/configuration.html)

## 网关服务安装 (CLI)

在 WSL2 内部：

```
openclaw-cn onboard --install-daemon
```

或：

```
clawdbot gateway install
```

或：

```
clawdbot configure
```

出现提示时选择 **Gateway service**。

修复/迁移：

```
clawdbot doctor
```

## 高级：通过 LAN 暴露 WSL 服务 (portproxy)

WSL 有自己的虚拟网络。如果另一台机器需要访问**在 WSL 内部**运行的服务（SSH、本地 TTS 服务器或网关），你必须将 Windows 端口转发到当前的 WSL IP。WSL IP 在重启后会更改，因此你可能需要刷新转发规则。

示例（PowerShell **作为管理员**）：

powershell

```
$Distro = "Ubuntu-24.04"
$ListenPort = 2222
$TargetPort = 22

$WslIp = (wsl -d $Distro -- hostname -I).Trim().Split(" ")[0]
if (-not $WslIp) { throw "WSL IP not found." }

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$ListenPort `
  connectaddress=$WslIp connectport=$TargetPort
```

允许端口通过 Windows 防火墙（一次性）：

powershell

```
New-NetFirewallRule -DisplayName "WSL SSH $ListenPort" -Direction Inbound `
  -Protocol TCP -LocalPort $ListenPort -Action Allow
```

在 WSL 重启后刷新 portproxy：

powershell

```
netsh interface portproxy delete v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 | Out-Null
netsh interface portproxy add v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 `
  connectaddress=$WslIp connectport=$TargetPort | Out-Null
```

注意：

* 从另一台机器 SSH 的目标是 **Windows 主机 IP**（例如：`ssh user@windows-host -p 2222`）。
* 远程节点必须指向**可达的**网关 URL（不是 `127.0.0.1`）；使用 `clawdbot status --all` 确认。
* 使用 `listenaddress=0.0.0.0` 用于 LAN 访问；`127.0.0.1` 仅限本地。
* 如果你希望这是自动的，请注册一个计划任务在登录时运行刷新步骤。

## 逐步 WSL2 安装

### 1) 安装 WSL2 + Ubuntu

打开 PowerShell (管理员)：

powershell

```
wsl --install
# Or pick a distro explicitly:
wsl --list --online
wsl --install -d Ubuntu-24.04
```

如果 Windows 要求，请重启。

### 2) 启用 systemd (网关安装需要)

在你的 WSL 终端中：

bash

```
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

然后从 PowerShell：

powershell

```
wsl --shutdown
```

重新打开 Ubuntu，然后验证：

bash

```
systemctl --user status
```

### 3) 安装 Clawdbot (在 WSL 内部)

在 WSL 内部遵循 Linux 快速开始流程：

bash

```
git clone https://github.com/clawdbot/clawdbot.git
cd clawdbot
pnpm install
pnpm ui:build # auto-installs UI deps on first run
pnpm build
openclaw-cn onboard
```

完整指南：[快速开始](/start/getting-started.html)

## Windows 伴侣应用

我们还没有 Windows 伴侣应用。如果你想贡献使其发生，欢迎贡献。
