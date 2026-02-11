# Slack

Source: https://clawd.org.cn/channels/slack.html

# Slack

## Socket 模式 (默认)

### 快速设置 (新手)

1. 创建一个 Slack 应用并启用 **Socket Mode**。
2. 创建 **App Token** (`xapp-...`) 和 **Bot Token** (`xoxb-...`)。
3. 为 Clawdbot 设置令牌并启动 Gateway。

最小配置:

json5

```
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-..."
    }
  }
}
```

### 设置

1. 在 <https://api.slack.com/apps> 创建一个 Slack 应用 (从头开始)。
2. **Socket Mode** → 开启。然后去 **Basic Information** → **App-Level Tokens** → **Generate Token and Scopes**，添加 scope `connections:write`。复制 **App Token** (`xapp-...`)。
3. **OAuth & Permissions** → 添加 bot token scopes (使用下面的 manifest)。点击 **Install to Workspace**。复制 **Bot User OAuth Token** (`xoxb-...`)。
4. 可选: **OAuth & Permissions** → 添加 **User Token Scopes** (见下面的只读列表)。重新安装应用并复制 **User OAuth Token** (`xoxp-...`)。
5. **Event Subscriptions** → 启用事件并订阅:
   * `message.*` (包含编辑/删除/线程广播)
   * `app_mention`
   * `reaction_added`, `reaction_removed`
   * `member_joined_channel`, `member_left_channel`
   * `channel_rename`
   * `pin_added`, `pin_removed`
6. 将 bot 邀请到你希望它读取的频道。
7. Slash Commands → 如果你使用 `channels.slack.slashCommand`，创建 `/clawd`。如果你启用原生命令，为每个内置命令添加一个 slash command (名称与 `/help` 相同)。对于 Slack，原生命令默认为关闭，除非你设置 `channels.slack.commands.native: true` (全局 `commands.native` 是 `"auto"`，这会让 Slack 保持关闭)。
8. App Home → 启用 **Messages Tab** 以便用户可以私信 bot。

使用下面的 manifest 以保持 scopes 和事件同步。

多账户支持: 使用 `channels.slack.accounts`，配合每个账户的令牌和可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration.html#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

### Clawdbot 配置 (最小化)

通过环境变量设置令牌 (推荐):

* `SLACK_APP_TOKEN=xapp-...`
* `SLACK_BOT_TOKEN=xoxb-...`

或者通过配置:

json5

```
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-..."
    }
  }
}
```

### 用户令牌 (可选)

Clawdbot 可以使用 Slack 用户令牌 (`xoxp-...`) 进行读取操作 (历史记录, 置顶, 反应, emoji, 成员信息)。默认情况下，这保持只读：读取时如果存在用户令牌则优先使用，写入时除非你显式选择，否则仍使用 bot 令牌。即使 `userTokenReadOnly: false`，当 bot 令牌可用时，仍首选 bot 令牌进行写入。

用户令牌在配置文件中配置 (不支持环境变量)。对于多账户，设置 `channels.slack.accounts.<id>.userToken`。

bot + app + user tokens 的示例:

json5

```
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-...",
      userToken: "xoxp-..."
    }
  }
}
```

显式设置 `userTokenReadOnly` (允许用户令牌写入) 的示例:

json5

```
{
  channels: {
    slack: {
      enabled: true,
      appToken: "xapp-...",
      botToken: "xoxb-...",
      userToken: "xoxp-...",
      userTokenReadOnly: false
    }
  }
}
```

#### 令牌使用

* 读取操作 (历史记录, 反应列表, 置顶列表, emoji 列表, 成员信息, 搜索) 在配置时优先使用用户令牌，否则使用 bot 令牌。
* 写入操作 (发送/编辑/删除消息, 添加/移除反应, 置顶/取消置顶, 文件上传) 默认使用 bot 令牌。如果 `userTokenReadOnly: false` 且没有 bot 令牌可用，Clawdbot 回退到用户令牌。

### 历史上下文

* `channels.slack.historyLimit` (或 `channels.slack.accounts.*.historyLimit`) 控制有多少最近的频道/群组消息被包装到提示词中。
* 回退到 `messages.groupChat.historyLimit`。设置为 `0` 以禁用 (默认 50)。

## HTTP 模式 (Events API)

当你的 Gateway 可以通过 HTTPS 被 Slack 访问时 (典型的服务器部署)，使用 HTTP webhook 模式。HTTP 模式使用 Events API + Interactivity + Slash Commands 共享一个请求 URL。

### 设置

1. 创建一个 Slack 应用并 **禁用 Socket Mode** (如果你只使用 HTTP 则是可选的)。
2. **Basic Information** → 复制 **Signing Secret**。
3. **OAuth & Permissions** → 安装应用并复制 **Bot User OAuth Token** (`xoxb-...`)。
4. **Event Subscriptions** → 启用事件并将 **Request URL** 设置为你的 gateway webhook 路径 (默认 `/slack/events`)。
5. **Interactivity & Shortcuts** → 启用并设置相同的 **Request URL**。
6. **Slash Commands** → 为你的命令设置相同的 **Request URL**。

示例请求 URL: `https://gateway-host/slack/events`

### Clawdbot 配置 (最小化)

json5

```
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events"
    }
  }
}
```

多账户 HTTP 模式: 设置 `channels.slack.accounts.<id>.mode = "http"` 并为每个账户提供唯一的 `webhookPath`，以便每个 Slack 应用可以指向其自己的 URL。

### Manifest (可选)

使用此 Slack app manifest 快速创建应用 (如果需要，调整名称/命令)。如果你计划配置用户令牌，请包含 user scopes。

json

```
{
  "display_information": {
    "name": "Clawdbot",
    "description": "Slack connector for Clawdbot"
  },
  "features": {
    "bot_user": {
      "display_name": "Clawdbot",
      "always_online": false
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/clawd",
        "description": "Send a message to Clawdbot",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "chat:write",
        "channels:history",
        "channels:read",
        "groups:history",
        "groups:read",
        "groups:write",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "users:read",
        "app_mentions:read",
        "reactions:read",
        "reactions:write",
        "pins:read",
        "pins:write",
        "emoji:read",
        "commands",
        "files:read",
        "files:write"
      ],
      "user": [
        "channels:history",
        "channels:read",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "mpim:history",
        "mpim:read",
        "users:read",
        "reactions:read",
        "pins:read",
        "emoji:read",
        "search:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "reaction_added",
        "reaction_removed",
        "member_joined_channel",
        "member_left_channel",
        "channel_rename",
        "pin_added",
        "pin_removed"
      ]
    }
  }
}
```

如果你启用原生命令，请为每个你想要暴露的命令添加一个 `slash_commands` 条目 (匹配 `/help` 列表)。使用 `channels.slack.commands.native` 进行覆盖。

## Scopes (当前 vs 可选)

Slack 的 Conversations API 是类型范围的：你只需要你实际接触的对话类型的 scopes (channels, groups, im, mpim)。参见 <https://docs.slack.dev/apis/web-api/using-the-conversations-api/> 了解概览。

### Bot 令牌 Scopes (必需)

* `chat:write` (通过 `chat.postMessage` 发送/更新/删除消息) <https://docs.slack.dev/reference/methods/chat.postMessage>
* `im:write` (通过 `conversations.open` 为用户 DM 打开私信) <https://docs.slack.dev/reference/methods/conversations.open>
* `channels:history`, `groups:history`, `im:history`, `mpim:history`<https://docs.slack.dev/reference/methods/conversations.history>
* `channels:read`, `groups:read`, `im:read`, `mpim:read`<https://docs.slack.dev/reference/methods/conversations.info>
* `users:read` (用户查找) <https://docs.slack.dev/reference/methods/users.info>
* `reactions:read`, `reactions:write` (`reactions.get` / `reactions.add`) <https://docs.slack.dev/reference/methods/reactions.get><https://docs.slack.dev/reference/methods/reactions.add>
* `pins:read`, `pins:write` (`pins.list` / `pins.add` / `pins.remove`) <https://docs.slack.dev/reference/scopes/pins.read><https://docs.slack.dev/reference/scopes/pins.write>
* `emoji:read` (`emoji.list`) <https://docs.slack.dev/reference/scopes/emoji.read>
* `files:write` (通过 `files.uploadV2` 上传) <https://docs.slack.dev/messaging/working-with-files/#upload>

### 用户令牌 Scopes (可选，默认只读)

如果你配置 `channels.slack.userToken`，在 **User Token Scopes** 下添加这些。

* `channels:history`, `groups:history`, `im:history`, `mpim:history`
* `channels:read`, `groups:read`, `im:read`, `mpim:read`
* `users:read`
* `reactions:read`
* `pins:read`
* `emoji:read`
* `search:read`

### 目前不需要 (但未来可能需要)

* `mpim:write` (仅当我们添加 group-DM 打开/DM 启动 via `conversations.open`)
* `groups:write` (仅当我们添加私有频道管理: 创建/重命名/邀请/归档)
* `chat:write.public` (仅当我们想要发布到 bot 不在其中的频道) <https://docs.slack.dev/reference/scopes/chat.write.public>
* `users:read.email` (仅当我们从 `users.info` 需要 email 字段) <https://docs.slack.dev/changelog/2017-04-narrowing-email-access>
* `files:read` (仅当我们开始列出/读取文件元数据)

## 配置

Slack 仅使用 Socket 模式 (没有 HTTP webhook 服务器)。提供两个令牌:

json

```
{
  "slack": {
    "enabled": true,
    "botToken": "xoxb-...",
    "appToken": "xapp-...",
    "groupPolicy": "allowlist",
    "dm": {
      "enabled": true,
      "policy": "pairing",
      "allowFrom": ["U123", "U456", "*"],
      "groupEnabled": false,
      "groupChannels": ["G123"],
      "replyToMode": "all"
    },
    "channels": {
      "C123": { "allow": true, "requireMention": true },
      "#general": {
        "allow": true,
        "requireMention": true,
        "users": ["U123"],
        "skills": ["search", "docs"],
        "systemPrompt": "Keep answers short."
      }
    },
    "reactionNotifications": "own",
    "reactionAllowlist": ["U123"],
    "replyToMode": "off",
    "actions": {
      "reactions": true,
      "messages": true,
      "pins": true,
      "memberInfo": true,
      "emojiList": true
    },
    "slashCommand": {
      "enabled": true,
      "name": "clawd",
      "sessionPrefix": "slack:slash",
      "ephemeral": true
    },
    "textChunkLimit": 4000,
    "mediaMaxMb": 20
  }
}
```

令牌也可以通过环境变量提供:

* `SLACK_BOT_TOKEN`
* `SLACK_APP_TOKEN`

Ack (确认) 反应通过 `messages.ackReaction` + `messages.ackReactionScope` 全局控制。使用 `messages.removeAckAfterReply` 在 bot 回复后清除 ack 反应。

## 限制

* 出站文本分块限制为 `channels.slack.textChunkLimit` (默认 4000)。
* 可选的换行符分块: 设置 `channels.slack.chunkMode="newline"` 在长度分块之前在空行 (段落边界) 处分割。
* 媒体上传上限为 `channels.slack.mediaMaxMb` (默认 20)。

## 回复线程化 (Reply threading)

默认情况下，Clawdbot 在主频道回复。使用 `channels.slack.replyToMode` 控制自动线程化:

| 模式 | 行为 |
| --- | --- |
| `off` | **默认。** 在主频道回复。仅当触发消息已经在线程中时才使用线程。 |
| `first` | 第一条回复进入线程 (在触发消息下方)，后续回复进入主频道。用于保持上下文可见同时避免线程混乱。 |
| `all` | 所有回复都进入线程。保持对话包含在内，但可能会降低可见性。 |

该模式适用于自动回复和 agent 工具调用 (`slack sendMessage`)。

### 按聊天类型线程化 (Per-chat-type threading)

你可以通过设置 `channels.slack.replyToModeByChatType` 为不同聊天类型配置不同的线程行为:

json5

```
{
  channels: {
    slack: {
      replyToMode: "off",        // 频道的默认值
      replyToModeByChatType: {
        direct: "all",           // 私信总是线程化
        group: "first"           // 群组私信/MPIM 第一条回复线程化
      },
    }
  }
}
```

支持的聊天类型:

* `direct`: 1:1 私信 (Slack `im`)
* `group`: 群组私信 / MPIMs (Slack `mpim`)
* `channel`: 标准频道 (公开/私有)

优先级:

1. `replyToModeByChatType.<chatType>`
2. `replyToMode`
