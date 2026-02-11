# Mattermost

来源: https://clawd.org.cn/channels/mattermost.html

# Mattermost (插件)

状态：通过插件支持（机器人令牌 + WebSocket 事件）。支持频道、群组和私信。Mattermost 是一个可自托管的团队消息平台；有关产品详情和下载，请访问官方网站 [mattermost.com](https://mattermost.com)。

## 需要插件

Mattermost 作为插件发布，不随核心安装捆绑。

通过 CLI 安装（npm 注册表）：

bash

```
openclaw-cn plugins install @clawdbot/mattermost
```

本地检出（当从 git 仓库运行时）：

bash

```
openclaw-cn plugins install ./extensions/mattermost
```

如果在配置/入职过程中选择 Mattermost 并且检测到 git 检出，Clawdbot 将自动提供本地安装路径。

详情：[插件](/plugin.html)

## 快速设置

1. 安装 Mattermost 插件。
2. 创建 Mattermost 机器人账号并复制 **机器人令牌**。
3. 复制 Mattermost **基础 URL**（例如 `https://chat.example.com`）。
4. 配置 Clawdbot 并启动网关。

最小配置：

json5

```
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token",
      baseUrl: "https://chat.example.com",
      dmPolicy: "pairing"
    }
  }
}
```

## 环境变量（默认账号）

如果你更喜欢环境变量，请在网关主机上设置这些：

* `MATTERMOST_BOT_TOKEN=...`
* `MATTERMOST_URL=https://chat.example.com`

环境变量仅适用于 **默认** 账号 (`default`)。其他账号必须使用配置值。

## 聊天模式

Mattermost 会自动回复私信。频道行为由 `chatmode` 控制：

* `oncall`（默认）：仅当在频道中被 @提及 时回复。
* `onmessage`：回复每条频道消息。
* `onchar`：当消息以触发前缀开头时回复。

配置示例：

json5

```
{
  channels: {
    mattermost: {
      chatmode: "onchar",
      oncharPrefixes: [">", "!"]
    }
  }
}
```

注意：

* `onchar` 仍然会回复显式的 @提及。
* `channels.mattermost.requireMention` 适用于旧配置，但首选 `chatmode`。

## 访问控制（私信）

* 默认：`channels.mattermost.dmPolicy = "pairing"`（未知发送者会收到配对码）。
* 批准方式：
  + `openclaw-cn pairing list mattermost`
  + `openclaw-cn pairing approve mattermost <CODE>`
* 公共私信：`channels.mattermost.dmPolicy="open"` 加上 `channels.mattermost.allowFrom=["*"]`。

## 频道（群组）

* 默认：`channels.mattermost.groupPolicy = "allowlist"`（提及门控）。
* 使用 `channels.mattermost.groupAllowFrom` 将发送者加入白名单（用户 ID 或 `@username`）。
* 开放频道：`channels.mattermost.groupPolicy="open"`（提及门控）。

## 出站投递目标

将这些目标格式与 `openclaw-cn message send` 或 cron/webhook 一起使用：

* `channel:<id>` 用于频道
* `user:<id>` 用于私信
* `@username` 用于私信（通过 Mattermost API 解析）

裸 ID 被视为频道。

## 多账号

Mattermost 支持在 `channels.mattermost.accounts` 下配置多个账号：

json5

```
{
  channels: {
    mattermost: {
      accounts: {
        default: { name: "Primary", botToken: "mm-token", baseUrl: "https://chat.example.com" },
        alerts: { name: "Alerts", botToken: "mm-token-2", baseUrl: "https://alerts.example.com" }
      }
    }
  }
}
```

## 故障排除

* 频道中无回复：确保机器人已加入频道并提及它 (oncall)，使用触发前缀 (onchar)，或设置 `chatmode: "onmessage"`。
* 认证错误：检查机器人令牌、基础 URL 以及账号是否已启用。
* 多账号问题：环境变量仅适用于 `default` 账号。
