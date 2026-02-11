# iMessage

来源: https://clawd.org.cn/channels/imessage.html

# iMessage (imsg)

状态: 外部 CLI 集成。网关生成 `imsg rpc` (基于 stdio 的 JSON-RPC)。

## 快速设置（初学者）

1. 确保此 Mac 已登录信息应用。
2. 安装 `imsg`：
   * `brew install steipete/tap/imsg`
3. 配置 Clawdbot 的 `channels.imessage.cliPath` 和 `channels.imessage.dbPath`。
4. 启动网关并批准任何 macOS 提示（自动化 + 完全磁盘访问权限）。

最小配置：

json5

```
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "/usr/local/bin/imsg",
      dbPath: "/Users/<you>/Library/Messages/chat.db"
    }
  }
}
```

## 简介

* 由 macOS 上的 `imsg` 支持的 iMessage 频道。
* 确定性路由：回复始终返回到 iMessage。
* 私信共享代理的主会话；群组是隔离的 (`agent:<agentId>:imessage:group:<chat_id>`)。
* 如果一个多参与者线程到达时 `is_group=false`，你仍然可以使用 `channels.imessage.groups` 通过 `chat_id` 隔离它（参见下文“类群组线程”）。

## 配置写入

默认情况下，允许 iMessage 通过 `/config set|unset` 触发配置更新（需要 `commands.config: true`）。

禁用方法：

json5

```
{
  channels: { imessage: { configWrites: false } }
}
```

## 要求

* 已登录信息应用的 macOS。
* Clawdbot + `imsg` 的完全磁盘访问权限（访问信息数据库）。
* 发送时的自动化权限。
* `channels.imessage.cliPath` 可以指向任何代理 stdin/stdout 的命令（例如，通过 SSH 连接到另一台 Mac 并运行 `imsg rpc` 的包装脚本）。

## 设置（快速路径）

1. 确保此 Mac 已登录信息应用。
2. 配置 iMessage 并启动网关。

### 专用机器人 macOS 用户（用于隔离身份）

如果你希望机器人通过**单独的 iMessage 身份**发送（并保持个人信息干净），请使用专用的 Apple ID + 专用的 macOS 用户。

1. 创建一个专用的 Apple ID（例如：`my-cool-bot@icloud.com`）。
   * Apple 可能需要电话号码进行验证 / 双重认证。
2. 创建一个 macOS 用户（例如：`clawdshome`）并登录。
3. 在该 macOS 用户中打开信息应用，并使用机器人 Apple ID 登录 iMessage。
4. 启用远程登录（系统设置 → 通用 → 共享 → 远程登录）。
5. 安装 `imsg`：
   * `brew install steipete/tap/imsg`
6. 设置 SSH，使 `ssh <bot-macos-user>@localhost true` 无需密码即可工作。
7. 将 `channels.imessage.accounts.bot.cliPath` 指向一个以机器人用户身份运行 `imsg` 的 SSH 包装器。

首次运行说明：发送/接收可能需要在*机器人 macOS 用户*中进行 GUI 批准（自动化 + 完全磁盘访问权限）。如果 `imsg rpc` 卡住或退出，请登录该用户（屏幕共享有帮助），运行一次性命令 `imsg chats --limit 1` / `imsg send ...`，批准提示，然后重试。

示例包装器 (`chmod +x`)。将 `<bot-macos-user>` 替换为你的实际 macOS 用户名：

bash

```
#!/usr/bin/env bash
set -euo pipefail

# Run an interactive SSH once first to accept host keys:
#   ssh <bot-macos-user>@localhost true
exec /usr/bin/ssh -o BatchMode=yes -o ConnectTimeout=5 -T <bot-macos-user>@localhost \
  "/usr/local/bin/imsg" "$@"
```

配置示例：

json5

```
{
  channels: {
    imessage: {
      enabled: true,
      accounts: {
        bot: {
          name: "Bot",
          enabled: true,
          cliPath: "/path/to/imsg-bot",
          dbPath: "/Users/<bot-macos-user>/Library/Messages/chat.db"
        }
      }
    }
  }
}
```

对于单账号设置，请使用扁平选项 (`channels.imessage.cliPath`, `channels.imessage.dbPath`) 而不是 `accounts` 映射。

### 远程/SSH 变体（可选）

如果你想在另一台 Mac 上使用 iMessage，请将 `channels.imessage.cliPath` 设置为一个通过 SSH 在远程 macOS 主机上运行 `imsg` 的包装器。Clawdbot 只需要 stdio。

示例包装器：

bash

```
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

**远程附件：** 当 `cliPath` 通过 SSH 指向远程主机时，信息数据库中的附件路径引用远程机器上的文件。Clawdbot 可以通过设置 `channels.imessage.remoteHost` 自动通过 SCP 获取这些文件：

json5

```
{
  channels: {
    imessage: {
      cliPath: "~/imsg-ssh",                     // 远程 Mac 的 SSH 包装器
      remoteHost: "user@gateway-host",           // 用于 SCP 文件传输
      includeAttachments: true
    }
  }
}
```

如果未设置 `remoteHost`，Clawdbot 会尝试通过解析包装脚本中的 SSH 命令来自动检测它。建议显式配置以提高可靠性。

#### 通过 Tailscale 连接远程 Mac（示例）

如果网关运行在 Linux 主机/虚拟机上，但 iMessage 必须运行在 Mac 上，Tailscale 是最简单的桥梁：网关通过 tailnet 与 Mac 通信，通过 SSH 运行 `imsg`，并通过 SCP 传回附件。

架构：

```
┌──────────────────────────────┐          SSH (imsg rpc)          ┌──────────────────────────┐
│ 网关主机 (Linux/VM)            │──────────────────────────────────▶│ 带有 Messages + imsg 的 Mac │
│ - clawdbot gateway           │          SCP (attachments)        │ - Messages 已登录         │
│ - channels.imessage.cliPath  │◀──────────────────────────────────│ - 远程登录已启用             │
└──────────────────────────────┘                                   └──────────────────────────┘
              ▲
              │ Tailscale tailnet (主机名或 100.x.y.z)
              ▼
        user@gateway-host
```

具体配置示例（Tailscale 主机名）：

json5

```
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "~/.openclaw/scripts/imsg-ssh",
      remoteHost: "bot@mac-mini.tailnet-1234.ts.net",
      includeAttachments: true,
      dbPath: "/Users/bot/Library/Messages/chat.db"
    }
  }
}
```

示例包装器 (`~/.openclaw/scripts/imsg-ssh`)：

bash

```
#!/usr/bin/env bash
exec ssh -T bot@mac-mini.tailnet-1234.ts.net imsg "$@"
```

注意：

* 确保 Mac 已登录信息应用，并且已启用远程登录。
* 使用 SSH 密钥，以便 `ssh bot@mac-mini.tailnet-1234.ts.net` 无需提示即可工作。
* `remoteHost` 应与 SSH 目标匹配，以便 SCP 可以获取附件。
* 多账号支持：使用 `channels.imessage.accounts` 进行按账号配置和可选 `name`。参见 [`gateway/configuration`](/gateway/configuration.html#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。不要提交 `~/.openclaw-cn/openclaw-cn.json`（通常包含令牌）。

## 访问控制（私信 + 群组）

私信：

* 默认：`channels.imessage.dmPolicy = "pairing"`。
* 未知发送者会收到配对码；消息被忽略直到批准（代码 1 小时后过期）。
* 批准方式：
  + `openclaw-cn pairing list imessage`
  + `openclaw-cn pairing approve imessage <CODE>`
* 配对是 iMessage 私信的默认令牌交换方式。详情：[配对](/start/pairing.html)

群组：

* `channels.imessage.groupPolicy = open | allowlist | disabled`。
* 当设置为 `allowlist` 时，`channels.imessage.groupAllowFrom` 控制谁可以在群组中触发。
* 提及门控使用 `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`），因为 iMessage 没有原生提及元数据。
* 多代理覆盖：在 `agents.list[].groupChat.mentionPatterns` 上设置按代理模式。

## 工作原理（行为）

* `imsg` 流式传输消息事件；网关将它们标准化为共享频道信封。
* 回复始终路由回相同的聊天 ID 或句柄。

## 类群组线程 (`is_group=false`)

某些 iMessage 线程可能有多个参与者，但根据 Messages 存储聊天标识符的方式，到达时仍可能显示 `is_group=false`。

如果你在 `channels.imessage.groups` 下显式配置 `chat_id`，Clawdbot 将该线程视为“群组”用于：

* 会话隔离（独立的 `agent:<agentId>:imessage:group:<chat_id>` 会话键）
* 群组白名单 / 提及门控行为

示例：

json5

```
{
  channels: {
    imessage: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15555550123"],
      groups: {
        "42": { "requireMention": false }
      }
    }
  }
}
```

当你想要为特定线程使用隔离的个性/模型时，这很有用（参见 [多代理路由](/concepts/multi-agent.html)）。关于文件系统隔离，参见 [沙盒](/gateway/sandboxing.html)。

## 媒体 + 限制

* 通过 `channels.imessage.includeAttachments` 可选摄取附件。
* 通过 `channels.imessage.mediaMaxMb` 限制媒体上限。

## 限制

* 出站文本被分块为 `channels.imessage.textChunkLimit`（默认 4000）。
* 可选换行分块：设置 `channels.imessage.chunkMode="newline"` 以在长度分块之前按空行（段落边界）拆分。
* 媒体上传上限为 `channels.imessage.mediaMaxMb`（默认 16）。

## 寻址 / 投递目标

首选 `chat_id` 以获得稳定路由：

* `chat_id:123`（推荐）
* `chat_guid:...`
* `chat_identifier:...`
* 直接句柄：`imessage:+1555` / `sms:+1555` / `user@example.com`

列出聊天：

```
imsg chats --limit 20
```

## 配置参考 (iMessage)

完整配置：[配置](/gateway/configuration.html)

提供者选项：

* `channels.imessage.enabled`：启用/禁用频道启动。
* `channels.imessage.cliPath`：`imsg` 的路径。
* `channels.imessage.dbPath`：Messages 数据库路径。
* `channels.imessage.remoteHost`：当 `cliPath` 指向远程 Mac 时，用于 SCP 附件传输的 SSH 主机（例如 `user@gateway-host`）。如果未设置，从 SSH 包装器自动检测。
* `channels.imessage.service`: `imessage | sms | auto`。
* `channels.imessage.region`：短信区域。
* `channels.imessage.dmPolicy`: `pairing | allowlist | open | disabled`（默认：pairing）。
* `channels.imessage.allowFrom`：DM 白名单（句柄、电子邮件、E.164 号码或 `chat_id:*`）。`open` 需要 `"*"`。iMessage 没有用户名；使用句柄或聊天目标。
* `channels.imessage.groupPolicy`: `open | allowlist | disabled`（默认：allowlist）。
* `channels.imessage.groupAllowFrom`：群组发送者白名单。
* `channels.imessage.historyLimit` / `channels.imessage.accounts.*.historyLimit`：作为上下文包含的最大群组消息数（0 禁用）。
* `channels.imessage.dmHistoryLimit`：DM 历史限制，按用户轮次。按用户覆盖：`channels.imessage.dms["<handle>"].historyLimit`。
* `channels.imessage.groups`：按群组默认值 + 白名单（使用 `"*"` 作为全局默认值）。
* `channels.imessage.includeAttachments`：将附件摄入上下文。
* `channels.imessage.mediaMaxMb`：入站/出站媒体上限 (MB)。
* `channels.imessage.textChunkLimit`：出站分块大小（字符）。
* `channels.imessage.chunkMode`: `length`（默认）或 `newline`，在长度分块之前按空行（段落边界）拆分。

相关全局选项：

* `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）。
* `messages.responsePrefix`。
