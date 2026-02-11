# WhatsApp

来源: https://clawd.org.cn/channels/whatsapp.html

# WhatsApp (web 频道)

状态: 仅限通过 Baileys 的 WhatsApp Web。网关拥有会话。

## 快速设置（初学者）

1. 尽可能使用**单独的电话号码**（推荐）。
2. 在 `~/.openclaw-cn/openclaw-cn.json` 中配置 WhatsApp。
3. 运行 `openclaw-cn channels login` 扫描二维码（已关联设备）。
4. 启动网关。

最小配置：

json5

```
{
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551234567"]
    }
  }
}
```

## 目标

* 在一个网关进程中支持多个 WhatsApp 账号（多账号）。
* 确定性路由：回复返回给 WhatsApp，无需模型路由。
* 模型可以看到足够的上下文来理解引用回复。

## 配置写入

默认情况下，允许 WhatsApp 通过 `/config set|unset` 触发配置更新（需要 `commands.config: true`）。

禁用方法：

json5

```
{
  channels: { whatsapp: { configWrites: false } }
}
```

## 架构（归属关系）

* **网关**拥有 Baileys socket 和收件箱循环。
* **CLI / macOS 应用**与网关通信；不直接使用 Baileys。
* 出站发送需要**活动监听器**；否则发送会快速失败。

## 获取电话号码（两种模式）

WhatsApp 需要真实的手机号码进行验证。VoIP 和虚拟号码通常会被阻止。支持两种在 WhatsApp 上运行 Clawdbot 的方式：

### 专用号码（推荐）

为 Clawdbot 使用**单独的电话号码**。体验最佳，路由清晰，没有自聊怪癖。理想设置：**备用/旧 Android 手机 + eSIM**。保持连接 Wi-Fi 和电源，并通过二维码关联。

**WhatsApp Business：** 你可以在同一设备上使用不同号码的 WhatsApp Business。非常适合将个人 WhatsApp 分开 —— 安装 WhatsApp Business 并在那里注册 Clawdbot 号码。

**配置示例（专用号码，单用户白名单）：**

json5

```
{
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551234567"]
    }
  }
}
```

**配对模式（可选）：** 如果你想使用配对而不是白名单，请将 `channels.whatsapp.dmPolicy` 设置为 `pairing`。未知发送者会收到配对码；使用以下命令批准：`openclaw-cn pairing approve whatsapp <code>`

### 个人号码（备选）

快速备选：在**你自己的号码**上运行 Clawdbot。给自己发消息（WhatsApp “Message yourself”）进行测试，这样就不会打扰联系人。在设置和实验期间，需要在主手机上读取验证码。**必须启用自聊模式。** 当向导询问你的个人 WhatsApp 号码时，请输入你用来发消息的手机号码（所有者/发送者），而不是助手号码。

**配置示例（个人号码，自聊）：**

json

```
{
  "whatsapp": {
    "selfChatMode": true,
    "dmPolicy": "allowlist",
    "allowFrom": ["+15551234567"]
  }
}
```

如果未设置 `messages.responsePrefix`，自聊回复默认为 `[{identity.name}]`（如果设置了身份名称），否则为 `[clawdbot]`。显式设置它可以自定义或禁用前缀（使用 `""` 移除它）。

### 号码获取技巧

* **本地 eSIM** 来自你所在国家的移动运营商（最可靠）
  + 奥地利：[hot.at](https://www.hot.at)
  + 英国：[giffgaff](https://www.giffgaff.com) — 免费 SIM 卡，无合约
* **预付费 SIM 卡** — 便宜，只需要接收一条短信进行验证

**避免：** TextNow, Google Voice, 大多数“免费短信”服务 — WhatsApp 会严厉封锁这些号码。

**提示：** 号码只需要接收一条验证短信。之后，WhatsApp Web 会话通过 `creds.json` 保持。

## 为什么不使用 Twilio？

* 早期的 Clawdbot 版本支持 Twilio 的 WhatsApp Business 集成。
* WhatsApp Business 号码不适合作为个人助手。
* Meta 强制执行 24 小时回复窗口；如果你在过去 24 小时内没有回复，商业号码无法发起新消息。
* 高频率或“健谈”的使用会触发严厉的封锁，因为商业账户并不打算发送大量个人助手消息。
* 结果：投递不可靠且频繁封锁，因此移除了支持。

## 登录 + 凭证

* 登录命令：`openclaw-cn channels login`（通过已关联设备扫描二维码）。
* 多账号登录：`openclaw-cn channels login --account <id>` (`<id>` = `accountId`)。
* 默认账号（省略 `--account` 时）：如果存在则为 `default`，否则为第一个配置的账号 ID（排序后）。
* 凭证存储在 `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`。
* 备份副本位于 `creds.json.bak`（损坏时恢复）。
* 遗留兼容性：旧版本安装将 Baileys 文件直接存储在 `~/.openclaw/credentials/` 中。
* 注销：`openclaw-cn channels logout`（或 `--account <id>`）删除 WhatsApp 认证状态（但保留共享的 `oauth.json`）。
* 注销的 socket => 错误提示重新关联。

## 入站流程（私信 + 群组）

* WhatsApp 事件来自 `messages.upsert` (Baileys)。
* 收件箱监听器在关闭时分离，以避免在测试/重启中积累事件处理程序。
* 状态/广播聊天被忽略。
* 直接聊天使用 E.164；群组使用群组 JID。
* **DM 策略**：`channels.whatsapp.dmPolicy` 控制直接聊天访问（默认：`pairing`）。
  + 配对：未知发送者会收到配对码（通过 `openclaw-cn pairing approve whatsapp <code>` 批准；代码 1 小时后过期）。
  + 开放：需要 `channels.whatsapp.allowFrom` 包含 `"*"`。
  + 自身消息始终允许；“自聊模式”仍需要 `channels.whatsapp.allowFrom` 包含你自己的号码。

### 个人号码模式（备选）

如果你在**个人 WhatsApp 号码**上运行 Clawdbot，请启用 `channels.whatsapp.selfChatMode`（见上方示例）。

行为：

* 出站私信从不触发配对回复（防止骚扰联系人）。
* 入站未知发送者仍遵循 `channels.whatsapp.dmPolicy`。
* 自聊模式（allowFrom 包含你的号码）避免自动已读回执并忽略提及 JID。
* 非自聊私信发送已读回执。

## 已读回执

默认情况下，网关一旦接受入站 WhatsApp 消息，就会将其标记为已读（蓝勾）。

全局禁用：

json5

```
{
  channels: { whatsapp: { sendReadReceipts: false } }
}
```

按账号禁用：

json5

```
{
  channels: {
    whatsapp: {
      accounts: {
        personal: { sendReadReceipts: false }
      }
    }
  }
}
```

注意：

* 自聊模式始终跳过已读回执。

## WhatsApp 常见问题：发送消息 + 配对

**当我关联 WhatsApp 时，Clawdbot 会给随机联系人发消息吗？**  
不会。默认 DM 策略是 **配对**，所以未知发送者只会收到一个配对码，他们的消息**不会被处理**。Clawdbot 只回复它收到的聊天，或者你显式触发的发送（代理/CLI）。

**配对在 WhatsApp 上如何工作？**  
配对是针对未知发送者的私信门禁：

* 来自新发送者的第一条私信返回一个短代码（消息未处理）。
* 批准命令：`openclaw-cn pairing approve whatsapp <code>`（查看列表 `openclaw-cn pairing list whatsapp`）。
* 代码 1 小时后过期；每个频道的待处理请求上限为 3 个。

**多个人可以在同一个 WhatsApp 号码上使用不同的 Clawdbot 吗？**  
可以，通过 `bindings` 将每个发送者路由到不同的代理（peer `kind: "dm"`, 发送者 E.164 如 `+15551234567`）。回复仍然来自**同一个 WhatsApp 账号**，并且直接聊天会折叠到每个代理的主会话，所以**每人使用一个代理**。DM 访问控制 (`dmPolicy`/`allowFrom`) 是每个 WhatsApp 账号全局的。参见 [多代理路由](/concepts/multi-agent.html)。

**为什么向导会询问我的电话号码？**  
向导使用它来设置你的 **白名单/所有者**，以便允许你自己的私信。它不用于自动发送。如果你在个人 WhatsApp 号码上运行，请使用相同的号码并启用 `channels.whatsapp.selfChatMode`。

## 消息标准化（模型看到的内容）

* `Body` 是当前消息体及信封。
* 引用回复上下文**始终附加**：

  ```
  [Replying to +1555 id:ABC123]
  <quoted text or <media:...>>
  [/Replying]
  ```
* 回复元数据也会设置：
  + `ReplyToId` = stanzaId
  + `ReplyToBody` = 引用内容或媒体占位符
  + `ReplyToSender` = E.164（如果已知）
* 仅媒体的入站消息使用占位符：
  + `<media:image|video|audio|document|sticker>`

## 群组

* 群组映射到 `agent:<agentId>:whatsapp:group:<jid>` 会话。
* 群组策略：`channels.whatsapp.groupPolicy = open|disabled|allowlist`（默认 `allowlist`）。
* 激活模式：
  + `mention`（默认）：需要 @提及 或正则匹配。
  + `always`：总是触发。
* `/activation mention|always` 仅限所有者使用，必须作为独立消息发送。
* 所有者 = `channels.whatsapp.allowFrom`（如果未设置则为自身 E.164）。
* **历史注入**（仅待处理）：
  + 最近的*未处理*消息（默认 50 条）插入到：`[Chat messages since your last reply - for context]` 下（会话中已有的消息不会重新注入）
  + 当前消息在：`[Current message - respond to this]` 下
  + 附加发送者后缀：`[from: Name (+E164)]`
* 群组元数据缓存 5 分钟（主题 + 参与者）。

## 回复投递（线程）

* WhatsApp Web 发送标准消息（当前网关不支持引用回复线程）。
* 此频道忽略回复标签。

## 确认回应（收到时自动回应）

WhatsApp 可以在收到消息后立即自动发送 emoji 回应，在机器人生成回复之前。这为用户提供了消息已接收的即时反馈。

**配置：**

json

```
{
  "whatsapp": {
    "ackReaction": {
      "emoji": "👀",
      "direct": true,
      "group": "mentions"
    }
  }
}
```

**选项：**

* `emoji`（字符串）：用于确认的 Emoji（例如 "👀", "✅", "📨"）。为空或省略 = 功能禁用。
* `direct`（布尔值，默认：`true`）：在私信/DM 聊天中发送回应。
* `group`（字符串，默认：`"mentions"`）：群聊行为：
  + `"always"`：回应所有群组消息（即使没有 @提及）
  + `"mentions"`：仅当机器人被 @提及 时回应
  + `"never"`：在群组中从不回应

**按账号覆盖：**

json

```
{
  "whatsapp": {
    "accounts": {
      "work": {
        "ackReaction": {
          "emoji": "✅",
          "direct": false,
          "group": "always"
        }
      }
    }
  }
}
```

**行为说明：**

* 回应在收到消息时**立即**发送，在输入指示器或机器人回复之前。
* 在 `requireMention: false`（激活：总是）的群组中，`group: "mentions"` 将回应所有消息（不仅仅是 @提及）。
* 即发即弃：回应失败会被记录，但不会阻止机器人回复。
* 群组回应会自动包含参与者 JID。
* WhatsApp 忽略 `messages.ackReaction`；请使用 `channels.whatsapp.ackReaction` 代替。

## 代理工具（回应）

* 工具：`whatsapp` 的 `react` 动作 (`chatJid`, `messageId`, `emoji`, 可选 `remove`)。
* 可选：`participant`（群组发送者），`fromMe`（回应你自己的消息），`accountId`（多账号）。
* 回应移除语义：参见 [/tools/reactions](/tools/reactions.html)。
* 工具门控：`channels.whatsapp.actions.reactions`（默认：启用）。

## 限制

* 出站文本被分块为 `channels.whatsapp.textChunkLimit`（默认 4000）。
* 可选换行分块：设置 `channels.whatsapp.chunkMode="newline"` 以在长度分块之前按空行（段落边界）拆分。
* 入站媒体保存上限为 `channels.whatsapp.mediaMaxMb`（默认 50 MB）。
* 出站媒体项目上限为 `agents.defaults.mediaMaxMb`（默认 5 MB）。

## 出站发送（文本 + 媒体）

* 使用活动 web 监听器；如果网关未运行则报错。
* 文本分块：每条消息最大 4k（可通过 `channels.whatsapp.textChunkLimit` 配置，可选 `channels.whatsapp.chunkMode`）。
* 媒体：
  + 支持图片/视频/音频/文档。
  + 音频作为 PTT 发送；`audio/ogg` => `audio/ogg; codecs=opus`。
  + 仅第一个媒体项目有说明文字。
  + 媒体获取支持 HTTP(S) 和本地路径。
  + 动画 GIF：WhatsApp 需要 `gifPlayback: true` 的 MP4 才能实现内联循环。
    - CLI: `openclaw-cn message send --media <mp4> --gif-playback`
    - Gateway: `send` 参数包含 `gifPlayback: true`

## 语音笔记（PTT 音频）

WhatsApp 将音频作为 **语音笔记**（PTT 气泡）发送。

* 最佳结果：OGG/Opus。Clawdbot 将 `audio/ogg` 重写为 `audio/ogg; codecs=opus`。
* `[[audio_as_voice]]` 在 WhatsApp 中被忽略（音频已经作为语音笔记发送）。

## 媒体限制 + 优化

* 默认出站上限：5 MB（每个媒体项目）。
* 覆盖：`agents.defaults.mediaMaxMb`。
* 图片自动优化为上限内的 JPEG（调整大小 + 质量扫描）。
* 超大媒体 => 错误；媒体回复回退到文本警告。

## 心跳

* **网关心跳** 记录连接健康状况 (`web.heartbeatSeconds`, 默认 60s)。
* **代理心跳** 可以按代理配置 (`agents.list[].heartbeat`) 或通过 `agents.defaults.heartbeat` 全局配置（当没有设置按代理条目时作为回退）。
  + 使用配置的心跳提示（默认：`Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`）+ `HEARTBEAT_OK` 跳过行为。
  + 投递默认为上次使用的频道（或配置的目标）。

## 重连行为

* 退避策略：`web.reconnect`：
  + `initialMs`, `maxMs`, `factor`, `jitter`, `maxAttempts`.
* 如果达到 maxAttempts，web 监控停止（降级）。
* 注销 => 停止并需要重新关联。

## 配置快速映射

* `channels.whatsapp.dmPolicy`（DM 策略：配对/白名单/开放/禁用）。
* `channels.whatsapp.selfChatMode`（同手机设置；机器人使用你的个人 WhatsApp 号码）。
* `channels.whatsapp.allowFrom`（DM 白名单）。WhatsApp 使用 E.164 电话号码（无用户名）。
* `channels.whatsapp.mediaMaxMb`（入站媒体保存上限）。
* `channels.whatsapp.ackReaction`（收到消息时自动回应：`{emoji, direct, group}`）。
* `channels.whatsapp.accounts.<accountId>.*`（按账号设置 + 可选 `authDir`）。
* `channels.whatsapp.accounts.<accountId>.mediaMaxMb`（按账号入站媒体上限）。
* `channels.whatsapp.accounts.<accountId>.ackReaction`（按账号确认回应覆盖）。
* `channels.whatsapp.groupAllowFrom`（群组发送者白名单）。
* `channels.whatsapp.groupPolicy`（群组策略）。
* `channels.whatsapp.historyLimit` / `channels.whatsapp.accounts.<accountId>.historyLimit`（群组历史上下文；`0` 禁用）。
* `channels.whatsapp.dmHistoryLimit`（DM 历史限制，按用户轮次）。按用户覆盖：`channels.whatsapp.dms["<phone>"].historyLimit`。
* `channels.whatsapp.groups`（群组白名单 + 提及门控默认值；使用 `"*"` 允许所有）
* `channels.whatsapp.actions.reactions`（门控 WhatsApp 工具回应）。
* `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）
* `messages.groupChat.historyLimit`
* `channels.whatsapp.messagePrefix`（入站前缀；按账号：`channels.whatsapp.accounts.<accountId>.messagePrefix`；已弃用：`messages.messagePrefix`）
* `messages.responsePrefix`（出站前缀）
* `agents.defaults.mediaMaxMb`
* `agents.defaults.heartbeat.every`
* `agents.defaults.heartbeat.model`（可选覆盖）
* `agents.defaults.heartbeat.target`
* `agents.defaults.heartbeat.to`
* `agents.defaults.heartbeat.session`
* `agents.list[].heartbeat.*`（按代理覆盖）
* `session.*`（范围，空闲，存储，主键）
* `web.enabled`（为 false 时禁用频道启动）
* `web.heartbeatSeconds`
* `web.reconnect.*`

## 日志 + 故障排除

* 子系统：`whatsapp/inbound`, `whatsapp/outbound`, `web-heartbeat`, `web-reconnect`。
* 日志文件：`/tmp/clawdbot/clawdbot-YYYY-MM-DD.log`（可配置）。
* 故障排除指南：[Gateway troubleshooting](/gateway/troubleshooting.html)。

## 故障排除（快速）

**未关联 / 需要扫码登录**

* 症状：`channels status` 显示 `linked: false` 或警告 “Not linked”。
* 修复：在网关主机上运行 `openclaw-cn channels login` 并扫描二维码（WhatsApp → 设置 → 已关联设备）。

**已关联但断开连接 / 重连循环**

* 症状：`channels status` 显示 `running, disconnected` 或警告 “Linked but disconnected”。
* 修复：`clawdbot doctor`（或重启网关）。如果问题持续，通过 `channels login` 重新关联并检查 `clawdbot logs --follow`。

**Bun 运行时**

* Bun **不推荐**。WhatsApp (Baileys) 和 Telegram 在 Bun 上不可靠。请使用 **Node** 运行网关。（参见入门指南运行时说明。）
