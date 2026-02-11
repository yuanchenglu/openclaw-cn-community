# 智能体

Source: https://clawd.org.cn/concepts/agent.html

# 智能体运行时 (Agent Runtime) 🤖

Clawdbot 运行一个源自 **p-mono** 的单一嵌入式智能体运行时。

## 工作区 (必选)

Clawdbot 使用单一的智能体工作区目录 (`agents.defaults.workspace`) 作为智能体工具和上下文的**唯一**工作目录 (`cwd`)。

推荐：如果 `~/.openclaw-cn/openclaw-cn.json` 不存在，使用 `clawdbot setup` 创建它并初始化工作区文件。

完整的工作区布局 + 备份指南：[智能体工作区](/concepts/agent-workspace.html)

如果启用了 `agents.defaults.sandbox`，非主会话可以在 `agents.defaults.sandbox.workspaceRoot` 下使用每个会话独立的工作区进行覆盖（参见 [网关配置](/gateway/configuration.html)）。

## 引导文件 (注入)

在 `agents.defaults.workspace` 中，Clawdbot 期望存在这些用户可编辑的文件：

* `AGENTS.md` — 操作说明 + “记忆”
* `SOUL.md` — 人设、边界、语气
* `TOOLS.md` — 用户维护的工具说明（例如 `imsg`, `sag`, 约定）
* `BOOTSTRAP.md` — 一次性的首次运行仪式（完成后删除）
* `IDENTITY.md` — 智能体名称/氛围/表情符号
* `USER.md` — 用户资料 + 首选称呼

在新会话的第一轮交互中，Clawdbot 会将这些文件的内容直接注入到智能体上下文中。

空文件会被跳过。大文件会被修剪和截断，并带有标记，以保持提示词精简（请阅读文件以获取完整内容）。

如果文件丢失，Clawdbot 会注入一个单行的“文件丢失”标记（并且 `clawdbot setup` 会创建一个安全的默认模板）。

`BOOTSTRAP.md` 仅针对**全新的工作区**创建（没有其他引导文件存在）。如果你在完成仪式后将其删除，以后的重启中不应再重新创建它。

要完全禁用引导文件创建（对于预先设定种子的工作区），请设置：

json5

```
{ agent: { skipBootstrap: true } }
```

## 内置工具

核心工具（读取/执行/编辑/写入及相关系统工具）始终可用，受工具策略限制。`apply_patch` 是可选的，并通过 `tools.exec.applyPatch` 进行门控。`TOOLS.md` **不**控制哪些工具存在；它只是关于你希望如何使用它们的指导。

## 技能

Clawdbot 从三个位置加载技能（名称冲突时工作区优先）：

* 捆绑 (Bundled)（随安装包提供）
* 托管/本地 (Managed/local)：`~/.openclaw/skills`
* 工作区 (Workspace)：`<workspace>/skills`

技能可以通过配置/环境变量进行门控（参见 [网关配置](/gateway/configuration.html) 中的 `skills`）。

## p-mono 集成

Clawdbot 重用了 p-mono 代码库的一部分（模型/工具），但**会话管理、发现和工具连接由 Clawdbot 拥有**。

* 没有 p-coding 智能体运行时。
* 不会查询 `~/.pi/agent` 或 `<workspace>/.pi` 设置。

## 会话

会话记录以 JSONL 格式存储在：

* `~/.openclaw/agents/<agentId>/sessions/<SessionId>.jsonl`

会话 ID 是稳定的，由 Clawdbot 选择。**不会**读取旧的 Pi/Tau 会话文件夹。

## 流式传输时的转向控制

当队列模式为 `steer` 时，入站消息会被注入到当前的运行中。队列会在**每次工具调用后**进行检查；如果存在排队的消息，当前助手消息中剩余的工具调用将被跳过（错误工具结果为 "Skipped due to queued user message."），然后排队的用户消息会在下一个助手响应之前被注入。

当队列模式为 `followup` 或 `collect` 时，入站消息会被保留，直到当前回合结束，然后以排队的有效负载开始新的智能体回合。有关模式 + 防抖/上限行为，请参见 [队列](/concepts/queue.html)。

块流式传输 (Block streaming) 在助手块完成后立即发送；**默认关闭** (`agents.defaults.blockStreamingDefault: "off"`)。通过 `agents.defaults.blockStreamingBreak` 调整边界（`text_end` vs `message_end`；默认为 text\_end）。使用 `agents.defaults.blockStreamingChunk` 控制软块分块（默认为 800–1200 字符；优先段落中断，然后是换行符；句子最后）。使用 `agents.defaults.blockStreamingCoalesce` 合并流式块以减少单行垃圾信息（发送前基于空闲的合并）。非 Telegram 频道需要显式的 `*.blockStreaming: true` 才能启用块回复。详细的工具摘要在工具启动时发出（无防抖）；控制 UI 通过智能体事件流式传输工具输出（如果可用）。更多详情：[流式传输 + 分块](/concepts/streaming.html)。

## 模型引用

配置中的模型引用（例如 `agents.defaults.model` 和 `agents.defaults.models`）通过在**第一个** `/` 处拆分来解析。

* 配置模型时使用 `provider/model`。
* 如果模型 ID 本身包含 `/`（OpenRouter 风格），请包含提供商前缀（例如：`openrouter/moonshotai/kimi-k2`）。
* 如果省略提供商，Clawdbot 将输入视为别名或**默认提供商**的模型（仅当模型 ID 中没有 `/` 时有效）。

## 配置 (最小)

至少设置：

* `agents.defaults.workspace`
* `channels.whatsapp.allowFrom` (强烈推荐)

---

*下一步：[群聊](/concepts/group-messages.html)* 🦞
