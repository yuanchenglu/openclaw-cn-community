# 架构

Source: https://clawd.org.cn/concepts/architecture.html

# 网关架构

最后更新：2026-01-22

## 概述

* 一个长效运行的 **网关 (Gateway)** 拥有所有的消息界面（通过 Baileys 的 WhatsApp，通过 grammY 的 Telegram，Slack，Discord，Signal，iMessage，WebChat）。
* 控制平面客户端（macOS 应用，CLI，Web UI，自动化脚本）通过 **WebSocket** 连接到网关配置的绑定主机（默认 `127.0.0.1:18789`）。
* **节点 (Nodes)**（macOS/iOS/Android/无头模式）也通过 **WebSocket** 连接，但声明 `role: node` 并带有明确的功能/命令。
* 每个主机一个网关；它是唯一打开 WhatsApp 会话的地方。
* 一个 **画布主机 (canvas host)**（默认 `18793`）提供代理可编辑的 HTML 和 A2UI 服务。

## 组件与流程

### 网关 (Gateway - 守护进程)

* 维护提供商连接。
* 暴露类型化的 WS API（请求，响应，服务器推送事件）。
* 针对 JSON Schema 验证入站帧。
* 发出诸如 `agent`, `chat`, `presence`, `health`, `heartbeat`, `cron` 等事件。

### 客户端 (mac 应用 / CLI / web 管理端)

* 每个客户端一个 WS 连接。
* 发送请求 (`health`, `status`, `send`, `agent`, `system-presence`)。
* 订阅事件 (`tick`, `agent`, `presence`, `shutdown`)。

### 节点 (macOS / iOS / Android / 无头模式)

* 连接到带有 `role: node` 的 **同一 WS 服务器**。
* 在 `connect` 中提供设备身份；配对是 **基于设备的**（角色 `node`），批准信息存在设备配对存储中。
* 暴露命令，如 `canvas.*`, `camera.*`, `screen.record`, `location.get`。

协议详情：

* [网关协议](/gateway/protocol.html)

### WebChat

* 使用网关 WS API 进行聊天历史记录和发送的静态 UI。
* 在远程设置中，通过与其他客户端相同的 SSH/Tailscale 隧道连接。

## 连接生命周期（单个客户端）

```
Client                    Gateway
  |                          |
  |---- req:connect -------->|
  |<------ res (ok) ---------|   (或 res error + close)
  |   (payload=hello-ok 携带快照: presence + health)
  |                          |
  |<------ event:presence ---|
  |<------ event:tick -------|
  |                          |
  |------- req:agent ------->|
  |<------ res:agent --------|   (ack: {runId,status:"accepted"})
  |<------ event:agent ------|   (流式传输)
  |<------ res:agent --------|   (最终: {runId,status,summary})
  |                          |
```

## 线路协议（摘要）

* 传输：WebSocket，带有 JSON 载荷的文本帧。
* 第一帧 **必须** 是 `connect`。
* 握手后：
  + 请求：`{type:"req", id, method, params}` → `{type:"res", id, ok, payload|error}`
  + 事件：`{type:"event", event, payload, seq?, stateVersion?}`
* 如果设置了 `OPENCLAW_GATEWAY_TOKEN`（或 `--token`），`connect.params.auth.token` 必须匹配，否则套接字将关闭。
* 副作用方法（`send`, `agent`）需要幂等键才能安全重试；服务器保留一个短暂的去重缓存。
* 节点必须在 `connect` 中包含 `role: "node"` 以及 capabilities/commands/permissions。

## 配对 + 本地信任

* 所有 WS 客户端（操作员 + 节点）在 `connect` 上包含 **设备身份**。
* 新设备 ID 需要配对批准；网关会颁发一个 **设备令牌** 用于后续连接。
* **本地** 连接（回环地址或网关主机自己的 tailnet 地址）可以自动批准，以保持同一主机的用户体验流畅。
* **非本地** 连接必须签署 `connect.challenge` 随机数，并需要明确批准。
* 网关认证 (`gateway.auth.*`) 仍然适用于 **所有** 连接，无论是本地还是远程。

详情：[网关协议](/gateway/protocol.html)，[配对](/start/pairing.html)，[安全](/gateway/security.html)。

## 协议类型化和代码生成

* TypeBox 模式定义了协议。
* JSON Schema 是从这些模式生成的。
* Swift 模型是从 JSON Schema 生成的。

## 远程访问

* 首选：Tailscale 或 VPN。
* 替代方案：SSH 隧道

  bash

  ```
  ssh -N -L 18789:127.0.0.1:18789 user@host
  ```
* 相同的握手 + 认证令牌适用于隧道。
* 在远程设置中可以为 WS 启用 TLS + 可选的固定证书。

## 运维快照

* 启动：`clawdbot gateway`（前台，日志输出到 stdout）。
* 健康检查：通过 WS 的 `health`（也包含在 `hello-ok` 中）。
* 监管：launchd/systemd 用于自动重启。

## 不变量

* 恰好一个网关控制每台主机的一个 Baileys 会话。
* 握手是强制性的；任何非 JSON 或非 connect 的第一帧都会导致硬关闭。
* 事件不重播；客户端必须在出现缺口时刷新。
