# 钩子

Source: https://clawd.org.cn/hooks.html

# Hooks

钩子提供了一个可扩展的事件驱动系统，用于响应智能体命令和事件自动执行操作。钩子可以从目录中自动发现，并可以通过 CLI 命令进行管理，类似于 Clawdbot 中技能的工作方式。

## 快速了解

钩子是发生某些事情时运行的小脚本。有两种类型：

* **Hooks**（本页）：在智能体事件触发时在网关内部运行，如 `/new`、`/reset`、`/stop` 或生命周期事件。
* **Webhooks**：外部 HTTP webhooks，允许其他系统在 Clawdbot 中触发工作。请参阅 [Webhook 钩子](/automation/webhook.html) 或使用 `clawdbot webhooks` 获取 Gmail 辅助命令。

钩子也可以捆绑在插件内；请参阅 [插件](/plugin.html#plugin-hooks)。

常见用途：

* 当你重置会话时保存记忆快照
* 保留所有命令的审计跟踪以进行故障排除或合规性检查
* 当会话开始或结束时触发后续自动化
* 当事件触发时将文件写入智能体工作区或调用外部 API

如果你能写一个小的 TypeScript 函数，你就能写一个钩子。钩子会被自动发现，你可以通过 CLI 启用或禁用它们。

## 概览

钩子系统允许你：

* 当发出 `/new` 时将会话上下文保存到记忆中
* 记录所有命令以进行审计
* 在智能体生命周期事件上触发自定义自动化
* 扩展 Clawdbot 的行为而无需修改核心代码

## 开始使用

### 捆绑钩子

Clawdbot 附带了四个自动发现的捆绑钩子：

* **💾 session-memory**：当你发出 `/new` 时，将会话上下文保存到你的智能体工作区（默认 `~/clawwork/memory/`）
* **📝 command-logger**：将所有命令事件记录到 `~/.openclaw/logs/commands.log`
* **🚀 boot-md**：当网关启动时运行 `BOOT.md`（需要启用内部钩子）
* **😈 soul-evil**：在清洗窗口期间或随机地将注入的 `SOUL.md` 内容替换为 `SOUL_EVIL.md`

列出可用钩子：

bash

```
clawdbot hooks list
```

启用钩子：

bash

```
clawdbot hooks enable session-memory
```

检查钩子状态：

bash

```
clawdbot hooks check
```

获取详细信息：

bash

```
clawdbot hooks info session-memory
```

### 入职

在入职期间 (`openclaw-cn onboard`)，系统会提示你启用推荐的钩子。向导会自动发现符合条件的钩子并将其显示以供选择。

## 钩子发现

钩子会自动从三个目录（按优先级顺序）发现：

1. **工作区钩子**：`<workspace>/hooks/`（每个智能体，最高优先级）
2. **托管钩子**：`~/.openclaw/hooks/`（用户安装，跨工作区共享）
3. **捆绑钩子**：`<clawdbot>/dist/hooks/bundled/`（随 Clawdbot 附带）

托管钩子目录可以是**单个钩子**或**钩子包**（包目录）。

每个钩子都是一个包含以下内容的目录：

```
my-hook/
├── HOOK.md          # 元数据 + 文档
└── handler.ts       # 处理程序实现
```

## 钩子包 (npm/archives)

钩子包是标准的 npm 包，通过 `package.json` 中的 `openclaw.hooks` 导出一个或多个钩子。使用以下命令安装它们：

bash

```
clawdbot hooks install <path-or-spec>
```

示例 `package.json`：

json

```
{
  "name": "@acme/my-hooks",
  "version": "0.1.0",
  "clawdbot": {
    "hooks": ["./hooks/my-hook", "./hooks/other-hook"]
  }
}
```

每个条目指向一个包含 `HOOK.md` 和 `handler.ts`（或 `index.ts`）的钩子目录。钩子包可以附带依赖项；它们将安装在 `~/.openclaw/hooks/<id>` 下。

## 钩子结构

### HOOK.md 格式

`HOOK.md` 文件包含 YAML frontmatter 中的元数据加上 Markdown 文档：

markdown

```
---
name: my-hook
description: "Short description of what this hook does"
homepage: https://docs.clawd.bot/hooks#my-hook
metadata: {"clawdbot":{"emoji":"🔗","events":["command:new"],"requires":{"bins":["node"]}}}
---

# My Hook

Detailed documentation goes here...

## What It Does

- Listens for `/new` commands
- Performs some action
- Logs the result

## Requirements

- Node.js must be installed

## Configuration

No configuration needed.
```

### 元数据字段

`metadata.openclaw` 对象支持：

* **`emoji`**：CLI 显示表情符号（例如 `"💾"`）
* **`events`**：要监听的事件数组（例如 `["command:new", "command:reset"]`）
* **`export`**：要使用的命名导出（默认为 `"default"`）
* **`homepage`**：文档 URL
* **`requires`**：可选要求
  + **`bins`**：PATH 上所需的二进制文件（例如 `["git", "node"]`）
  + **`anyBins`**：必须存在这些二进制文件中的至少一个
  + **`env`**：所需的环境变量
  + **`config`**：所需的配置路径（例如 `["workspace.dir"]`）
  + **`os`**：所需的平台（例如 `["darwin", "linux"]`）
* **`always`**：绕过资格检查（布尔值）
* **`install`**：安装方法（对于捆绑钩子：`[{"id":"bundled","kind":"bundled"}]`）

### 处理程序实现

`handler.ts` 文件导出一个 `HookHandler` 函数：

typescript

```
import type { HookHandler } from '../../src/hooks/hooks.js';

const myHandler: HookHandler = async (event) => {
  // Only trigger on 'new' command
  if (event.type !== 'command' || event.action !== 'new') {
    return;
  }

  console.log(`[my-hook] New command triggered`);
  console.log(`  Session: ${event.sessionKey}`);
  console.log(`  Timestamp: ${event.timestamp.toISOString()}`);

  // Your custom logic here

  // Optionally send message to user
  event.messages.push('✨ My hook executed!');
};

export default myHandler;
```

#### 事件上下文

每个事件包括：

typescript

```
{
  type: 'command' | 'session' | 'agent' | 'gateway',
  action: string,              // e.g., 'new', 'reset', 'stop'
  sessionKey: string,          // Session identifier
  timestamp: Date,             // When the event occurred
  messages: string[],          // Push messages here to send to user
  context: {
    sessionEntry?: SessionEntry,
    sessionId?: string,
    sessionFile?: string,
    commandSource?: string,    // e.g., 'whatsapp', 'telegram'
    senderId?: string,
    workspaceDir?: string,
    bootstrapFiles?: WorkspaceBootstrapFile[],
    cfg?: ClawdbotConfig
  }
}
```

## 事件类型

### 命令事件

当发出智能体命令时触发：

* **`command`**：所有命令事件（通用监听器）
* **`command:new`**：当发出 `/new` 命令时
* **`command:reset`**：当发出 `/reset` 命令时
* **`command:stop`**：当发出 `/stop` 命令时

### 智能体事件

* **`agent:bootstrap`**：在工作区引导文件注入之前（钩子可以修改 `context.bootstrapFiles`）

### 网关事件

当网关启动时触发：

* **`gateway:startup`**：在频道启动且钩子加载之后

### 工具结果钩子 (插件 API)

这些钩子不是事件流监听器；它们允许插件在 Clawdbot 持久化工具结果之前同步调整它们。

* **`tool_result_persist`**：在工具结果写入会话记录之前转换它们。必须是同步的；返回更新后的工具结果有效负载或 `undefined` 以保持原样。请参阅 [智能体循环](/concepts/agent-loop.html)。

### 未来事件

计划的事件类型：

* **`session:start`**：当新会话开始时
* **`session:end`**：当会话结束时
* **`agent:error`**：当智能体遇到错误时
* **`message:sent`**：当消息发送时
* **`message:received`**：当收到消息时

## 创建自定义钩子

### 1. 选择位置

* **工作区钩子** (`<workspace>/hooks/`)：每个智能体，最高优先级
* **托管钩子** (`~/.openclaw/hooks/`)：跨工作区共享

### 2. 创建目录结构

bash

```
mkdir -p ~/.openclaw/hooks/my-hook
cd ~/.openclaw/hooks/my-hook
```

### 3. 创建 HOOK.md

markdown

```
---
name: my-hook
description: "Does something useful"
metadata: {"clawdbot":{"emoji":"🎯","events":["command:new"]}}
---

# My Custom Hook

This hook does something useful when you issue `/new`.
```

### 4. 创建 handler.ts

typescript

```
import type { HookHandler } from '../../src/hooks/hooks.js';

const handler: HookHandler = async (event) => {
  if (event.type !== 'command' || event.action !== 'new') {
    return;
  }

  console.log('[my-hook] Running!');
  // Your logic here
};

export default handler;
```

### 5. 启用并测试

bash

```
# Verify hook is discovered
clawdbot hooks list

# Enable it
clawdbot hooks enable my-hook

# Restart your gateway process (menu bar app restart on macOS, or restart your dev process)

# Trigger the event
# Send /new via your messaging channel
```

## 配置

### 新配置格式 (推荐)

json

```
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "session-memory": { "enabled": true },
        "command-logger": { "enabled": false }
      }
    }
  }
}
```

### 每个钩子的配置

钩子可以有自定义配置：

json

```
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "my-hook": {
          "enabled": true,
          "env": {
            "MY_CUSTOM_VAR": "value"
          }
        }
      }
    }
  }
}
```

### 额外目录

从额外目录加载钩子：

json

```
{
  "hooks": {
    "internal": {
      "enabled": true,
      "load": {
        "extraDirs": ["/path/to/more/hooks"]
      }
    }
  }
}
```

### 遗留配置格式 (仍然支持)

旧的配置格式仍然有效以保持向后兼容性：

json

```
{
  "hooks": {
    "internal": {
      "enabled": true,
      "handlers": [
        {
          "event": "command:new",
          "module": "./hooks/handlers/my-handler.ts",
          "export": "default"
        }
      ]
    }
  }
}
```

**迁移**：使用新的基于发现的系统来创建新钩子。遗留处理程序在基于目录的钩子之后加载。

## CLI 命令

### 列出钩子

bash

```
# List all hooks
clawdbot hooks list

# Show only eligible hooks
clawdbot hooks list --eligible

# Verbose output (show missing requirements)
clawdbot hooks list --verbose

# JSON output
clawdbot hooks list --json
```

### 钩子信息

bash

```
# Show detailed info about a hook
clawdbot hooks info session-memory

# JSON output
clawdbot hooks info session-memory --json
```

### 检查资格

bash

```
# Show eligibility summary
clawdbot hooks check

# JSON output
clawdbot hooks check --json
```

### 启用/禁用

bash

```
# Enable a hook
clawdbot hooks enable session-memory

# Disable a hook
clawdbot hooks disable command-logger
```

## 捆绑钩子

### session-memory

当你发出 `/new` 时，将会话上下文保存到记忆中。

**事件**：`command:new`

**要求**：必须配置 `workspace.dir`

**输出**：`<workspace>/memory/YYYY-MM-DD-slug.md`（默认为 `~/clawd`）

**它做什么**：

1. 使用重置前的会话条目来定位正确的记录
2. 提取最后 15 行对话
3. 使用 LLM 生成描述性文件名 slug
4. 将会话元数据保存到带日期的记忆文件中

**示例输出**：

markdown

```
# Session: 2026-01-16 14:30:00 UTC

- **Session Key**: agent:main:main
- **Session ID**: abc123def456
- **Source**: telegram
```

**文件名示例**：

* `2026-01-16-vendor-pitch.md`
* `2026-01-16-api-design.md`
* `2026-01-16-1430.md`（如果 slug 生成失败，回退时间戳）

**启用**：

bash

```
clawdbot hooks enable session-memory
```

### command-logger

将所有命令事件记录到集中审计文件。

**事件**：`command`

**要求**：无

**输出**：`~/.openclaw/logs/commands.log`

**它做什么**：

1. 捕获事件详情（命令操作、时间戳、会话密钥、发送者 ID、来源）
2. 以 JSONL 格式追加到日志文件
3. 在后台静默运行

**示例日志条目**：

jsonl

```
{"timestamp":"2026-01-16T14:30:00.000Z","action":"new","sessionKey":"agent:main:main","senderId":"+1234567890","source":"telegram"}
{"timestamp":"2026-01-16T15:45:22.000Z","action":"stop","sessionKey":"agent:main:main","senderId":"user@example.com","source":"whatsapp"}
```

**查看日志**：

bash

```
# View recent commands
tail -n 20 ~/.openclaw/logs/commands.log

# Pretty-print with jq
cat ~/.openclaw/logs/commands.log | jq .

# Filter by action
grep '"action":"new"' ~/.openclaw/logs/commands.log | jq .
```

**启用**：

bash

```
clawdbot hooks enable command-logger
```

### soul-evil

在清洗窗口期间或随机地将注入的 `SOUL.md` 内容替换为 `SOUL_EVIL.md`。

**事件**：`agent:bootstrap`

**文档**：[SOUL Evil Hook](/hooks/soul-evil.html)

**输出**：不写入文件；交换仅在内存中发生。

**启用**：

bash

```
clawdbot hooks enable soul-evil
```

**配置**：

json

```
{
  "hooks": {
    "internal": {
      "enabled": true,
      "entries": {
        "soul-evil": {
          "enabled": true,
          "file": "SOUL_EVIL.md",
          "chance": 0.1,
          "purge": { "at": "21:00", "duration": "15m" }
        }
      }
    }
  }
}
```

### boot-md

当网关启动时运行 `BOOT.md`（在频道启动后）。必须启用内部钩子才能运行此功能。

**事件**：`gateway:startup`

**要求**：必须配置 `workspace.dir`

**它做什么**：

1. 从你的工作区读取 `BOOT.md`
2. 通过智能体运行器运行指令
3. 通过消息工具发送任何请求的出站消息

**启用**：

bash

```
clawdbot hooks enable boot-md
```

## 最佳实践

### 保持处理程序快速

钩子在命令处理期间运行。保持它们轻量级：

typescript

```
// ✓ Good - async work, returns immediately
const handler: HookHandler = async (event) => {
  void processInBackground(event); // Fire and forget
};

// ✗ Bad - blocks command processing
const handler: HookHandler = async (event) => {
  await slowDatabaseQuery(event);
  await evenSlowerAPICall(event);
};
```

### 优雅地处理错误

始终包装有风险的操作：

typescript

```
const handler: HookHandler = async (event) => {
  try {
    await riskyOperation(event);
  } catch (err) {
    console.error('[my-handler] Failed:', err instanceof Error ? err.message : String(err));
    // Don't throw - let other handlers run
  }
};
```

### 尽早过滤事件

如果事件不相关，请尽早返回：

typescript

```
const handler: HookHandler = async (event) => {
  // Only handle 'new' commands
  if (event.type !== 'command' || event.action !== 'new') {
    return;
  }

  // Your logic here
};
```

### 使用特定事件键

尽可能在元数据中指定确切事件：

yaml

```
metadata: {"clawdbot":{"events":["command:new"]}}  # Specific
```

而不是：

yaml

```
metadata: {"clawdbot":{"events":["command"]}}      # General - more overhead
```

## 调试

### 启用钩子日志记录

网关在启动时记录钩子加载：

```
Registered hook: session-memory -> command:new
Registered hook: command-logger -> command
Registered hook: boot-md -> gateway:startup
```

### 检查发现

列出所有发现的钩子：

bash

```
clawdbot hooks list --verbose
```

### 检查注册

在你的处理程序中，记录它何时被调用：

typescript

```
const handler: HookHandler = async (event) => {
  console.log('[my-handler] Triggered:', event.type, event.action);
  // Your logic
};
```

### 验证资格

检查为什么钩子不符合条件：

bash

```
clawdbot hooks info my-hook
```

在输出中查找缺失的要求。

## 测试

### 网关日志

监控网关日志以查看钩子执行情况：

bash

```
# macOS
./scripts/clawlog.sh -f

# Other platforms
tail -f ~/.openclaw/gateway.log
```

### 直接测试钩子

隔离测试你的处理程序：

typescript

```
import { test } from 'vitest';
import { createHookEvent } from './src/hooks/hooks.js';
import myHandler from './hooks/my-hook/handler.js';

test('my handler works', async () => {
  const event = createHookEvent('command', 'new', 'test-session', {
    foo: 'bar'
  });

  await myHandler(event);

  // Assert side effects
});
```

## 架构

### 核心组件

* **`src/hooks/types.ts`**：类型定义
* **`src/hooks/workspace.ts`**：目录扫描和加载
* **`src/hooks/frontmatter.ts`**：HOOK.md 元数据解析
* **`src/hooks/config.ts`**：资格检查
* **`src/hooks/hooks-status.ts`**：状态报告
* **`src/hooks/loader.ts`**：动态模块加载器
* **`src/cli/hooks-cli.ts`**：CLI 命令
* **`src/gateway/server-startup.ts`**：在网关启动时加载钩子
* **`src/auto-reply/reply/commands-core.ts`**：触发命令事件

### 发现流程

```
Gateway startup
    ↓
Scan directories (workspace → managed → bundled)
    ↓
Parse HOOK.md files
    ↓
Check eligibility (bins, env, config, os)
    ↓
Load handlers from eligible hooks
    ↓
Register handlers for events
```

### 事件流程

```
User sends /new
    ↓
Command validation
    ↓
Create hook event
    ↓
Trigger hook (all registered handlers)
    ↓
Command processing continues
    ↓
Session reset
```

## 故障排除

### 钩子未被发现

1. 检查目录结构：

   bash

   ```
   ls -la ~/.openclaw/hooks/my-hook/
   # Should show: HOOK.md, handler.ts
   ```
2. 验证 HOOK.md 格式：

   bash

   ```
   cat ~/.openclaw/hooks/my-hook/HOOK.md
   # Should have YAML frontmatter with name and metadata
   ```
3. 列出所有发现的钩子：

   bash

   ```
   clawdbot hooks list
   ```

### 钩子不符合条件

检查要求：

bash

```
clawdbot hooks info my-hook
```

查找缺失的：

* 二进制文件（检查 PATH）
* 环境变量
* 配置值
* OS 兼容性

### 钩子未执行

1. 验证钩子已启用：

   bash

   ```
   clawdbot hooks list
   # Should show ✓ next to enabled hooks
   ```
2. 重启你的网关进程以便钩子重新加载。
3. 检查网关日志是否有错误：

   bash

   ```
   ./scripts/clawlog.sh | grep hook
   ```

### 处理程序错误

检查 TypeScript/导入错误：

bash

```
# Test import directly
node -e "import('./path/to/handler.ts').then(console.log)"
```

## 迁移指南

### 从遗留配置到发现

**之前**：

json

```
{
  "hooks": {
    "internal": {
      "enabled": true,
      "handlers": [
        {
          "event": "command:new",
          "module": "./hooks/handlers/my-handler.ts"
        }
      ]
    }
  }
}
```

**之后**：

1. 创建钩子目录：

   bash

   ```
   mkdir -p ~/.openclaw/hooks/my-hook
   mv ./hooks/handlers/my-handler.ts ~/.openclaw/hooks/my-hook/handler.ts
   ```
2. 创建 HOOK.md：

   markdown

   ```
   ---
   name: my-hook
   description: "My custom hook"
   metadata: {"clawdbot":{"emoji":"🎯","events":["command:new"]}}
   ---

   # My Hook

   Does something useful.
   ```
3. 更新配置：

   json

   ```
   {
     "hooks": {
       "internal": {
         "enabled": true,
         "entries": {
           "my-hook": { "enabled": true }
         }
       }
     }
   }
   ```
4. 验证并重启你的网关进程：

   bash

   ```
   clawdbot hooks list
   # Should show: 🎯 my-hook ✓
   ```

**迁移的好处**：

* 自动发现
* CLI 管理
* 资格检查
* 更好的文档
* 一致的结构

## 另请参阅

* [CLI 参考：hooks](/cli/hooks.html)
