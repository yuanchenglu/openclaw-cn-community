# 多智能体

Source: https://clawd.org.cn/concepts/multi-agent.html

# 多智能体路由 (Multi-Agent Routing)

目标：在一个运行的网关中，拥有多个**隔离**的智能体（独立的工作区 + `agentDir` + 会话），以及多个频道帐户（例如两个 WhatsApp）。入站消息通过绑定路由到智能体。

## 什么是“一个智能体”？

一个**智能体**是一个完全限定范围的大脑，拥有自己的：

* **工作区**（文件、AGENTS.md/SOUL.md/USER.md、本地笔记、人设规则）。
* **状态目录** (`agentDir`) 用于认证配置文件、模型注册表和每个智能体的配置。
* **会话存储**（聊天记录 + 路由状态）位于 `~/.openclaw/agents/<agentId>/sessions`。

认证配置文件是**每个智能体独立**的。每个智能体读取自己的：

```
~/.openclaw/agents/<agentId>/agent/auth-profiles.json
```

主智能体的凭据**不会**自动共享。永远不要在智能体之间重用 `agentDir`（这会导致认证/会话冲突）。如果你想共享凭据，请将 `auth-profiles.json` 复制到另一个智能体的 `agentDir` 中。

技能是每个智能体通过每个工作区的 `skills/` 文件夹独立的，共享技能可从 `~/.openclaw/skills` 获取。参见 [技能：每智能体与共享](/tools/skills.html#per-agent-vs-shared-skills)。

网关可以托管**一个智能体**（默认）或并排托管**多个智能体**。

**工作区注意：** 每个智能体的工作区是**默认 cwd**，不是硬沙箱。相对路径在工作区内解析，但绝对路径可以访问其他主机位置，除非启用了沙箱。参见 [沙箱](/gateway/sandboxing.html)。

## 路径 (快速映射)

* 配置：`~/.openclaw-cn/openclaw-cn.json` (或 `OPENCLAW_CONFIG_PATH`)
* 状态目录：`~/.openclaw` (或 `OPENCLAW_STATE_DIR`)
* 工作区：`~/clawd` (或 `~/clawd-<agentId>`)
* 智能体目录：`~/.openclaw/agents/<agentId>/agent` (或 `agents.list[].agentDir`)
* 会话：`~/.openclaw/agents/<agentId>/sessions`

### 单智能体模式 (默认)

如果你什么都不做，Clawdbot 运行一个单一智能体：

* `agentId` 默认为 **`main`**。
* 会话键为 `agent:main:<mainKey>`。
* 工作区默认为 `~/clawd`（或 `~/clawd-<profile>` 当 `OPENCLAW_PROFILE` 设置时）。
* 状态默认为 `~/.openclaw/agents/main/agent`。

## 智能体助手

使用智能体向导添加一个新的隔离智能体：

bash

```
clawdbot agents add work
```

然后添加 `bindings`（或让向导来做）以路由入站消息。

验证：

bash

```
clawdbot agents list --bindings
```

## 多个智能体 = 多个人，多种个性

使用**多个智能体**，每个 `agentId` 变成一个**完全隔离的人设**：

* **不同的电话号码/帐户**（每个频道 `accountId`）。
* **不同的个性**（每个智能体的工作区文件如 `AGENTS.md` 和 `SOUL.md`）。
* **独立的认证 + 会话**（除非明确启用，否则没有串扰）。

这允许**多个人**共享一个网关服务器，同时保持他们的 AI “大脑”和数据隔离。

## 一个 WhatsApp 号码，多个人 (DM 拆分)

你可以将**不同的 WhatsApp 私信**路由到不同的智能体，同时保持在**一个 WhatsApp 帐户**上。通过 `peer.kind: "dm"` 匹配发送者 E.164（如 `+15551234567`）。回复仍然来自同一个 WhatsApp 号码（没有每个智能体的发送者身份）。

重要细节：直接聊天折叠到智能体的**主会话键**，因此真正的隔离需要**每人一个智能体**。

示例：

json5

```
{
  agents: {
    list: [
      { id: "alex", workspace: "~/clawd-alex" },
      { id: "mia", workspace: "~/clawd-mia" }
    ]
  },
  bindings: [
    { agentId: "alex", match: { channel: "whatsapp", peer: { kind: "dm", id: "+15551230001" } } },
    { agentId: "mia",  match: { channel: "whatsapp", peer: { kind: "dm", id: "+15551230002" } } }
  ],
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551230001", "+15551230002"]
    }
  }
}
```

注意：

* DM 访问控制是**每个 WhatsApp 帐户全局**的（配对/允许列表），而不是每个智能体。
* 对于共享群组，将群组绑定到一个智能体或使用 [广播群组](/broadcast-groups.html)。

## 路由规则 (消息如何选择智能体)

绑定是**确定性的**并且**最具体者获胜**：

1. `peer` 匹配（精确的 DM/群组/频道 id）
2. `guildId` (Discord)
3. `teamId` (Slack)
4. `accountId` 匹配频道
5. 频道级匹配 (`accountId: "*"`)
6. 回退到默认智能体 (`agents.list[].default`，否则为第一个列表条目，默认为 `main`)

## 多个帐户 / 电话号码

支持**多个帐户**的频道（例如 WhatsApp）使用 `accountId` 来标识每个登录。每个 `accountId` 可以路由到不同的智能体，因此一台服务器可以托管多个电话号码而不会混合会话。

## 概念

* `agentId`: 一个“大脑”（工作区、每个智能体的认证、每个智能体的会话存储）。
* `accountId`: 一个频道帐户实例（例如 WhatsApp 帐户 `"personal"` vs `"biz"`）。
* `binding`: 通过 `(channel, accountId, peer)` 和可选的 guild/team id 将入站消息路由到 `agentId`。
* 直接聊天折叠为 `agent:<agentId>:<mainKey>`（每个智能体“主”；`session.mainKey`）。

## 示例：两个 WhatsApp → 两个智能体

`~/.openclaw-cn/openclaw-cn.json` (JSON5):

js

```
{
  agents: {
    list: [
      {
        id: "home",
        default: true,
        name: "Home",
        workspace: "~/clawd-home",
        agentDir: "~/.openclaw/agents/home/agent",
      },
      {
        id: "work",
        name: "Work",
        workspace: "~/clawd-work",
        agentDir: "~/.openclaw/agents/work/agent",
      },
    ],
  },

  // 确定性路由：第一个匹配获胜（最具体的优先）。
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },

    // 可选的每个对等方覆盖（示例：发送特定群组到工作智能体）。
    {
      agentId: "work",
      match: {
        channel: "whatsapp",
        accountId: "personal",
        peer: { kind: "group", id: "1203630...@g.us" },
      },
    },
  ],

  // 默认关闭：智能体对智能体消息必须显式启用 + 允许列表。
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },

  channels: {
    whatsapp: {
      accounts: {
        personal: {
          // 可选覆盖。默认：~/.openclaw/credentials/whatsapp/personal
          // authDir: "~/.openclaw/credentials/whatsapp/personal",
        },
        biz: {
          // 可选覆盖。默认：~/.openclaw/credentials/whatsapp/biz
          // authDir: "~/.openclaw/credentials/whatsapp/biz",
        },
      },
    },
  },
}
```
