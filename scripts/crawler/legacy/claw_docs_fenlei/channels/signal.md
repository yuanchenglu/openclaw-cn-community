# Signal

Source: https://clawd.org.cn/channels/signal.html

# Signal (signal-cli)

状态: 外部 CLI 集成。Gateway 通过 HTTP JSON-RPC + SSE 与 `signal-cli` 通信。

## 快速设置 (新手)

1. 为 bot 使用一个 **独立的 Signal 号码** (推荐)。
2. 安装 `signal-cli` (需要 Java)。
3. 链接 bot 设备并启动守护进程:
   * `signal-cli link -n "Clawdbot"`
4. 配置 Clawdbot 并启动 Gateway。

最小配置:

json5

```
{
  channels: {
    signal: {
      enabled: true,
      account: "+15551234567",
      cliPath: "signal-cli",
      dmPolicy: "pairing",
      allowFrom: ["+15557654321"]
    }
  }
}
```

## 它是什么

* 通过 `signal-cli` 实现的 Signal 通道 (非嵌入式 libsignal)。
* 确定性路由: 回复总是回到 Signal。
* 私信共享 Agent 的主会话；群组是隔离的 (`agent:<agentId>:signal:group:<groupId>`)。

## 配置写入

默认情况下，允许 Signal 写入由 `/config set|unset` 触发的配置更新 (需要 `commands.config: true`)。

禁用方法:

json5

```
{
  channels: { signal: { configWrites: false } }
}
```

## 号码模型 (重要)

* Gateway 连接到一个 **Signal 设备** (`signal-cli` 账户)。
* 如果你在 **你的个人 Signal 账户** 上运行 bot，它会忽略你自己的消息 (循环保护)。
* 如果你想实现 "我发短信给 bot，它回复我"，请使用 **独立的 bot 号码**。

## 设置 (快速路径)

1. 安装 `signal-cli` (需要 Java)。
2. 链接 bot 账户:
   * `signal-cli link -n "Clawdbot"` 然后在 Signal 中扫描二维码。
3. 配置 Signal 并启动 Gateway。

示例:

json5

```
{
  channels: {
    signal: {
      enabled: true,
      account: "+15551234567",
      cliPath: "signal-cli",
      dmPolicy: "pairing",
      allowFrom: ["+15557654321"]
    }
  }
}
```

多账户支持: 使用 `channels.signal.accounts`，配合每个账户的配置和可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration.html#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

## 外部守护进程模式 (httpUrl)

如果你想自己管理 `signal-cli` (避免 JVM 冷启动慢、容器初始化或共享 CPU)，可以单独运行守护进程并将 Clawdbot 指向它:

json5

```
{
  channels: {
    signal: {
      httpUrl: "http://127.0.0.1:8080",
      autoStart: false
    }
  }
}
```

这会跳过 Clawdbot 内部的自动生成和启动等待。对于自动生成时启动较慢的情况，设置 `channels.signal.startupTimeoutMs`。

## 访问控制 (私信 + 群组)

私信 (DMs):

* 默认: `channels.signal.dmPolicy = "pairing"`。
* 未知发送者会收到配对码；消息被忽略直到批准 (代码 1 小时后过期)。
* 批准方式:
  + `openclaw-cn pairing list signal`
  + `openclaw-cn pairing approve signal <CODE>`
* 配对是 Signal 私信的默认令牌交换方式。详情: [配对](/start/pairing.html)
* 仅 UUID 的发送者 (来自 `sourceUuid`) 在 `channels.signal.allowFrom` 中存储为 `uuid:<id>`。

群组 (Groups):

* `channels.signal.groupPolicy = open | allowlist | disabled`。
* 当设置为 `allowlist` 时，`channels.signal.groupAllowFrom` 控制谁可以在群组中触发。

## 工作原理 (行为)

* `signal-cli` 作为守护进程运行；Gateway 通过 SSE 读取事件。
* 入站消息被标准化为共享通道信封。
* 回复总是路由回相同的号码或群组。

## 媒体 + 限制

* 出站文本分块限制为 `channels.signal.textChunkLimit` (默认 4000)。
* 可选的换行符分块: 设置 `channels.signal.chunkMode="newline"` 在长度分块之前在空行 (段落边界) 处分割。
* 支持附件 (从 `signal-cli` 获取 base64)。
* 默认媒体上限: `channels.signal.mediaMaxMb` (默认 8)。
* 使用 `channels.signal.ignoreAttachments` 跳过下载媒体。
* 群组历史上下文使用 `channels.signal.historyLimit` (或 `channels.signal.accounts.*.historyLimit`)，回退到 `messages.groupChat.historyLimit`。设置为 `0` 以禁用 (默认 50)。

## 正在输入 + 已读回执

* **正在输入指示器**: Clawdbot 通过 `signal-cli sendTyping` 发送正在输入信号，并在回复生成期间刷新它们。
* **已读回执**: 当 `channels.signal.sendReadReceipts` 为 true 时，Clawdbot 为允许的私信转发已读回执。
* Signal-cli 不暴露群组的已读回执。

## 反应 (消息工具)

* 使用 `message action=react` 且 `channel=signal`。
* 目标: 发送者 E.164 或 UUID (使用配对输出中的 `uuid:<id>`；也可以使用纯 UUID)。
* `messageId` 是你要反应的消息的 Signal 时间戳。
* 群组反应需要 `targetAuthor` 或 `targetAuthorUuid`。

示例:

```
message action=react channel=signal target=uuid:123e4567-e89b-12d3-a456-426614174000 messageId=1737630212345 emoji=🔥
message action=react channel=signal target=+15551234567 messageId=1737630212345 emoji=🔥 remove=true
message action=react channel=signal target=signal:group:<groupId> targetAuthor=uuid:<sender-uuid> messageId=1737630212345 emoji=✅
```

配置:

* `channels.signal.actions.reactions`: 启用/禁用反应动作 (默认 true)。
* `channels.signal.reactionLevel`: `off | ack | minimal | extensive`。
  + `off`/`ack` 禁用 Agent 反应 (消息工具 `react` 将报错)。
  + `minimal`/`extensive` 启用 Agent 反应并设置指导级别。
* 每个账户的覆盖: `channels.signal.accounts.<id>.actions.reactions`, `channels.signal.accounts.<id>.reactionLevel`。

## 投递目标 (CLI/cron)

* 私信: `signal:+15551234567` (或纯 E.164)。
* UUID 私信: `uuid:<id>` (或纯 UUID)。
* 群组: `signal:group:<groupId>`。
* 用户名: `username:<name>` (如果你的 Signal 账户支持)。

## 配置参考 (Signal)

完整配置: [Configuration](/gateway/configuration.html)

提供者选项:

* `channels.signal.enabled`: 启用/禁用通道启动。
* `channels.signal.account`: bot 账户的 E.164 号码。
* `channels.signal.cliPath`: `signal-cli` 的路径。
* `channels.signal.httpUrl`: 完整的守护进程 URL (覆盖 host/port)。
* `channels.signal.httpHost`, `channels.signal.httpPort`: 守护进程绑定 (默认 127.0.0.1:8080)。
* `channels.signal.autoStart`: 自动生成守护进程 (如果 `httpUrl` 未设置则默认 true)。
* `channels.signal.startupTimeoutMs`: 启动等待超时时间 (毫秒) (上限 120000)。
* `channels.signal.receiveMode`: `on-start | manual`。
* `channels.signal.ignoreAttachments`: 跳过附件下载。
* `channels.signal.ignoreStories`: 忽略来自守护进程的 stories。
* `channels.signal.sendReadReceipts`: 转发已读回执。
* `channels.signal.dmPolicy`: `pairing | allowlist | open | disabled` (默认: pairing)。
* `channels.signal.allowFrom`: 私信允许列表 (E.164 或 `uuid:<id>`)。`open` 需要 `"*"`. Signal 没有用户名；使用电话/UUID ids。
* `channels.signal.groupPolicy`: `open | allowlist | disabled` (默认: allowlist)。
* `channels.signal.groupAllowFrom`: 群组发送者允许列表。
* `channels.signal.historyLimit`: 包含为上下文的最大群组消息数 (0 禁用)。
* `channels.signal.dmHistoryLimit`: 私信历史限制 (用户轮次)。每个用户的覆盖: `channels.signal.dms["<phone_or_uuid>"].historyLimit`。
* `channels.signal.textChunkLimit`: 出站分块大小 (字符)。
* `channels.signal.chunkMode`: `length` (默认) 或 `newline` 在长度分块之前在空行 (段落边界) 处分割。
* `channels.signal.mediaMaxMb`: 入站/出站媒体上限 (MB)。
