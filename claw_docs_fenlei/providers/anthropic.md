# Anthropic

来源: https://clawd.org.cn/providers/anthropic.html

# Anthropic (Claude)

Anthropic 构建了 **Claude** 模型系列，并提供 API 访问。在 Clawdbot 中，您可以使用 API 密钥进行身份验证，或重复使用 **Claude Code CLI** 凭据（setup-token 或 OAuth）。

## 选项 A: Anthropic API 密钥

**最适合：** 标准 API 访问和基于使用量的计费。在 Anthropic 控制台中创建您的 API 密钥。

### CLI 设置

bash

```
openclaw-cn onboard
# 选择: Anthropic API key

# 或非交互式
openclaw-cn onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### 配置片段

json5

```
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } }
}
```

## Prompt 缓存 (Anthropic API)

Clawdbot **不会** 覆盖 Anthropic 的默认缓存 TTL，除非您设置它。这**仅限 API**；Claude Code CLI OAuth 忽略 TTL 设置。

要为每个模型设置 TTL，请使用模型 `params` 中的 `cacheControlTtl`：

json5

```
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-5": {
          params: { cacheControlTtl: "5m" } // 或 "1h"
        }
      }
    }
  }
}
```

Clawdbot 包含用于 Anthropic API 请求的 `extended-cache-ttl-2025-04-11` beta 标志；如果您覆盖提供者标头，请保留它（参见 [/gateway/configuration](/gateway/configuration.html)）。

## 选项 B: Claude Code CLI (setup-token 或 OAuth)

**最适合：** 使用您的 Claude 订阅或现有的 Claude Code CLI 登录。

### 获取 setup-token 的位置

Setup-token 由 **Claude Code CLI** 创建，而不是 Anthropic 控制台。您可以在**任何机器**上运行此命令：

bash

```
claude setup-token
```

将令牌粘贴到 Clawdbot（向导：**Anthropic token (paste setup-token)**），或在 gateway 主机上运行：

bash

```
openclaw-cn models auth setup-token --provider anthropic
```

如果您在另一台机器上生成了令牌，请粘贴它：

bash

```
openclaw-cn models auth paste-token --provider anthropic
```

### CLI 设置

bash

```
# 如果已登录，重用 Claude Code CLI OAuth 凭据
openclaw-cn onboard --auth-choice claude-cli
```

### 配置片段

json5

```
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-5" } } }
}
```

## 注意事项

* 使用 `claude setup-token` 生成 setup-token 并粘贴，或在 gateway 主机上运行 `openclaw-cn models auth setup-token`。
* 如果您在 Claude 订阅上看到“OAuth token refresh failed ...”，请使用 setup-token 重新验证或在 gateway 主机上重新同步 Claude Code CLI OAuth。参见 [/gateway/troubleshooting#oauth-token-refresh-failed-anthropic-claude-subscription](/gateway/troubleshooting.html#oauth-token-refresh-failed-anthropic-claude-subscription)。
* Clawdbot 将 `auth.profiles["anthropic:claude-cli"].mode` 写入为 `"oauth"`，以便配置文件同时接受 OAuth 和 setup-token 凭据。使用 `"token"` 的旧配置在加载时会自动迁移。
* 认证详情 + 重用规则在 [/concepts/oauth](/concepts/oauth.html) 中。

## 故障排除

**401 错误 / 令牌突然失效**

* Claude 订阅认证可能会过期或被吊销。重新运行 `claude setup-token` 并将其粘贴到 **gateway 主机** 中。
* 如果 Claude CLI 登录位于另一台机器上，请在 gateway 主机上使用 `openclaw-cn models auth paste-token --provider anthropic`。

**未找到提供者 "anthropic" 的 API 密钥**

* 认证是**按智能体**进行的。新智能体不会继承主智能体的密钥。
* 为该智能体重新运行入门向导，或在 gateway 主机上粘贴 setup-token / API 密钥，然后使用 `openclaw-cn models status` 进行验证。

**未找到配置文件 `anthropic:default` 或 `anthropic:claude-cli` 的凭据**

* 运行 `openclaw-cn models status` 查看哪个认证配置文件处于活动状态。
* 重新运行入门向导，或为该配置文件粘贴 setup-token / API 密钥。

**没有可用的认证配置文件 (全部处于冷却/不可用状态)**

* 检查 `openclaw-cn models status --json` 中的 `auth.unusableProfiles`。
* 添加另一个 Anthropic 配置文件或等待冷却。

更多信息：[/gateway/troubleshooting](/gateway/troubleshooting.html) 和 [/help/faq](/help/faq.html)。
