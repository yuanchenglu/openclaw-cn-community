# OpenRouter

来源: https://clawd.org.cn/providers/openrouter.html

# OpenRouter

OpenRouter 提供一个**统一 API**，通过单个端点和 API 密钥将请求路由到许多模型。它是 OpenAI 兼容的，因此大多数 OpenAI SDK 通过切换基础 URL 即可工作。

## CLI 设置

bash

```
openclaw-cn onboard --auth-choice apiKey --token-provider openrouter --token "$OPENROUTER_API_KEY"
```

## 配置片段

json5

```
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/anthropic/claude-sonnet-4-5" }
    }
  }
}
```

## 注意事项

* 模型引用为 `openrouter/<provider>/<model>`。
* 有关更多模型/提供者选项，请参阅 [/concepts/model-providers](/concepts/model-providers.html)。
* OpenRouter 在底层使用带有您的 API 密钥的 Bearer 令牌。
