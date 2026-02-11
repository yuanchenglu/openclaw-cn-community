# Webhook

Source: https://clawd.org.cn/automation/webhook.html

# Webhooks

Gateway 可以暴露一个小型 HTTP webhook 端点用于外部触发。

## 启用 (Enable)

json5

```
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks"
  }
}
```

注意：

* 当 `hooks.enabled=true` 时，`hooks.token` 是必需的。
* `hooks.path` 默认为 `/hooks`。

## 认证 (Auth)

每个请求都必须包含 hook token。推荐使用 headers：

* `Authorization: Bearer <token>` (推荐)
* `x-clawdbot-token: <token>`
* `?token=<token>` (已弃用；会记录警告并在未来的主要版本中移除)

## 端点 (Endpoints)

### `POST /hooks/wake`

Payload:

json

```
{ "text": "System line", "mode": "now" }
```

* `text` **必需** (string): 事件的描述 (例如, "New email received")。
* `mode` 可选 (`now` | `next-heartbeat`): 是否触发立即心跳 (默认 `now`) 还是等待下一次定期检查。

效果:

* 为 **main** (主) 会话将系统事件加入队列
* 如果 `mode=now`, 触发立即心跳

### `POST /hooks/agent`

Payload:

json

```
{
  "message": "Run this",
  "name": "Email",
  "sessionKey": "hook:email:msg-123",
  "wakeMode": "now",
  "deliver": true,
  "channel": "last",
  "to": "+15551234567",
  "model": "openai/gpt-5.2-mini",
  "thinking": "low",
  "timeoutSeconds": 120
}
```

* `message` **必需** (string): 供 Agent 处理的提示或消息。
* `name` 可选 (string): Hook 的可读名称 (例如, "GitHub")，用作会话摘要的前缀。
* `sessionKey` 可选 (string): 用于标识 Agent 会话的键。默认为随机的 `hook:<uuid>`。使用一致的键允许在 Hook 上下文中进行多轮对话。
* `wakeMode` 可选 (`now` | `next-heartbeat`): 是否触发立即心跳 (默认 `now`) 还是等待下一次定期检查。
* `deliver` 可选 (boolean): 如果为 `true`，Agent 的响应将被发送到消息通道。默认为 `true`。仅作为心跳确认的响应会自动跳过。
* `channel` 可选 (string): 用于传递消息的通道。可选值: `last`, `whatsapp`, `telegram`, `discord`, `slack`, `mattermost` (插件), `signal`, `imessage`, `msteams`。默认为 `last`。
* `to` 可选 (string): 通道的接收者标识符 (例如 WhatsApp/Signal 的电话号码, Telegram 的 chat ID, Discord/Slack/Mattermost (插件) 的 channel ID, MS Teams 的 conversation ID)。默认为主会话中的最后一个接收者。
* `model` 可选 (string): 模型覆盖 (例如 `anthropic/claude-3-5-sonnet` 或别名)。如果受到限制，必须在允许的模型列表中。
* `thinking` 可选 (string): 思考级别覆盖 (例如 `low`, `medium`, `high`)。
* `timeoutSeconds` 可选 (number): Agent 运行的最大持续时间（秒）。

效果:

* 运行一个 **隔离的** Agent 轮次 (拥有自己的 session key)
* 总是将摘要发布到 **main** (主) 会话
* 如果 `wakeMode=now`, 触发立即心跳

### `POST /hooks/<name>` (映射)

自定义 hook 名称通过 `hooks.mappings` 解析 (见配置)。映射可以将任意 payload 转换为 `wake` 或 `agent` 动作，并支持可选的模板或代码转换。

映射选项 (摘要):

* `hooks.presets: ["gmail"]` 启用内置的 Gmail 映射。
* `hooks.mappings` 允许你在配置中定义 `match`, `action` 和模板。
* `hooks.transformsDir` + `transform.module` 加载 JS/TS 模块以实现自定义逻辑。
* 使用 `match.source` 保持通用的摄取端点 (基于 payload 的路由)。
* TS 转换需要运行时有 TS 加载器 (例如 `bun` 或 `tsx`) 或预编译的 `.js`。
* 在映射上设置 `deliver: true` + `channel`/`to` 以将回复路由到聊天界面 (`channel` 默认为 `last` 并回退到 WhatsApp)。
* `allowUnsafeExternalContent: true` 禁用该 hook 的外部内容安全包装器 (危险; 仅用于受信任的内部来源)。
* `clawdbot webhooks gmail setup` 写入 `hooks.gmail` 配置以供 `clawdbot webhooks gmail run` 使用。参见 [Gmail Pub/Sub](/automation/gmail-pubsub.html) 了解完整的 Gmail 监听流程。

## 响应 (Responses)

* `200` 对应 `/hooks/wake`
* `202` 对应 `/hooks/agent` (异步运行已开始)
* `401` 对应认证失败
* `400` 对应无效 payload
* `413` 对应 payload 过大

## 示例 (Examples)

bash

```
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

bash

```
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-clawdbot-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","wakeMode":"next-heartbeat"}'
```

### 使用不同的模型

将 `model` 添加到 agent payload (或映射) 中以覆盖该次运行的模型：

bash

```
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'x-clawdbot-token: SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.2-mini"}'
```

如果你强制执行 `agents.defaults.models`，请确保覆盖模型包含在其中。

bash

```
curl -X POST http://127.0.0.1:18789/hooks/gmail \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"source":"gmail","messages":[{"from":"Ada","subject":"Hello","snippet":"Hi"}]}'
```

## 安全性 (Security)

* 将 hook 端点保持在环回接口 (loopback)、tailnet 或受信任的反向代理后面。
* 使用专用的 hook token；不要重用 gateway auth token。
* 避免在 webhook 日志中包含敏感的原始 payload。
* Hook payload 默认被视为不受信任的，并被安全边界包裹。如果你必须为特定 hook 禁用此功能，请在该 hook 的映射中设置 `allowUnsafeExternalContent: true` (危险)。
