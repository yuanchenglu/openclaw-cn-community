# OpenAI

来源: https://clawd.org.cn/providers/openai.html

# OpenAI

OpenAI 提供用于 GPT 模型的开发者 API。Codex 支持用于订阅访问的 **ChatGPT 登录** 或用于基于使用量访问的 **API 密钥** 登录。Codex 云需要 ChatGPT 登录，而 Codex CLI 支持任一登录方法。Codex CLI 将登录详细信息缓存在 `~/.codex/auth.json`（或您的操作系统凭据存储）中，Clawdbot 可以重用这些信息。

## 选项 A: OpenAI API 密钥 (OpenAI 平台)

**最适合：** 直接 API 访问和基于使用量的计费。从 OpenAI 仪表板获取您的 API 密钥。

### CLI 设置

bash

```
openclaw-cn onboard --auth-choice openai-api-key
# 或非交互式
openclaw-cn onboard --openai-api-key "$OPENAI_API_KEY"
```

### 配置片段

json5

```
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.2" } } }
}
```

## 选项 B: OpenAI Code (Codex) 订阅

**最适合：** 使用 ChatGPT/Codex 订阅访问而不是 API 密钥。Codex 云需要 ChatGPT 登录，而 Codex CLI 支持 ChatGPT 或 API 密钥登录。

Clawdbot 可以重用您的 **Codex CLI** 登录 (`~/.codex/auth.json`) 或运行 OAuth 流程。

### CLI 设置

bash

```
# 重用现有的 Codex CLI 登录
openclaw-cn onboard --auth-choice codex-cli

# 或在向导中运行 Codex OAuth
openclaw-cn onboard --auth-choice openai-codex
```

### 配置片段

json5

```
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.2" } } }
}
```

## 注意事项

* 模型引用始终使用 `provider/model`（参见 [/concepts/models](/concepts/models.html)）。
* 认证详情 + 重用规则在 [/concepts/oauth](/concepts/oauth.html) 中。
