# 测试

Source: https://clawd.org.cn/testing.html

# 测试

Clawdbot 有三个 Vitest 套件（单元/集成、e2e、live）和一小组 Docker 运行器。

这份文档是一份“我们如何测试”的指南：

* 每个套件涵盖的内容（以及它故意*不*涵盖的内容）
* 常见工作流（本地、推送前、调试）运行哪些命令
* 实时测试如何发现凭据并选择模型/提供商
* 如何为现实世界的模型/提供商问题添加回归测试

## 快速开始

大多数时候：

* 完整门控（推送前预期）：`pnpm lint && pnpm build && pnpm test`

当你修改测试或想要额外的信心时：

* 覆盖率门控：`pnpm test:coverage`
* E2E 套件：`pnpm test:e2e`

当调试真实的提供商/模型（需要真实凭据）时：

* 实时套件（模型 + 网关工具/图像探测）：`pnpm test:live`

提示：当你只需要一个失败的案例时，最好使用下面描述的允许列表环境变量来缩小实时测试范围。

## 测试套件（在何处运行什么）

将套件视为“增加现实感”（以及增加不稳定性/成本）：

### 单元 / 集成 (默认)

* 命令：`pnpm test`
* 配置：`vitest.config.ts`
* 文件：`src/**/*.test.ts`
* 范围：
  + 纯单元测试
  + 进程内集成测试（网关认证、路由、工具、解析、配置）
  + 已知错误的确定性回归
* 预期：
  + 在 CI 中运行
  + 不需要真实密钥
  + 应该快速且稳定

### E2E (网关冒烟)

* 命令：`pnpm test:e2e`
* 配置：`vitest.e2e.config.ts`
* 文件：`src/**/*.e2e.test.ts`
* 范围：
  + 多实例网关端到端行为
  + WebSocket/HTTP 表面、节点配对和更重的网络
* 预期：
  + 在 CI 中运行（当在管道中启用时）
  + 不需要真实密钥
  + 比单元测试有更多的移动部件（可能更慢）

### 实时 (真实提供商 + 真实模型)

* 命令：`pnpm test:live`
* 配置：`vitest.live.config.ts`
* 文件：`src/**/*.live.test.ts`
* 默认：通过 `pnpm test:live` **启用**（设置 `OPENCLAW_LIVE_TEST=1`）
* 范围：
  + “这个提供商/模型*今天*使用真实凭据是否真的有效？”
  + 捕获提供商格式更改、工具调用怪癖、认证问题和速率限制行为
* 预期：
  + 设计上非 CI 稳定（真实网络、真实提供商策略、配额、中断）
  + 花费金钱 / 使用速率限制
  + 最好运行缩小的子集而不是“所有内容”
  + 实时运行将通过 source `~/.profile` 来获取丢失的 API 密钥
  + Anthropic 密钥轮换：设置 `OPENCLAW_LIVE_ANTHROPIC_KEYS="sk-...,sk-..."`（或 `OPENCLAW_LIVE_ANTHROPIC_KEY=sk-...`）或多个 `ANTHROPIC_API_KEY*` 变量；测试将在速率限制时重试

## 我应该运行哪个套件？

使用此决策表：

* 编辑逻辑/测试：运行 `pnpm test`（如果你更改了很多，运行 `pnpm test:coverage`）
* 触及网关网络 / WS 协议 / 配对：添加 `pnpm test:e2e`
* 调试“我的机器人挂了” / 提供商特定的失败 / 工具调用：运行缩小的 `pnpm test:live`

## 实时：模型冒烟 (配置文件密钥)

实时测试分为两层，以便我们可以隔离失败：

* “直接模型”告诉我们提供商/模型是否可以使用给定的密钥回答。
* “网关冒烟”告诉我们完整的网关+智能体管道对于该模型是否工作（会话、历史记录、工具、沙箱策略等）。

### 第 1 层：直接模型完成 (无网关)

* 测试：`src/agents/models.profiles.live.test.ts`
* 目标：
  + 枚举发现的模型
  + 使用 `getApiKeyForModel` 选择你有凭据的模型
  + 每个模型运行一个小型的完成（以及在需要时针对性的回归）
* 如何启用：
  + `pnpm test:live`（或者如果直接调用 Vitest，设置 `OPENCLAW_LIVE_TEST=1`）
* 设置 `OPENCLAW_LIVE_MODELS=modern`（或 `all`，modern 的别名）以实际运行此套件；否则它会跳过，以使 `pnpm test:live` 专注于网关冒烟
* 如何选择模型：
  + `OPENCLAW_LIVE_MODELS=modern` 运行现代允许列表（Opus/Sonnet/Haiku 4.5, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.1, Grok 4）
  + `OPENCLAW_LIVE_MODELS=all` 是现代允许列表的别名
  + 或 `OPENCLAW_LIVE_MODELS="openai/gpt-5.2,anthropic/claude-opus-4-5,..."`（逗号允许列表）
* 如何选择提供商：
  + `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（逗号允许列表）
* 密钥来自哪里：
  + 默认：配置文件存储和环境回退
  + 设置 `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 以强制仅使用**配置文件存储**
* 为什么存在：
  + 将“提供商 API 损坏 / 密钥无效”与“网关智能体管道损坏”分开
  + 包含小的、隔离的回归（示例：OpenAI Responses/Codex Responses 推理重放 + 工具调用流）

### 第 2 层：网关 + 开发智能体冒烟 (“@clawdbot” 实际做什么)

* 测试：`src/gateway/gateway-models.profiles.live.test.ts`
* 目标：
  + 启动进程内网关
  + 创建/修补 `agent:dev:*` 会话（每次运行覆盖模型）
  + 迭代带有密钥的模型并断言：
    - “有意义”的回复（无工具）
    - 真实的工具调用工作（读取探测）
    - 可选的额外工具探测（执行+读取探测）
    - OpenAI 回归路径（仅工具调用 → 后续）保持工作
* 探测详情（以便你可以快速解释失败）：
  + `read` 探测：测试在工作区中写入一个随机数文件，并要求智能体 `read` 它并回显随机数。
  + `exec+read` 探测：测试要求智能体 `exec`-将随机数写入临时文件，然后 `read` 它回来。
  + 图像探测：测试附加一个生成的 PNG（猫 + 随机代码）并期望模型返回 `cat <CODE>`。
  + 实现参考：`src/gateway/gateway-models.profiles.live.test.ts` 和 `src/gateway/live-image-probe.ts`。
* 如何启用：
  + `pnpm test:live`（或者如果直接调用 Vitest，设置 `OPENCLAW_LIVE_TEST=1`）
* 如何选择模型：
  + 默认：现代允许列表（Opus/Sonnet/Haiku 4.5, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.1, Grok 4）
  + `OPENCLAW_LIVE_GATEWAY_MODELS=all` 是现代允许列表的别名
  + 或设置 `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（或逗号列表）以缩小范围
* 如何选择提供商（避免“OpenRouter 一切”）：
  + `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（逗号允许列表）
* 工具 + 图像探测在此实时测试中始终开启：
  + `read` 探测 + `exec+read` 探测（工具压力）
  + 当模型通告图像输入支持时，图像探测运行
  + 流程（高层）：
    - 测试生成一个带有“CAT” + 随机代码的小 PNG (`src/gateway/live-image-probe.ts`)
    - 通过 `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 发送
    - 网关将附件解析为 `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - 嵌入式智能体将多模态用户消息转发给模型
    - 断言：回复包含 `cat` + 代码（OCR 容差：允许轻微错误）

提示：要查看你可以在机器上测试什么（以及确切的 `provider/model` id），运行：

bash

```
openclaw-cn models list
openclaw-cn models list --json
```

## 实时：Anthropic setup-token 冒烟

* 测试：`src/agents/anthropic.setup-token.live.test.ts`
* 目标：验证 Claude Code CLI setup-token（或粘贴的 setup-token 配置文件）是否可以完成 Anthropic 提示。
* 启用：
  + `pnpm test:live`（或者如果直接调用 Vitest，设置 `OPENCLAW_LIVE_TEST=1`）
  + `OPENCLAW_LIVE_SETUP_TOKEN=1`
* 令牌来源（选一个）：
  + 配置文件：`OPENCLAW_LIVE_SETUP_TOKEN_PROFILE=anthropic:setup-token-test`
  + 原始令牌：`OPENCLAW_LIVE_SETUP_TOKEN_VALUE=sk-ant-oat01-...`
* 模型覆盖（可选）：
  + `OPENCLAW_LIVE_SETUP_TOKEN_MODEL=anthropic/claude-opus-4-5`

设置示例：

bash

```
openclaw-cn models auth paste-token --provider anthropic --profile-id anthropic:setup-token-test
OPENCLAW_LIVE_SETUP_TOKEN=1 OPENCLAW_LIVE_SETUP_TOKEN_PROFILE=anthropic:setup-token-test pnpm test:live src/agents/anthropic.setup-token.live.test.ts
```

## 实时：CLI 后端冒烟 (Claude Code CLI 或其他本地 CLI)

* 测试：`src/gateway/gateway-cli-backend.live.test.ts`
* 目标：验证使用本地 CLI 后端的网关 + 智能体管道，而不触及你的默认配置。
* 启用：
  + `pnpm test:live`（或者如果直接调用 Vitest，设置 `OPENCLAW_LIVE_TEST=1`）
  + `OPENCLAW_LIVE_CLI_BACKEND=1`
* 默认：
  + 模型：`claude-cli/claude-sonnet-4-5`
  + 命令：`claude`
  + 参数：`["-p","--output-format","json","--dangerously-skip-permissions"]`
* 覆盖（可选）：
  + `OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-opus-4-5"`
  + `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.2-codex"`
  + `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/claude"`
  + `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["-p","--output-format","json","--permission-mode","bypassPermissions"]'`
  + `OPENCLAW_LIVE_CLI_BACKEND_CLEAR_ENV='["ANTHROPIC_API_KEY","ANTHROPIC_API_KEY_OLD"]'`
  + `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` 发送真实图像附件（路径注入提示中）。
  + `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` 将图像文件路径作为 CLI 参数传递，而不是提示注入。
  + `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（或 `"list"`）控制当设置 `IMAGE_ARG` 时如何传递图像参数。
  + `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` 发送第二回合验证恢复流。
* `OPENCLAW_LIVE_CLI_BACKEND_DISABLE_MCP_CONFIG=0` 保持 Claude Code CLI MCP 配置启用（默认使用临时空文件禁用 MCP 配置）。

示例：

bash

```
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="claude-cli/claude-sonnet-4-5" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

### 推荐的实时配方

狭窄、明确的允许列表最快且最不容易出错：

* 单个模型，直接（无网关）：

  + `OPENCLAW_LIVE_MODELS="openai/gpt-5.2" pnpm test:live src/agents/models.profiles.live.test.ts`
* 单个模型，网关冒烟：

  + `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
* 跨多个提供商的工具调用：

  + `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2,anthropic/claude-opus-4-5,google/gemini-3-flash-preview,zai/glm-4.7,minimax/minimax-m2.1" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
* Google 重点（Gemini API 密钥 + Antigravity）：

  + Gemini (API 密钥)：`OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  + Antigravity (OAuth)：`OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-5-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

注意：

* `google/...` 使用 Gemini API（API 密钥）。
* `google-antigravity/...` 使用 Antigravity OAuth 桥接（Cloud Code Assist 风格的智能体端点）。
* `google-gemini-cli/...` 使用你机器上的本地 `gemini` CLI（单独的认证 + 工具怪癖）。
* Gemini API vs Gemini CLI：
  + API：Clawdbot 通过 HTTP 调用 Google 托管的 Gemini API（API 密钥 / 配置文件认证）；这大多数用户所说的“Gemini”。
  + CLI：Clawdbot 在外部调用本地 `gemini` 二进制文件；它有自己的认证，行为可能不同（流式传输/工具支持/版本偏差）。

## 实时：模型矩阵 (我们覆盖的内容)

没有固定的“CI 模型列表”（实时是选择加入的），但这些是在带有密钥的开发机器上**推荐**定期覆盖的模型。

### 现代冒烟集 (工具调用 + 图像)

这是我们期望保持工作的“常见模型”运行：

* OpenAI (非 Codex)：`openai/gpt-5.2`（可选：`openai/gpt-5.1`）
* OpenAI Codex：`openai-codex/gpt-5.2`（可选：`openai-codex/gpt-5.2-codex`）
* Anthropic：`anthropic/claude-opus-4-5`（或 `anthropic/claude-sonnet-4-5`）
* Google (Gemini API)：`google/gemini-3-pro-preview` 和 `google/gemini-3-flash-preview`（避免旧的 Gemini 2.x 模型）
* Google (Antigravity)：`google-antigravity/claude-opus-4-5-thinking` 和 `google-antigravity/gemini-3-flash`
* Z.AI (GLM)：`zai/glm-4.7`
* MiniMax：`minimax/minimax-m2.1`

运行带有工具 + 图像的网关冒烟：`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.2,openai-codex/gpt-5.2,anthropic/claude-opus-4-5,google/gemini-3-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-5-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/minimax-m2.1" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### 基线：工具调用 (Read + 可选 Exec)

每个提供商家族至少选择一个：

* OpenAI：`openai/gpt-5.2`（或 `openai/gpt-5-mini`）
* Anthropic：`anthropic/claude-opus-4-5`（或 `anthropic/claude-sonnet-4-5`）
* Google：`google/gemini-3-flash-preview`（或 `google/gemini-3-pro-preview`）
* Z.AI (GLM)：`zai/glm-4.7`
* MiniMax：`minimax/minimax-m2.1`

可选的额外覆盖（最好有）：

* xAI：`xai/grok-4`（或最新可用）
* Mistral：`mistral/`…（选择一个你启用的具有“工具”能力的模型）
* Cerebras：`cerebras/`…（如果你有访问权限）
* LM Studio：`lmstudio/`…（本地；工具调用取决于 API 模式）

### 视觉：图像发送 (附件 → 多模态消息)

在 `OPENCLAW_LIVE_GATEWAY_MODELS` 中至少包含一个具有图像能力的模型（Claude/Gemini/OpenAI 视觉能力变体等）以行使图像探测。

### 聚合器 / 替代网关

如果你启用了密钥，我们也支持通过以下方式测试：

* OpenRouter：`openrouter/...`（数百个模型；使用 `openclaw-cn models scan` 查找工具+图像能力候选者）
* OpenCode Zen：`opencode/...`（通过 `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY` 认证）

你可以包含在实时矩阵中的更多提供商（如果你有凭据/配置）：

* 内置：`openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
* 通过 `models.providers`（自定义端点）：`minimax`（云/API），加上任何 OpenAI/Anthropic 兼容代理（LM Studio, vLLM, LiteLLM 等）

提示：不要试图在文档中硬编码“所有模型”。权威列表是你机器上 `discoverModels(...)` 返回的内容 + 任何可用的密钥。

## 凭据 (永不提交)

实时测试以与 CLI 相同的方式发现凭据。实际含义：

* 如果 CLI 工作，实时测试应该找到相同的密钥。
* 如果实时测试说“无凭据”，请以与调试 `openclaw-cn models list` / 模型选择相同的方式调试。
* 配置文件存储：`~/.openclaw/credentials/`（首选；测试中“配置文件密钥”的含义）
* 配置：`~/.openclaw/openclaw.json`（或 `OPENCLAW_CONFIG_PATH`）

如果你想依赖环境密钥（例如在你的 `~/.profile` 中导出），请在 `source ~/.profile` 后运行本地测试，或使用下面的 Docker 运行器（它们可以将 `~/.profile` 挂载到容器中）。

## Deepgram 实时 (音频转录)

* 测试：`src/media-understanding/providers/deepgram/audio.live.test.ts`
* 启用：`DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Docker 运行器 (可选 “在 Linux 中工作” 检查)

这些在 repo Docker 镜像内运行 `pnpm test:live`，挂载你的本地配置目录和工作区（如果挂载，也会 source `~/.profile`）：

* 直接模型：`pnpm test:docker:live-models`（脚本：`scripts/test-live-models-docker.sh`）
* 网关 + 开发智能体：`pnpm test:docker:live-gateway`（脚本：`scripts/test-live-gateway-models-docker.sh`）
* 入职向导（TTY，完整脚手架）：`pnpm test:docker:onboard`（脚本：`scripts/e2e/onboard-docker.sh`）
* 网关网络（两个容器，WS 认证 + 健康）：`pnpm test:docker:gateway-network`（脚本：`scripts/e2e/gateway-network-docker.sh`）
* 插件（自定义扩展加载 + 注册表冒烟）：`pnpm test:docker:plugins`（脚本：`scripts/e2e/plugins-docker.sh`）

有用的环境变量：

* `OPENCLAW_CONFIG_DIR=...`（默认：`~/.openclaw`）挂载到 `/home/node/.openclaw`
* `OPENCLAW_WORKSPACE_DIR=...`（默认：`~/clawd`）挂载到 `/home/node/clawd`
* `OPENCLAW_PROFILE_FILE=...`（默认：`~/.profile`）挂载到 `/home/node/.profile` 并在运行测试前 source
* `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` 以缩小运行范围
* `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` 以确保凭据来自配置文件存储（而非环境）

## 文档健全性

在文档编辑后运行文档检查：`pnpm docs:list`。

## 离线回归 (CI 安全)

这些是没有真实提供商的“真实管道”回归：

* 网关工具调用（模拟 OpenAI，真实网关 + 智能体循环）：`src/gateway/gateway.tool-calling.mock-openai.test.ts`
* 网关向导（WS `wizard.start`/`wizard.next`，写入配置 + 强制认证）：`src/gateway/gateway.wizard.e2e.test.ts`

## 智能体可靠性评估 (技能)

我们已经有一些行为像“智能体可靠性评估”的 CI 安全测试：

* 通过真实网关 + 智能体循环的模拟工具调用 (`src/gateway/gateway.tool-calling.mock-openai.test.ts`)。
* 验证会话连线和配置效果的端到端向导流 (`src/gateway/gateway.wizard.e2e.test.ts`)。

技能方面仍然缺少什么（参见 [技能](/tools/skills.html)）：

* **决策：** 当技能列在提示中时，智能体是否选择了正确的技能（或避免不相关的技能）？
* **合规性：** 智能体在使用前是否阅读了 `SKILL.md` 并遵循所需的步骤/参数？
* **工作流契约：** 多回合场景，断言工具顺序、会话历史记录结转和沙箱边界。

未来的评估应首先保持确定性：

* 使用模拟提供商的场景运行器，断言工具调用 + 顺序、技能文件读取和会话连线。
* 一小组专注于技能的场景（使用 vs 避免、门控、提示注入）。
* 仅在 CI 安全套件就位后，才进行可选的实时评估（选择加入，环境门控）。

## 添加回归 (指导)

当你修复在实时中发现的提供商/模型问题时：

* 如果可能，添加一个 CI 安全的回归（模拟/存根提供商，或捕获确切的请求形状转换）
* 如果它本质上是仅实时的（速率限制、认证策略），请保持实时测试狭窄并通过环境变量选择加入
* 最好针对捕获错误的最小层：
  + 提供商请求转换/重放错误 → 直接模型测试
  + 网关会话/历史记录/工具管道错误 → 网关实时冒烟或 CI 安全网关模拟测试
