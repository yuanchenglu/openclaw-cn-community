# Gmail 集成

Source: https://clawd.org.cn/automation/gmail-pubsub.html

# Gmail Pub/Sub -> Clawdbot

目标：Gmail 监视 -> Pub/Sub 推送 -> `gog gmail watch serve` -> Clawdbot Webhook。

## 先决条件

* 已安装 `gcloud` 并登录 ([安装指南](https://docs.cloud.google.com/sdk/docs/install-sdk))。
* 已安装 `gog` (gogcli) 并为 Gmail 帐户授权 ([gogcli.sh](https://gogcli.sh/))。
* 已启用 Clawdbot hooks（参见 [Webhooks](/automation/webhook.html)）。
* `tailscale` 已登录 ([tailscale.com](https://tailscale.com/))。支持的设置使用 Tailscale Funnel 作为公共 HTTPS 端点。其他隧道服务也可以工作，但是 DIY/不受支持并且需要手动连线。目前，Tailscale 是我们支持的。

示例 hook 配置（启用 Gmail 预设映射）：

json5

```
{
  hooks: {
    enabled: true,
    token: "OPENCLAW_HOOK_TOKEN",
    path: "/hooks",
    presets: ["gmail"]
  }
}
```

要将 Gmail 摘要投递到聊天界面，请使用设置 `deliver` + 可选 `channel`/`to` 的映射覆盖预设：

json5

```
{
  hooks: {
    enabled: true,
    token: "OPENCLAW_HOOK_TOKEN",
    presets: ["gmail"],
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        wakeMode: "now",
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate:
          "New email from {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].snippet}}\n{{messages[0].body}}",
        model: "openai/gpt-5.2-mini",
        deliver: true,
        channel: "last"
        // to: "+15551234567"
      }
    ]
  }
}
```

如果你想要一个固定的频道，设置 `channel` + `to`。否则 `channel: "last"` 使用最后的投递路由（回退到 WhatsApp）。

要强制为 Gmail 运行使用更便宜的模型，请在映射中设置 `model`（`provider/model` 或别名）。如果你强制执行 `agents.defaults.models`，请将其包含在内。

要专门为 Gmail hooks 设置默认模型和思考级别，请在配置中添加 `hooks.gmail.model` / `hooks.gmail.thinking`：

json5

```
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off"
    }
  }
}
```

注意：

* 映射中的每个 hook `model`/`thinking` 仍然覆盖这些默认值。
* 回退顺序：`hooks.gmail.model` → `agents.defaults.model.fallbacks` → 主模型 (auth/rate-limit/timeouts)。
* 如果设置了 `agents.defaults.models`，Gmail 模型必须在允许列表中。
* 默认情况下，Gmail hook 内容包含在外部内容安全边界中。要禁用（危险），设置 `hooks.gmail.allowUnsafeExternalContent: true`。

要进一步自定义有效负载处理，请添加 `hooks.mappings` 或 `hooks.transformsDir` 下的 JS/TS 转换模块（参见 [Webhooks](/automation/webhook.html)）。

## 向导 (推荐)

使用 Clawdbot 助手将所有内容连接起来（在 macOS 上通过 brew 安装依赖项）：

bash

```
clawdbot webhooks gmail setup \
  --account clawdbot@gmail.com
```

默认值：

* 使用 Tailscale Funnel 作为公共推送端点。
* 为 `clawdbot webhooks gmail run` 写入 `hooks.gmail` 配置。
* 启用 Gmail hook 预设 (`hooks.presets: ["gmail"]`)。

路径说明：当启用 `tailscale.mode` 时，Clawdbot 自动将 `hooks.gmail.serve.path` 设置为 `/` 并将公共路径保持在 `hooks.gmail.tailscale.path`（默认 `/gmail-pubsub`），因为 Tailscale 在代理之前会去除设置的路径前缀。如果你需要后端接收带前缀的路径，请将 `hooks.gmail.tailscale.target`（或 `--tailscale-target`）设置为完整的 URL，如 `http://127.0.0.1:8788/gmail-pubsub` 并匹配 `hooks.gmail.serve.path`。

想要自定义端点？使用 `--push-endpoint <url>` 或 `--tailscale off`。

平台说明：在 macOS 上，向导通过 Homebrew 安装 `gcloud`, `gogcli`, 和 `tailscale`；在 Linux 上请先手动安装它们。

网关自动启动 (推荐)：

* 当 `hooks.enabled=true` 且 `hooks.gmail.account` 已设置时，网关在启动时启动 `gog gmail watch serve` 并自动续订监视。
* 设置 `OPENCLAW_SKIP_GMAIL_WATCHER=1` 以选择退出（如果你自己运行守护进程）。
* 不要同时运行手动守护进程，否则你会遇到 `listen tcp 127.0.0.1:8788: bind: address already in use`。

手动守护进程（启动 `gog gmail watch serve` + 自动续订）：

bash

```
clawdbot webhooks gmail run
```

## 一次性设置

1. 选择**拥有 `gog` 使用的 OAuth 客户端**的 GCP 项目。

bash

```
gcloud auth login
gcloud config set project <project-id>
```

注意：Gmail 监视要求 Pub/Sub 主题与 OAuth 客户端位于同一项目中。

2. 启用 API：

bash

```
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

3. 创建主题：

bash

```
gcloud pubsub topics create gog-gmail-watch
```

4. 允许 Gmail 推送发布：

bash

```
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

## 开始监视

bash

```
gog gmail watch start \
  --account clawdbot@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

保存输出中的 `history_id`（用于调试）。

## 运行推送处理程序

本地示例（共享令牌认证）：

bash

```
gog gmail watch serve \
  --account clawdbot@gmail.com \
  --bind 127.0.0.1 \
  --port 8788 \
  --path /gmail-pubsub \
  --token <shared> \
  --hook-url http://127.0.0.1:18789/hooks/gmail \
  --hook-token OPENCLAW_HOOK_TOKEN \
  --include-body \
  --max-bytes 20000
```

注意：

* `--token` 保护推送端点 (`x-gog-token` 或 `?token=`)。
* `--hook-url` 指向 Clawdbot `/hooks/gmail`（映射；隔离运行 + 摘要到主会话）。
* `--include-body` 和 `--max-bytes` 控制发送给 Clawdbot 的正文片段。
