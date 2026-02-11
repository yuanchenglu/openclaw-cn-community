# macOS

来源: https://clawd.org.cn/platforms/macos.html

# Clawdbot macOS 配套应用 (菜单栏 + Gateway 代理)

macOS 应用是 Clawdbot 的**菜单栏配套应用**。它拥有权限，在本地管理/连接到 Gateway (launchd 或手动)，并将 macOS 功能作为 node 暴露给 agent。

## 功能

* 在菜单栏显示原生通知和状态。
* 拥有 TCC 提示权限 (通知, 辅助功能, 屏幕录制, 麦克风, 语音识别, 自动化/AppleScript)。
* 运行或连接到 Gateway (本地或远程)。
* 暴露仅限 macOS 的工具 (Canvas, Camera, Screen Recording, `system.run`)。
* 在**远程**模式下启动本地 node host 服务 (launchd)，在**本地**模式下停止它。
* 可选托管 **PeekabooBridge** 用于 UI 自动化。
* 根据请求通过 npm/pnpm 安装全局 CLI (`clawdbot`) (Gateway 运行时不推荐使用 bun)。

## 本地与远程模式

* **本地** (默认): 如果存在运行中的本地 Gateway，应用会连接到它；否则它会通过 `clawdbot gateway install` 启用 launchd 服务。
* **远程**: 应用通过 SSH/Tailscale 连接到 Gateway，且从不启动本地进程。应用启动本地 **node host 服务**，以便远程 Gateway 可以访问此 Mac。应用不会将 Gateway 作为子进程生成。

## Launchd 控制

应用管理标记为 `com.openclaw.gateway` 的每用户 LaunchAgent (或使用 `--profile`/`OPENCLAW_PROFILE` 时为 `com.openclaw.<profile>`)。

bash

```
launchctl kickstart -k gui/$UID/com.openclaw.gateway
launchctl bootout gui/$UID/com.openclaw.gateway
```

运行命名配置文件时，将标签替换为 `com.openclaw.<profile>`。

如果未安装 LaunchAgent，请从应用启用它或运行 `clawdbot gateway install`。

## Node 功能 (mac)

macOS 应用将自己呈现为一个 node。常用命令：

* Canvas: `canvas.present`, `canvas.navigate`, `canvas.eval`, `canvas.snapshot`, `canvas.a2ui.*`
* Camera: `camera.snap`, `camera.clip`
* Screen: `screen.record`
* System: `system.run`, `system.notify`

Node 报告 `permissions` 映射，以便 agent 决定允许什么。

Node 服务 + 应用 IPC:

* 当无头 node host 服务运行时 (远程模式)，它作为 node 连接到 Gateway WS。
* `system.run` 在 macOS 应用 (UI/TCC 上下文) 中通过本地 Unix socket 执行；提示 + 输出保留在应用中。

图示 (SCI):

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + TCC + system.run)
```

## 执行批准 (system.run)

`system.run` 由 macOS 应用中的 **Exec approvals** 控制 (设置 → Exec approvals)。安全 + 询问 + 允许列表存储在 Mac 本地：

```
~/.openclaw/exec-approvals.json
```

示例：

json

```
{
  "version": 1,
  "defaults": {
    "security": "deny",
    "ask": "on-miss"
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "allowlist": [
        { "pattern": "/opt/homebrew/bin/rg" }
      ]
    }
  }
}
```

注意：

* `allowlist` 条目是解析后的二进制路径的 glob 模式。
* 在提示中选择“Always Allow”会将该命令添加到允许列表中。
* `system.run` 环境变量覆盖被过滤 (丢弃 `PATH`, `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`) 然后与应用的环境合并。

## Deep links

应用注册 `clawdbot://` URL scheme 用于本地操作。

### `clawdbot://agent`

触发 Gateway `agent` 请求。

bash

```
open 'clawdbot://agent?message=Hello%20from%20deep%20link'
```

查询参数：

* `message` (必需)
* `sessionKey` (可选)
* `thinking` (可选)
* `deliver` / `to` / `channel` (可选)
* `timeoutSeconds` (可选)
* `key` (可选无人值守模式密钥)

安全：

* 如果没有 `key`，应用会提示确认。
* 有效 `key` 时，运行是无人值守的 (用于个人自动化)。

## 入门流程 (典型)

1. 安装并启动 **Clawdbot.app**。
2. 完成权限检查清单 (TCC 提示)。
3. 确保 **本地** 模式处于活动状态且 Gateway 正在运行。
4. 如果需要终端访问，请安装 CLI。

## 构建与开发工作流 (native)

* `cd apps/macos && swift build`
* `swift run Clawdbot` (或 Xcode)
* 打包应用: `scripts/package-mac-app.sh`

## 调试 Gateway 连接 (macOS CLI)

使用调试 CLI 执行与 macOS 应用相同的 Gateway WebSocket 握手和发现逻辑，而无需启动应用。

bash

```
cd apps/macos
swift run clawdbot-mac connect --json
swift run clawdbot-mac discover --timeout 3000 --json
```

连接选项：

* `--url <ws://host:port>`: 覆盖配置
* `--mode <local|remote>`: 从配置解析 (默认: config 或 local)
* `--probe`: 强制进行新的健康探测
* `--timeout <ms>`: 请求超时 (默认: `15000`)
* `--json`: 用于 diff 的结构化输出

发现选项：

* `--include-local`: 包含会被过滤为“local”的 gateway
* `--timeout <ms>`: 整体发现窗口 (默认: `2000`)
* `--json`: 用于 diff 的结构化输出

提示：与 `clawdbot gateway discover --json` 进行比较，查看 macOS 应用的发现管道 (NWBrowser + tailnet DNS‑SD 回退) 是否与 Node CLI 的基于 `dns-sd` 的发现不同。

## 远程连接管道 (SSH 隧道)

当 macOS 应用在 **远程** 模式下运行时，它会打开一个 SSH 隧道，以便本地 UI 组件可以像在 localhost 上一样与远程 Gateway 通话。

### 控制隧道 (Gateway WebSocket 端口)

* **目的:** 健康检查, 状态, Web Chat, 配置, 和其他控制平面调用。
* **本地端口:** Gateway 端口 (默认 `18789`), 始终稳定。
* **远程端口:** 远程主机上的相同 Gateway 端口。
* **行为:** 无随机本地端口；应用重用现有的健康隧道或在需要时重启它。
* **SSH 形状:** `ssh -N -L <local>:127.0.0.1:<remote>` 带 BatchMode + ExitOnForwardFailure + keepalive 选项。
* **IP 报告:** SSH 隧道使用环回地址，因此 gateway 看到的 node IP 为 `127.0.0.1`。如果您希望显示真实的客户端 IP，请使用 **Direct (ws/wss)** 传输 (参见 [macOS 远程访问](/platforms/mac/remote.html))。

有关设置步骤，请参阅 [macOS 远程访问](/platforms/mac/remote.html)。有关协议详细信息，请参阅 [Gateway 协议](/gateway/protocol.html)。

## 相关文档

* [Gateway 运行手册](/gateway.html)
* [Gateway (macOS)](/platforms/mac/bundled-gateway.html)
* [macOS 权限](/platforms/mac/permissions.html)
* [Canvas](/platforms/mac/canvas.html)
