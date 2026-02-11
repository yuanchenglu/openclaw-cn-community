# Discord

Source: https://clawd.org.cn/channels/discord.html

# Discord (Bot API)

状态：支持通过官方 Discord bot gateway 进行私信和群组文字频道聊天。

## 快速设置 (入门)

1. 创建一个 Discord bot 并复制 bot token。
2. 为 Clawdbot 设置 token：
   * 环境变量：`DISCORD_BOT_TOKEN=...`
   * 或配置：`channels.discord.token: "..."`。
   * 如果两者都设置了，配置优先（环境变量仅作为默认账户的回退）。
3. 将 bot 邀请到你的服务器并授予消息权限。
4. 启动网关。
5. 私信访问默认为配对模式（pairing）；在第一次联系时批准配对码。

最小配置：

json5

```
{
  channels: {
    discord: {
      enabled: true,
      token: "YOUR_BOT_TOKEN"
    }
  }
}
```

## 目标

* 通过 Discord 私信或群组频道与 Clawdbot 交谈。
* 直接聊天会汇入 agent 的主会话（默认为 `agent:main:main`）；群组频道作为 `agent:<agentId>:discord:channel:<channelId>` 保持隔离（显示名称使用 `discord:<guildSlug>#<channelSlug>`）。
* 群组私信默认被忽略；可通过 `channels.discord.dm.groupEnabled` 启用，并可选择通过 `channels.discord.dm.groupChannels` 进行限制。
* 保持路由确定性：回复总是回到它们来源的频道。

## 工作原理

1. 创建一个 Discord 应用 → Bot，启用你需要的 intents（私信 + 群组消息 + 消息内容），并获取 bot token。
2. 将 bot 邀请到你的服务器，并授予在你想要使用它的地方读取/发送消息所需的权限。
3. 使用 `channels.discord.token`（或作为回退的 `DISCORD_BOT_TOKEN`）配置 Clawdbot。
4. 运行网关；当有可用 token（配置优先，环境变量回退）且 `channels.discord.enabled` 不为 `false` 时，它会自动启动 Discord 频道。
   * 如果你更喜欢环境变量，设置 `DISCORD_BOT_TOKEN`（配置块是可选的）。
5. 直接聊天：投递时使用 `user:<id>`（或 `<@id>` 提及）；所有对话都落在共享的 `main` 会话中。裸数字 ID 是模棱两可的，会被拒绝。
6. 群组频道：使用 `channel:<channelId>` 进行投递。默认需要提及，可以按群组（guild）或按频道设置。
7. 直接聊天：通过 `channels.discord.dm.policy`（默认：`"pairing"`）默认安全。未知发送者会收到一个配对码（1小时后过期）；通过 `openclaw-cn pairing approve discord <code>` 批准。
   * 要保持旧的“对任何人开放”的行为：设置 `channels.discord.dm.policy="open"` 和 `channels.discord.dm.allowFrom=["*"]`。
   * 要强制白名单：设置 `channels.discord.dm.policy="allowlist"` 并在 `channels.discord.dm.allowFrom` 中列出发送者。
   * 要忽略所有私信：设置 `channels.discord.dm.enabled=false` 或 `channels.discord.dm.policy="disabled"`。
8. 群组私信默认被忽略；可通过 `channels.discord.dm.groupEnabled` 启用，并可选择通过 `channels.discord.dm.groupChannels` 进行限制。
9. 可选的群组规则：设置 `channels.discord.guilds`，以 guild id（首选）或 slug 为键，包含每个频道的规则。
10. 可选的原生命令：`commands.native` 默认为 `"auto"`（对 Discord/Telegram 开启，对 Slack 关闭）。通过 `channels.discord.commands.native: true|false|"auto"` 覆盖；`false` 会清除之前注册的命令。文本命令由 `commands.text` 控制，必须作为独立的 `/...` 消息发送。使用 `commands.useAccessGroups: false` 绕过命令的访问组检查。
    * 完整命令列表 + 配置：[Slash commands](/tools/slash-commands.html)
11. 可选的群组上下文历史：设置 `channels.discord.historyLimit`（默认 20，回退到 `messages.groupChat.historyLimit`），以便在回复提及消息时包含最后 N 条群组消息作为上下文。设置为 `0` 以禁用。
12. 反应：agent 可以通过 `discord` 工具触发反应（由 `channels.discord.actions.*` 控制）。
    * 反应移除语义：参见 [/tools/reactions](/tools/reactions.html)。
    * `discord` 工具仅在当前频道为 Discord 时暴露。
13. 原生命令使用隔离的会话键（`agent:<agentId>:discord:slash:<userId>`）而不是共享的 `main` 会话。

注意：名称 → id 解析使用群组成员搜索，需要 Server Members Intent；如果 bot 无法搜索成员，请使用 ids 或 `<@id>` 提及。注意：Slugs 是小写的，空格替换为 `-`。频道名称是 slug 化的，没有开头的 `#`。注意：群组上下文 `[from:]` 行包含 `author.tag` + `id`，以便轻松进行 ping-ready 回复。

## 配置写入

默认情况下，Discord 允许写入由 `/config set|unset` 触发的配置更新（需要 `commands.config: true`）。

禁用方法：

json5

```
{
  channels: { discord: { configWrites: false } }
}
```

## 如何创建自己的机器人

这是在服务器（guild）频道（如 `#help`）中运行 Clawdbot 的“Discord Developer Portal”设置。

### 1) 创建 Discord 应用 + bot 用户

1. Discord Developer Portal → **Applications** → **New Application**
2. 在你的应用中：
   * **Bot** → **Add Bot**
   * 复制 **Bot Token**（这就是你放入 `DISCORD_BOT_TOKEN` 的内容）

### 2) 启用 Clawdbot 需要的网关 intents

Discord 会阻止“特权 intents”，除非你显式启用它们。

在 **Bot** → **Privileged Gateway Intents** 中，启用：

* **Message Content Intent**（在大多数群组中读取消息文本所必需；没有它你会看到“Used disallowed intents”或者 bot 会连接但不对消息做出反应）
* **Server Members Intent**（推荐；某些成员/用户查找和群组中的白名单匹配需要）

你通常**不**需要 **Presence Intent**。

### 3) 生成邀请 URL (OAuth2 URL Generator)

在你的应用中：**OAuth2** → **URL Generator**

**Scopes**

* ✅ `bot`
* ✅ `applications.commands`（原生命令需要）

**Bot Permissions** (最小基准)

* ✅ View Channels
* ✅ Send Messages
* ✅ Read Message History
* ✅ Embed Links
* ✅ Attach Files
* ✅ Add Reactions (可选但推荐)
* ✅ Use External Emojis / Stickers (可选；仅当你想要它们时)

避免 **Administrator**，除非你在调试并且完全信任该 bot。

复制生成的 URL，打开它，选择你的服务器，并安装 bot。

### 4) 获取 ids (guild/user/channel)

Discord 到处都使用数字 id；Clawdbot 配置首选 id。

1. Discord (桌面/网页) → **User Settings** → **Advanced** → 启用 **Developer Mode**
2. 右键点击：
   * 服务器名称 → **Copy Server ID** (guild id)
   * 频道 (例如 `#help`) → **Copy Channel ID**
   * 你的用户 → **Copy User ID**

### 5) 配置 Clawdbot

#### Token

通过环境变量设置 bot token（服务器上推荐）：

* `DISCORD_BOT_TOKEN=...`

或通过配置：

json5

```
{
  channels: {
    discord: {
      enabled: true,
      token: "YOUR_BOT_TOKEN"
    }
  }
}
```

多账户支持：使用 `channels.discord.accounts` 配置每个账户的 token 和可选的 `name`。参见 [`gateway/configuration`](/gateway/configuration.html#telegramaccounts--discordaccounts--slackaccounts--signalaccounts--imessageaccounts) 了解共享模式。

#### 白名单 + 频道路由

示例“单服务器，仅允许我，仅允许 #help”：

json5

```
{
  channels: {
    discord: {
      enabled: true,
      dm: { enabled: false },
      guilds: {
        "YOUR_GUILD_ID": {
          users: ["YOUR_USER_ID"],
          requireMention: true,
          channels: {
            help: { allow: true, requireMention: true }
          }
        }
      },
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1
      }
    }
  }
}
```

注意：

* `requireMention: true` 意味着 bot 仅在被提及时回复（推荐用于共享频道）。
* `agents.list[].groupChat.mentionPatterns`（或 `messages.groupChat.mentionPatterns`）也算作群组消息的提及。
* 多 agent 覆盖：在 `agents.list[].groupChat.mentionPatterns` 上设置每个 agent 的模式。
* 如果存在 `channels`，任何未列出的频道默认被拒绝。
* 使用 `"*"` 频道条目应用跨所有频道的默认值；显式频道条目覆盖通配符。
* 线程继承父频道配置（白名单，`requireMention`，技能，提示词等），除非你显式添加线程频道 id。
* bot 撰写的消息默认被忽略；设置 `channels.discord.allowBots=true` 以允许它们（自己的消息保持过滤）。
* 警告：如果你允许回复其他 bot（`channels.discord.allowBots=true`），请使用 `requireMention`，`channels.discord.guilds.*.channels.<id>.users` 白名单，和/或 `AGENTS.md` 和 `SOUL.md` 中的明确护栏来防止 bot 对 bot 的回复循环。

### 6) 验证是否工作

1. 启动网关。
2. 在你的服务器频道中，发送：`@Krill hello`（或者是你的 bot 名称）。
3. 如果什么都没发生：检查下面的 **故障排除**。

### 故障排除

* 首先：运行 `clawdbot doctor` 和 `openclaw-cn channels status --probe`（可操作的警告 + 快速审计）。
* **“Used disallowed intents”**：在 Developer Portal 中启用 **Message Content Intent**（可能还有 **Server Members Intent**），然后重启网关。
* **Bot 连接了但在群组频道中从不回复**：
  + 缺少 **Message Content Intent**，或
  + Bot 缺少频道权限（View/Send/Read History），或
  + 你的配置需要提及而你没有提及它，或
  + 你的 guild/channel 白名单拒绝了该频道/用户。
* **`requireMention: false` 但仍然没有回复**：
* `channels.discord.groupPolicy` 默认为 **allowlist**（白名单）；将其设置为 `"open"` 或在 `channels.discord.guilds` 下添加一个 guild 条目（可选地在 `channels.discord.guilds.<id>.channels` 下列出频道以进行限制）。
  + 如果你只设置了 `DISCORD_BOT_TOKEN` 而从未创建 `channels.discord` 部分，运行时默认 `groupPolicy` 为 `open`。添加 `channels.discord.groupPolicy`，`channels.defaults.groupPolicy`，或 guild/channel 白名单来锁定它。
* `requireMention` 必须位于 `channels.discord.guilds`（或特定频道）下。顶层的 `channels.discord.requireMention` 被忽略。
* **权限审计** (`channels status --probe`) 仅检查数字频道 ID。如果你使用 slugs/names 作为 `channels.discord.guilds.*.channels` 的键，审计无法验证权限。
* **私信不工作**：`channels.discord.dm.enabled=false`，`channels.discord.dm.policy="disabled"`，或者你还没有被批准（`channels.discord.dm.policy="pairing"`）。

## 能力 & 限制

* 私信和群组文字频道（线程被视为单独的频道；不支持语音）。
* 正在输入指示器尽力发送；消息分块使用 `channels.discord.textChunkLimit`（默认 2000）并按行数分割长回复（`channels.discord.maxLinesPerMessage`，默认 17）。
* 可选的换行分块：设置 `channels.discord.chunkMode="newline"` 以在长度分块之前按空行（段落边界）分割。
* 文件上传支持高达配置的 `channels.discord.mediaMaxMb`（默认 8 MB）。
* 默认提及门控群组回复以避免嘈杂的 bot。
* 当消息引用另一条消息时，注入回复上下文（引用内容 + ids）。
* 原生回复线程 **默认关闭**；通过 `channels.discord.replyToMode` 和 reply tags 启用。

## 重试策略

出站 Discord API 调用在速率限制 (429) 时重试，使用 Discord `retry_after`（如果可用），带有指数退避和抖动。通过 `channels.discord.retry` 配置。参见 [重试策略](/concepts/retry.html)。

## 配置

json5

```
{
  channels: {
    discord: {
      enabled: true,
      token: "abc.123",
      groupPolicy: "allowlist",
      guilds: {
        "*": {
          channels: {
            general: { allow: true }
          }
        }
      },
      mediaMaxMb: 8,
      actions: {
        reactions: true,
        stickers: true,
        emojiUploads: true,
        stickerUploads: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        channels: true,
        voiceStatus: true,
        events: true,
        moderation: false
      },
      replyToMode: "off",
      dm: {
        enabled: true,
        policy: "pairing", // pairing | allowlist | open | disabled
        allowFrom: ["123456789012345678", "steipete"],
        groupEnabled: false,
        groupChannels: ["clawd-dm"]
      },
      guilds: {
        "*": { requireMention: true },
        "123456789012345678": {
          slug: "friends-of-clawd",
          requireMention: false,
          reactionNotifications: "own",
          users: ["987654321098765432", "steipete"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"],
              skills: ["search", "docs"],
              systemPrompt: "Keep answers short."
            }
          }
        }
      }
    }
  }
}
```

Ack 反应通过 `messages.ackReaction` + `messages.ackReactionScope` 全局控制。使用 `messages.removeAckAfterReply` 在 bot 回复后清除 ack 反应。

* `dm.enabled`: 设置 `false` 以忽略所有私信（默认 `true`）。
* `dm.policy`: 私信访问控制（推荐 `pairing`）。`"open"` 需要 `dm.allowFrom=["*"]`。
* `dm.allowFrom`: 私信白名单（用户 id 或名称）。用于 `dm.policy="allowlist"` 和 `dm.policy="open"` 验证。wizard 接受用户名并在 bot 可以搜索成员时将其解析为 id。
* `dm.groupEnabled`: 启用群组私信（默认 `false`）。
* `dm.groupChannels`: 群组私信频道 id 或 slugs 的可选白名单。
* `groupPolicy`: 控制群组频道处理（`open|disabled|allowlist`）；`allowlist` 需要频道白名单。
* `guilds`: 按 guild id（首选）或 slug 为键的每 guild 规则。
* `guilds."*"`: 当不存在显式条目时应用的默认每 guild 设置。
* `guilds.<id>.slug`: 用于显示名称的可选友好 slug。
* `guilds.<id>.users`: 可选的每 guild 用户白名单（id 或名称）。
* `guilds.<id>.channels.<channel>.allow`: 当 `groupPolicy="allowlist"` 时允许/拒绝频道。
* `guilds.<id>.channels.<channel>.requireMention`: 频道的提及门控。
* `guilds.<id>.channels.<channel>.users`: 可选的每频道用户白名单。
* `guilds.<id>.channels.<channel>.skills`: 技能过滤器（省略 = 所有技能，空 = 无）。
* `guilds.<id>.channels.<channel>.systemPrompt`: 频道的额外系统提示词（与频道主题组合）。
* `guilds.<id>.channels.<channel>.enabled`: 设置 `false` 以禁用频道。
* `guilds.<id>.channels`: 频道规则（键是频道 slugs 或 id）。
* `guilds.<id>.requireMention`: 每 guild 提及要求（可按频道覆盖）。
* `guilds.<id>.reactionNotifications`: 反应系统事件模式（`off`, `own`, `all`, `allowlist`）。
* `textChunkLimit`: 出站文本分块大小（字符）。默认：2000。
* `chunkMode`: `length`（默认）仅在超过 `textChunkLimit` 时分割；`newline` 在长度分块之前按空行（段落边界）分割。
* `maxLinesPerMessage`: 每条消息的软最大行数。默认：17。
* `mediaMaxMb`: 限制保存到磁盘的入站媒体。
* `historyLimit`: 回复提及时作为上下文包含的最近群组消息数量（默认 20；回退到 `messages.groupChat.historyLimit`；`0` 禁用）。
* `dmHistoryLimit`: 用户轮次中的 DM 历史限制。每用户覆盖：`dms["<user_id>"].historyLimit`。
* `retry`: 出站 Discord API 调用的重试策略（attempts, minDelayMs, maxDelayMs, jitter）。
* `actions`: 每动作工具门控；省略以允许所有（设置 `false` 以禁用）。
  + `reactions` (涵盖 react + read reactions)
  + `stickers`, `emojiUploads`, `stickerUploads`, `polls`, `permissions`, `messages`, `threads`, `pins`, `search`
  + `memberInfo`, `roleInfo`, `channelInfo`, `voiceStatus`, `events`
  + `channels` (创建/编辑/删除频道 + 分类 + 权限)
  + `roles` (角色添加/移除，默认 `false`)
  + `moderation` (超时/踢出/封禁，默认 `false`)

反应通知使用 `guilds.<id>.reactionNotifications`：

* `off`: 无反应事件。
* `own`: bot 自己消息上的反应（默认）。
* `all`: 所有消息上的所有反应。
* `allowlist`: 来自 `guilds.<id>.users` 的反应（空列表禁用）。

### 工具动作默认值

| Action group | Default | Notes |
| --- | --- | --- |
| reactions | enabled | React + list reactions + emojiList |
| stickers | enabled | Send stickers |
| emojiUploads | enabled | Upload emojis |
| stickerUploads | enabled | Upload stickers |
| polls | enabled | Create polls |
| permissions | enabled | Channel permission snapshot |
| messages | enabled | Read/send/edit/delete |
| threads | enabled | Create/list/reply |
| pins | enabled | Pin/unpin/list |
| search | enabled | Message search (preview feature) |
| memberInfo | enabled | Member info |
| roleInfo | enabled | Role list |
| channelInfo | enabled | Channel info + list |
| channels | enabled | Channel/category management |
| voiceStatus | enabled | Voice state lookup |
| events | enabled | List/create scheduled events |
| roles | disabled | Role add/remove |
| moderation | disabled | Timeout/kick/ban |

* `replyToMode`: `off` (默认), `first`, 或 `all`。仅当模型包含 reply tag 时应用。

## Reply tags

要请求线程回复，模型可以在其输出中包含一个 tag：

* `[[reply_to_current]]` — 回复触发的 Discord 消息。
* `[[reply_to:<id>]]` — 回复上下文/历史中的特定消息 id。当前消息 id 作为 `[message_id: …]` 附加到提示词；历史条目已包含 id。

行为由 `channels.discord.replyToMode` 控制：

* `off`: 忽略 tags。
* `first`: 仅第一个出站块/附件是回复。
* `all`: 每个出站块/附件都是回复。

白名单匹配注意：

* `allowFrom`/`users`/`groupChannels` 接受 id，名称，标签，或像 `<@id>` 这样的提及。
* 支持像 `discord:`/`user:` (用户) 和 `channel:` (群组私信) 这样的前缀。
* 使用 `*` 允许任何发送者/频道。
* 当存在 `guilds.<id>.channels` 时，未列出的频道默认被拒绝。
* 当省略 `guilds.<id>.channels` 时，允许白名单 guild 中的所有频道。
* 要允许 **无频道**，设置 `channels.discord.groupPolicy: "disabled"`（或保持空的白名单）。
* configure wizard 接受 `Guild/Channel` 名称（公开 + 私有）并在可能时将它们解析为 ID。
* 启动时，Clawdbot 将白名单中的频道/用户名称解析为 ID（当 bot 可以搜索成员时）并记录映射；未解析的条目保持原样。

原生命令注意：

* 注册的命令反映了 Clawdbot 的聊天命令。
* 原生命令遵守与私信/群组消息相同的白名单（`channels.discord.dm.allowFrom`, `channels.discord.guilds`, 每频道规则）。
* Slash commands 可能仍然在 Discord UI 中对未在白名单中的用户可见；Clawdbot 在执行时强制执行白名单并回复“not authorized”。

## 工具动作

agent 可以使用 `discord` 调用如下动作：

* `react` / `reactions` (添加或列出反应)
* `sticker`, `poll`, `permissions`
* `readMessages`, `sendMessage`, `editMessage`, `deleteMessage`
* Read/search/pin 工具负载包含标准化的 `timestampMs` (UTC epoch ms) 和 `timestampUtc` 以及原始 Discord `timestamp`。
* `threadCreate`, `threadList`, `threadReply`
* `pinMessage`, `unpinMessage`, `listPins`
* `searchMessages`, `memberInfo`, `roleInfo`, `roleAdd`, `roleRemove`, `emojiList`
* `channelInfo`, `channelList`, `voiceStatus`, `eventList`, `eventCreate`
* `timeout`, `kick`, `ban`

Discord 消息 id 显露在注入的上下文（`[discord message id: …]` 和历史行）中，以便 agent 可以针对它们。Emoji 可以是 unicode（例如，`✅`）或自定义 emoji 语法如 `<:party_blob:1234567890>`。

## 安全 & 运维

* 像对待密码一样对待 bot token；在受监督的主机上首选 `DISCORD_BOT_TOKEN` 环境变量，或锁定配置文件权限。
* 仅授予 bot 需要的权限（通常是 Read/Send Messages）。
* 如果 bot 卡住或受速率限制，在确认没有其他进程拥有 Discord 会话后，重启网关（`clawdbot gateway --force`）。
