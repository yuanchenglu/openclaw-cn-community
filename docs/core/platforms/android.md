# Android

Source: https://clawd.org.cn/platforms/android.html

# Android 应用 (节点)

## 支持快照

* 角色：伴侣节点应用（Android 不托管网关）。
* 需要网关：是（在 macOS、Linux 或 Windows 上通过 WSL2 运行）。
* 安装：[快速开始](/start/getting-started.html) + [配对](/gateway/pairing.html)。
* 网关：[运行手册](/gateway.html) + [配置](/gateway/configuration.html)。
  + 协议：[网关协议](/gateway/protocol.html)（节点 + 控制平面）。

## 系统控制

系统控制 (launchd/systemd) 位于网关主机上。请参阅 [网关](/gateway.html)。

## 连接运行手册

Android 节点应用 ⇄ (mDNS/NSD + WebSocket) ⇄ **网关**

Android 直接连接到网关 WebSocket（默认 `ws://<host>:18789`）并使用网关拥有的配对。

### 先决条件

* 你可以在“主”机器上运行网关。
* Android 设备/模拟器可以到达网关 WebSocket：
  + 同一 LAN 使用 mDNS/NSD，**或**
  + 同一 Tailscale tailnet 使用广域 Bonjour / 单播 DNS-SD（见下文），**或**
  + 手动网关主机/端口（回退）
* 你可以在网关机器上运行 CLI (`clawdbot`)（或通过 SSH）。

### 1) 启动网关

bash

```
clawdbot gateway --port 18789 --verbose
```

在日志中确认你看到类似以下内容：

* `listening on ws://0.0.0.0:18789`

对于仅 tailnet 设置（推荐用于维也纳 ⇄ 伦敦），将网关绑定到 tailnet IP：

* 在网关主机上的 `~/.openclaw/openclaw.json` 中设置 `gateway.bind: "tailnet"`。
* 重启网关 / macOS 菜单栏应用。

### 2) 验证发现 (可选)

从网关机器：

bash

```
dns-sd -B _clawdbot-gw._tcp local.
```

更多调试说明：[Bonjour](/gateway/bonjour.html)。

#### 通过单播 DNS-SD 进行 Tailnet (维也纳 ⇄ 伦敦) 发现

Android NSD/mDNS 发现不会跨越网络。如果你的 Android 节点和网关在不同的网络上但通过 Tailscale 连接，请改用广域 Bonjour / 单播 DNS-SD：

1. 在网关主机上设置一个 DNS-SD 区域（例如 `clawdbot.internal.`）并发布 `_clawdbot-gw._tcp` 记录。
2. 配置 Tailscale 分割 DNS，将 `clawdbot.internal` 指向该 DNS 服务器。

详情和示例 CoreDNS 配置：[Bonjour](/gateway/bonjour.html)。

### 3) 从 Android 连接

在 Android 应用中：

* 应用通过**前台服务**（持久通知）保持其网关连接处于活动状态。
* 打开 **设置**。
* 在 **发现的网关** 下，选择你的网关并点击 **连接**。
* 如果 mDNS 被阻止，使用 **高级 → 手动网关**（主机 + 端口）和 **连接 (手动)**。

首次成功配对后，Android 会在启动时自动重新连接：

* 手动端点（如果已启用），否则
* 最后发现的网关（尽力而为）。

### 4) 批准配对 (CLI)

在网关机器上：

bash

```
clawdbot nodes pending
clawdbot nodes approve <requestId>
```

配对详情：[网关配对](/gateway/pairing.html)。

### 5) 验证节点已连接

* 通过节点状态：

  bash

  ```
  clawdbot nodes status
  ```
* 通过网关：

  bash

  ```
  clawdbot gateway call node.list --params "{}"
  ```

### 6) 聊天 + 历史记录

Android 节点的聊天表单使用网关的**主会话密钥** (`main`)，因此历史记录和回复与 WebChat 和其他客户端共享：

* 历史记录：`chat.history`
* 发送：`chat.send`
* 推送更新（尽力而为）：`chat.subscribe` → `event:"chat"`

### 7) 画布 + 相机

#### 网关画布主机 (推荐用于 web 内容)

如果你希望节点显示智能体可以在磁盘上编辑的真实 HTML/CSS/JS，请将节点指向网关画布主机。

注意：节点在 `canvasHost.port`（默认 `18793`）上使用独立的画布主机。

1. 在网关主机上创建 `~/clawwork/canvas/index.html`。
2. 将节点导航到它（LAN）：

bash

```
clawdbot nodes invoke --node "<Android Node>" --command canvas.navigate --params '{"url":"http://<gateway-hostname>.local:18793/__clawdbot__/canvas/"}'
```

Tailnet（可选）：如果两个设备都在 Tailscale 上，请使用 MagicDNS 名称或 tailnet IP 而不是 `.local`，例如 `http://<gateway-magicdns>:18793/__clawdbot__/canvas/`。

此服务器将实时重新加载客户端注入 HTML 并在文件更改时重新加载。A2UI 主机位于 `http://<gateway-host>:18793/__clawdbot__/a2ui/`。

画布命令（仅限前台）：

* `canvas.eval`, `canvas.snapshot`, `canvas.navigate`（使用 `{"url":""}` 或 `{"url":"/"}` 返回默认脚手架）。`canvas.snapshot` 返回 `{ format, base64 }`（默认 `format="jpeg"`）。
* A2UI：`canvas.a2ui.push`, `canvas.a2ui.reset`（`canvas.a2ui.pushJSONL` 遗留别名）

相机命令（仅限前台；权限门控）：

* `camera.snap` (jpg)
* `camera.clip` (mp4)

有关参数和 CLI 助手，请参阅 [相机节点](/nodes/camera.html)。
