# 定时任务 (Cron jobs - Gateway 调度器)

> **Cron 还是 Heartbeat?** 请参阅 [Cron vs Heartbeat](/automation/cron-vs-heartbeat.html) 了解何时使用哪种机制。

Cron 是 Gateway 内置的调度器。它持久化保存任务，在正确的时间唤醒 Agent，并可以选择将输出发送回聊天。

如果你想要 *“每天早上运行这个”* 或者 *“20分钟后提醒 Agent”*，Cron 就是你要用的机制。

## 配置

在你的 `config.json5` 中启用 cron 模块：

```json5
{
  cron: {
    enabled: true, // 默认为 true
    store: "~/.openclaw-cn/cron/jobs.json",
    maxConcurrentRuns: 1 // 默认为 1
  }
}
```

## 一次性提醒 (One-shot reminders)

你可以通过 CLI 调度任务。这通常用于提醒。

```bash
clawdbot cron add \
  --name "Send reminder" \
  --at "2026-01-12T18:00:00Z" \
  --session main \
  --system-event "Reminder: submit expense report." \
  --wake now \
  --delete-after-run
```

- `--at`: ISO 8601 时间戳。
- `--session`: 事件发送到的会话 ID。
- `--system-event`: 作为系统事件注入到会话中的文本。
- `--wake`: 如果为 `now`，立即唤醒 Agent 进行调度（可选）。
- `--delete-after-run`: 成功执行后删除任务。

## 周期性任务 (Recurring jobs)

使用标准的 cron 语法（例如 `0 9 * * *` 表示每天上午 9 点）。

```bash
clawdbot cron add \
  --name "Daily briefing" \
  --schedule "0 9 * * *" \
  --session main \
  --user-message "Good morning! Please summarize yesterday's logs."
```

## 执行方式 (Execution style)

默认情况下，cron 任务在后台运行。如果你希望 Agent 的响应发布到特定频道（例如 Slack），必须确保该会话已链接到该频道，或者使用显式发送消息的 `automation` 脚本。

如果 `--session` 引用的是现有的聊天会话（如 Slack 线程 ID），Agent 的输出将出现在那里（如果 Gateway 已连接）。

## 命令

- `clawdbot cron list`: 显示所有已调度的任务。
- `clawdbot cron remove <id>`: 删除任务。
- `clawdbot cron trigger <id>`: 强制立即运行任务。

## 故障排除 (Troubleshooting)

- **时区 (Timezones)**: 除非在配置或 ISO 字符串中指定了 UTC，否则调度器使用服务器的本地时间。
- **错过的任务 (Missed jobs)**: 如果 Gateway 宕机，错过的任务可能会在启动时运行，具体取决于 `missedJobBehavior`（v1 中尚未完全实现）。
