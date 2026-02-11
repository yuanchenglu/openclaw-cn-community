# 记忆

Source: https://clawd.org.cn/concepts/memory.html

# 记忆 (Memory)

Clawdbot 的记忆是**智能体工作区中的纯 Markdown**。这些文件是事实来源；模型只“记得”被写入磁盘的内容。

记忆搜索工具由活动记忆插件提供（默认：`memory-core`）。使用 `plugins.slots.memory = "none"` 禁用记忆插件。

## 记忆文件 (Markdown)

默认的工作区布局使用两层记忆：

* `memory/YYYY-MM-DD.md`
  + 每日日志（仅追加）。
  + 在会话开始时读取今天 + 昨天的内容。
* `MEMORY.md` (可选)
  + 策划的长期记忆。
  + **仅在主、私有会话中加载**（绝不在群组上下文中加载）。

这些文件位于工作区下（`agents.defaults.workspace`，默认 `~/clawd`）。完整布局请参见 [智能体工作区](/concepts/agent-workspace.html)。

## 何时写入记忆

* 决定、偏好和持久性事实进入 `MEMORY.md`。
* 日常笔记和运行上下文进入 `memory/YYYY-MM-DD.md`。
* 如果有人说“记住这个”，把它写下来（不要只保留在 RAM 中）。
* 这个领域还在发展中。提醒模型存储记忆会有所帮助；它会知道该怎么做。
* 如果你想让某些东西保留下来，**要求机器人将其写入**记忆中。

## 自动记忆刷新 (压缩前 ping)

当会话**接近自动压缩**时，Clawdbot 会触发一个**静默的、智能体驱动的回合**，提醒模型在上下文被压缩**之前**写入持久性记忆。默认提示明确说明模型*可以回复*，但通常 `NO_REPLY` 是正确的响应，因此用户永远不会看到这个回合。

这由 `agents.defaults.compaction.memoryFlush` 控制：

json5

```
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store."
        }
      }
    }
  }
}
```

详情：

* **软阈值 (Soft threshold)**：当会话令牌估计超过 `contextWindow - reserveTokensFloor - softThresholdTokens` 时触发刷新。
* **静默 (Silent)**：默认情况下提示包含 `NO_REPLY`，因此不会投递任何内容。
* **两个提示**：一个用户提示加上一个系统提示附加提醒。
* **每个压缩周期一次刷新**（在 `sessions.json` 中跟踪）。
* **工作区必须可写**：如果会话在沙箱中运行且 `workspaceAccess: "ro"` 或 `"none"`，则跳过刷新。

有关完整的压缩生命周期，请参见 [会话管理 + 压缩](/reference/session-management-compaction.html)。

## 向量记忆搜索 (Vector memory search)

Clawdbot 可以在 `MEMORY.md` 和 `memory/*.md` 上构建一个小型向量索引，以便即使措辞不同，语义查询也能找到相关笔记。

默认值：

* 默认启用。
* 监视记忆文件的更改（防抖）。
* 默认使用远程嵌入。如果未设置 `memorySearch.provider`，Clawdbot 会自动选择：
  1. `local` 如果配置了 `memorySearch.local.modelPath` 且文件存在。
  2. `openai` 如果可以解析 OpenAI 密钥。
  3. `gemini` 如果可以解析 Gemini 密钥。
  4. 否则记忆搜索保持禁用状态，直到配置为止。
* 本地模式使用 node-llama-cpp，可能需要 `pnpm approve-builds`。
* 使用 sqlite-vec（如果可用）在 SQLite 内部加速向量搜索。

远程嵌入**需要**嵌入提供商的 API 密钥。Clawdbot 从认证配置文件、`models.providers.*.apiKey` 或环境变量中解析密钥。Codex OAuth 仅涵盖 chat/completions，**不**满足记忆搜索的嵌入需求。对于 Gemini，使用 `GEMINI_API_KEY` 或 `models.providers.google.apiKey`。当使用自定义 OpenAI 兼容端点时，设置 `memorySearch.remote.apiKey`（以及可选的 `memorySearch.remote.headers`）。

### Gemini 嵌入 (原生)

将提供商设置为 `gemini` 以直接使用 Gemini 嵌入 API：

json5

```
agents: {
  defaults: {
    memorySearch: {
      provider: "gemini",
      model: "gemini-embedding-001",
      remote: {
        apiKey: "YOUR_GEMINI_API_KEY"
      }
    }
  }
}
```

注意：

* `remote.baseUrl` 是可选的（默认为 Gemini API 基础 URL）。
* `remote.headers` 允许你在需要时添加额外的标头。
* 默认模型：`gemini-embedding-001`。

如果你想使用**自定义 OpenAI 兼容端点**（OpenRouter, vLLM, 或代理），你可以将 `remote` 配置与 OpenAI 提供商一起使用：

json5

```
agents: {
  defaults: {
    memorySearch: {
      provider: "openai",
      model: "text-embedding-3-small",
      remote: {
        baseUrl: "https://api.example.com/v1/",
        apiKey: "YOUR_OPENAI_COMPAT_API_KEY",
        headers: { "X-Custom-Header": "value" }
      }
    }
  }
}
```

如果你不想设置 API 密钥，请使用 `memorySearch.provider = "local"` 或设置 `memorySearch.fallback = "none"`。

回退 (Fallbacks)：

* `memorySearch.fallback` 可以是 `openai`, `gemini`, `local`, 或 `none`。
* 回退提供商仅在主嵌入提供商失败时使用。

批量索引 (OpenAI + Gemini)：

* 对 OpenAI 和 Gemini 嵌入默认启用。设置 `agents.defaults.memorySearch.remote.batch.enabled = false` 以禁用。
* 默认行为等待批量完成；如果需要，调整 `remote.batch.wait`, `remote.batch.pollIntervalMs`, 和 `remote.batch.timeoutMinutes`。
* 设置 `remote.batch.concurrency` 以控制我们并行提交多少批量作业（默认：2）。
* 批量模式适用于 `memorySearch.provider = "openai"` 或 `"gemini"` 并使用相应的 API 密钥。
* Gemini 批量作业使用异步嵌入批量端点，需要 Gemini Batch API 可用性。

为什么 OpenAI 批量快速 + 便宜：

* 对于大型回填，OpenAI 通常是我们支持的最快选项，因为我们可以在单个批量作业中提交许多嵌入请求，并让 OpenAI 异步处理它们。
* OpenAI 为 Batch API 工作负载提供折扣定价，因此大型索引运行通常比同步发送相同请求便宜。
* 有关详情，请参阅 OpenAI Batch API 文档和定价：
  + <https://platform.openai.com/docs/api-reference/batch>
  + <https://platform.openai.com/pricing>

配置示例：

json5

```
agents: {
  defaults: {
    memorySearch: {
      provider: "openai",
      model: "text-embedding-3-small",
      fallback: "openai",
      remote: {
        batch: { enabled: true, concurrency: 2 }
      },
      sync: { watch: true }
    }
  }
}
```

工具：

* `memory_search` — 返回带有文件 + 行范围的片段。
* `memory_get` — 按路径读取记忆文件内容。

本地模式：

* 设置 `agents.defaults.memorySearch.provider = "local"`。
* 提供 `agents.defaults.memorySearch.local.modelPath` (GGUF 或 `hf:` URI)。
* 可选：设置 `agents.defaults.memorySearch.fallback = "none"` 以避免远程回退。

### 记忆工具如何工作

* `memory_search` 从 `MEMORY.md` + `memory/**/*.md` 中语义搜索 Markdown 块（~400 令牌目标，80 令牌重叠）。它返回片段文本（上限 ~700 字符）、文件路径、行范围、分数、提供商/模型，以及我们是否从本地 → 远程嵌入回退。不返回完整的文件有效负载。
* `memory_get` 读取特定的记忆 Markdown 文件（相对于工作区），可选地从起始行开始读取 N 行。`MEMORY.md` / `memory/` 之外的路径会被拒绝。
* 这两个工具仅当 `memorySearch.enabled` 对智能体解析为 true 时启用。

### 索引什么 (以及何时)

* 文件类型：仅 Markdown (`MEMORY.md`, `memory/**/*.md`)。
* 索引存储：每个智能体的 SQLite 位于 `~/.openclaw/memory/<agentId>.sqlite`（可通过 `agents.defaults.memorySearch.store.path` 配置，支持 `{agentId}` 令牌）。
* 新鲜度：`MEMORY.md` + `memory/` 上的监视器将索引标记为脏（防抖 1.5s）。同步安排在会话开始、搜索或间隔时运行，并异步运行。会话记录使用增量阈值触发后台同步。
* 重建索引触发器：索引存储嵌入**提供商/模型 + 端点指纹 + 分块参数**。如果其中任何一个发生变化，Clawdbot 会自动重置并重建整个存储的索引。

### 混合搜索 (Hybrid search) (BM25 + 向量)
