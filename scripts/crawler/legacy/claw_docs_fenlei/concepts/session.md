# 会话

Source: https://clawd.org.cn/concepts/session.html

# 会话管理 (Session Management)

Clawdbot 将**每个智能体的一个直接聊天会话**视为主要会话。直接聊天会折叠为 `agent:<agentId>:<mainKey>`（默认为 `main`），而群组/频道聊天会有自己的键。`session.mainKey` 会被遵守。

使用 `session.dmScope` 来控制**私信 (Direct Messages)** 的分组方式：

* `main` (默认)：所有私信共享主会话以保持连续性。
* `per-peer`：跨频道按发送者 ID 隔离。
* `per-channel-peer`：按频道 + 发送者隔离（推荐用于多用户收件箱）。使用 `session.identityLinks` 将带提供商前缀的对等方 ID 映射到规范身份，以便在使用 `per-peer` 或 `per-channel-peer` 时，同一人在不同频道间共享一个 DM 会话。

## 网关是事实来源 (Gateway is the source of truth)

所有会话状态都由**网关拥有**（“主” Clawdbot）。UI 客户端（macOS 应用程序、WebChat 等）必须向网关查询会话列表和令牌计数，而不是读取本地文件。

* 在**远程模式**下，你关心的会话存储位于远程网关主机上，而不是你的 Mac 上。
* UI 中显示的令牌计数来自网关的存储字段（`inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`）。客户端不会解析 JSONL 记录来“修正”总数。

## 状态存储位置

* 在**网关主机**上：
  + 存储文件：`~/.openclaw/agents/<agentId>/sessions/sessions.json`（每个智能体）。
* 会话记录 (Transcripts)：`~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`（Telegram 主题会话使用 `.../<SessionId>-topic-<threadId>.jsonl`）。
* 存储是一个映射 `sessionKey -> { sessionId, updatedAt, ... }`。删除条目是安全的；它们会按需重新创建。
* 群组条目可能包含 `displayName`, `channel`, `subject`, `room`, 和 `space` 以在 UI 中标记会话。
* 会话条目包含 `origin` 元数据（标签 + 路由提示），以便 UI 可以解释会话的来源。
* Clawdbot **不**读取旧的 Pi/Tau 会话文件夹。

## 会话修剪 (Session pruning)

默认情况下，Clawdbot 会在调用 LLM 之前从内存上下文中修剪**旧的工具结果**。这**不**会重写 JSONL 历史记录。参见 [/concepts/session-pruning](/concepts/session-pruning.html)。

## 压缩前记忆刷新 (Pre-compaction memory flush)

当会话接近自动压缩时，Clawdbot 可以运行一个**静默记忆刷新**回合，提醒模型将持久性笔记写入磁盘。这仅在工作区可写时运行。参见 [记忆](/concepts/memory.html) 和 [压缩](/concepts/compaction.html)。

## 映射传输 → 会话键 (Mapping transports → session keys)

* 直接聊天遵循 `session.dmScope`（默认 `main`）。
  + `main`: `agent:<agentId>:<mainKey>`（跨设备/频道的连续性）。
    - 多个电话号码和频道可以映射到同一个智能体主键；它们作为同一个对话的传输通道。
  + `per-peer`: `agent:<agentId>:dm:<peerId>`。
  + `per-channel-peer`: `agent:<agentId>:<channel>:dm:<peerId>`。
  + 如果 `session.identityLinks` 匹配带提供商前缀的对等方 ID（例如 `telegram:123`），规范键将替换 `<peerId>`，以便同一人在不同频道间共享会话。
* 群聊隔离状态：`agent:<agentId>:<channel>:group:<id>`（房间/频道使用 `agent:<agentId>:<channel>:channel:<id>`）。
  + Telegram 论坛主题在群组 ID 后附加 `:topic:<threadId>` 以进行隔离。
  + 旧的 `group:<id>` 键仍被识别以便迁移。
* 入站上下文可能仍使用 `group:<id>`；频道从 `Provider` 推断并标准化为规范的 `agent:<agentId>:<channel>:group:<id>` 形式。
* 其他来源：
  + Cron 作业：`cron:<job.id>`
  + Webhooks：`hook:<uuid>`（除非由 hook 显式设置）
  + Node 运行：`node-<nodeId>`

## 生命周期 (Lifecycle)

* 重置策略：会话会被重用直到过期，过期评估在下一条入站消息时进行。
* 每日重置：默认为**网关主机本地时间凌晨 4:00**。如果会话的最后更新早于最近的每日重置时间，则该会话过期。
* 空闲重置（可选）：`idleMinutes` 添加一个滑动空闲窗口。当配置了每日重置和空闲重置时，**先过期的那个**强制开启新会话。
* 仅旧版空闲：如果你设置了 `session.idleMinutes` 而没有设置任何 `session.reset`/`resetByType` 配置，Clawdbot 保持在仅空闲模式以保持向后兼容性。
* 按类型覆盖（可选）：`resetByType` 允许你覆盖 `dm`, `group`, 和 `thread` 会话的策略（thread = Slack/Discord 线程，Telegram 主题，以及连接器提供的 Matrix 线程）。
* 按频道覆盖（可选）：`resetByChannel` 覆盖频道的重置策略（适用于该频道的所有会话类型，并优先于 `reset`/`resetByType`）。
* 重置触发器：精确的 `/new` 或 `/reset`（加上 `resetTriggers` 中的任何额外内容）启动一个新的会话 ID 并传递消息的其余部分。`/new <model>` 接受模型别名、`provider/model` 或提供商名称（模糊匹配）以设置新会话的模型。如果单独发送 `/new` 或 `/reset`，Clawdbot 会运行一个简短的“你好”问候回合以确认重置。
* 手动重置：从存储中删除特定键或删除 JSONL 记录；下一条消息将重新创建它们。
* 隔离的 cron 作业每次运行总是生成一个新的 `sessionId`（不重用空闲会话）。

## 发送策略 (可选)

阻止特定会话类型的投递，而无需列出单个 ID。

json5

```
{
  session: {
    sendPolicy: {
      rules: [
        { action: "deny", match: { channel: "discord", chatType: "group" } },
        { action: "deny", match: { keyPrefix: "cron:" } }
      ],
      default: "allow"
    }
  }
}
```

运行时覆盖（仅限所有者）：

* `/send on` → 允许此会话
* `/send off` → 拒绝此会话
* `/send inherit` → 清除覆盖并使用配置规则

作为独立消息发送这些指令以使其生效。

## 配置 (可选重命名示例)

json5

```
// ~/.openclaw/openclaw.json
{
  session: {
    scope: "per-sender",      // 保持群组键分离
    dmScope: "main",          // DM 连续性（对于共享收件箱设置为 per-channel-peer）
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"]
    },
    reset: {
      // 默认值：mode=daily, atHour=4 (网关主机本地时间)。
      // 如果你也设置了 idleMinutes，先过期的那个生效。
      mode: "daily",
      atHour: 4,
      idleMinutes: 120
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      dm: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 }
    },
    resetByChannel: {
      discord: { mode: "idle", idleMinutes: 10080 }
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    mainKey: "main",
  }
}
```

## 检查 (Inspecting)

* `clawdbot status` — 显示存储路径和最近的会话。
* `clawdbot sessions --json` — 转储每个条目（使用 `--active <minutes>` 过滤）。
* `clawdbot gateway call sessions.list --params '{}'` — 从运行中的网关获取会话（使用 `--url`/`--token` 进行远程网关访问）。
* 在聊天中作为独立消息发送 `/status` 以查看智能体是否可达、使用了多少会话上下文、当前的思考/详细开关，以及你的 WhatsApp web 凭据最后刷新的时间（有助于发现重新链接的需求）。
* 发送 `/context list` 或 `/context detail` 查看系统提示和注入的工作区文件中包含的内容（以及最大的上下文贡献者）。
* 作为独立消息发送 `/stop` 以中止当前运行，清除该会话的排队后续消息，并停止从中生成的任何子智能体运行（回复包含停止的计数）。
* 作为独立消息发送 `/compact`（可选指令）以总结旧的上下文并释放窗口空间。参见 [/concepts/compaction](/concepts/compaction.html)。
* JSONL 记录可以直接打开以查看完整的回合。

## 提示

* 保持主键专用于 1:1 流量；让群组保持自己的键。
* 自动化清理时，删除单个键而不是整个存储，以保留其他地方的上下文。

## 会话来源元数据 (Session origin metadata)

每个会话条目在 `origin` 中记录其来源（尽力而为）：

* `label`: 人类标签（从对话标签 + 群组主题/频道解析）
* `provider`: 标准化频道 ID（包括扩展名）
* `from`/`to`: 入站信封中的原始路由 ID
* `accountId`: 提供商帐户 ID（多帐户时）
* `threadId`: 线程/主题 ID（当频道支持时）

来源字段为私信、频道和群组填充。如果连接器仅更新投递路由（例如，为了保持 DM 主会话新鲜），它仍应提供入站上下文，以便会话保留其解释器元数据。扩展可以通过在入站上下文中发送 `ConversationLabel`, `GroupSubject`, `GroupChannel`, `GroupSpace`, 和 `SenderName` 并调用 `recordSessionMetaFromInbound`（或将相同的上下文传递给 `updateLastRoute`）来实现这一点。
