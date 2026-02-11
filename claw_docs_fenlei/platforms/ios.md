# iOS

来源: https://clawd.org.cn/platforms/ios.html

# iOS App (Node)

可用性：内部预览。iOS 应用尚未公开分发。

## 功能

* 通过 WebSocket 连接到 Gateway (LAN 或 tailnet)。
* 暴露 node 功能：Canvas, 屏幕快照, 相机捕获, 位置, 通话模式, 语音唤醒。
* 接收 `node.invoke` 命令并报告 node 状态事件。

## 要求

* Gateway 运行在另一台设备上 (macOS, Linux, 或通过 WSL2 的 Windows)。
* 网络路径：
  + 通过 Bonjour 在同一 LAN 下，**或者**
  + 通过单播 DNS-SD (`clawdbot.internal.`) 的 Tailnet，**或者**
  + 手动主机/端口 (回退)。

## 快速开始 (配对 + 连接)

1. 启动 Gateway:

bash

```
clawdbot gateway --port 18789
```

2. 在 iOS 应用中，打开设置并选择已发现的 gateway (或启用手动主机并输入主机/端口)。
3. 在 gateway 主机上批准配对请求：

bash

```
clawdbot nodes pending
clawdbot nodes approve <requestId>
```

4. 验证连接：

bash

```
clawdbot nodes status
clawdbot gateway call node.list --params "{}"
```

## 发现路径

### Bonjour (LAN)

Gateway 在 `local.` 上广播 `_clawdbot._tcp`。iOS 应用会自动列出这些。

### Tailnet (跨网络)

如果 mDNS 被阻止，请使用单播 DNS-SD 区域 (推荐域名：`clawdbot.internal.`) 和 Tailscale 分离 DNS。参见 [Bonjour](/gateway/bonjour.html) 获取 CoreDNS 示例。

### 手动主机/端口

在设置中，启用 **Manual Host** 并输入 gateway 主机 + 端口 (默认 `18789`)。

## Canvas + A2UI

iOS node 渲染 WKWebView canvas。使用 `node.invoke` 驱动它：

bash

```
clawdbot nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18793/__clawdbot__/canvas/"}'
```

注意：

* Gateway canvas host 提供 `/__clawdbot__/canvas/` 和 `/__clawdbot__/a2ui/`。
* 当 canvas host URL 被广播时，iOS node 在连接时自动导航到 A2UI。
* 使用 `canvas.navigate` 和 `{"url":""}` 返回内置脚手架。

### Canvas eval / snapshot

bash

```
clawdbot nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__clawdbot; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

bash

```
clawdbot nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## 语音唤醒 + 通话模式

* 语音唤醒和通话模式在设置中可用。
* iOS 可能会挂起后台音频；当应用未处于活动状态时，将语音功能视为尽力而为。

## 常见错误

* `NODE_BACKGROUND_UNAVAILABLE`: 将 iOS 应用带到前台 (canvas/camera/screen 命令需要它)。
* `A2UI_HOST_NOT_CONFIGURED`: Gateway 未广播 canvas host URL；检查 [Gateway 配置](/gateway/configuration.html) 中的 `canvasHost`。
* 配对提示从未出现：运行 `clawdbot nodes pending` 并手动批准。
* 重新安装后重新连接失败：Keychain 配对令牌已被清除；重新配对 node。

## 相关文档

* [配对](/gateway/pairing.html)
* [发现](/gateway/discovery.html)
* [Bonjour](/gateway/bonjour.html)
