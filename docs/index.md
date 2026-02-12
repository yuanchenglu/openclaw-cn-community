---
layout: doc
displayAllHeaders: true
---

# 5分钟快速上手 (Quick Start)

> **目标**: 在 5 分钟内完成 OpenClaw 的安装与运行。
> **核心理念**: Direct to Value - 拒绝废话，直接运行。

## 1. 极速安装

打开终端 (Terminal 或 PowerShell)，复制并运行以下命令：

::: code-group

```bash [macOS / Linux]
curl -fsSL https://clawd.org.cn/install.sh | bash
```

```powershell [Windows]
iwr -useb https://clawd.org.cn/install.ps1 | iex
```

:::

## 2. 快速配置

安装完成后，输入以下命令启动交互式配置向导：

```bash
openclaw-cn onboard
```

向导将引导你完成最核心的设置：
1.  **选择 AI 模型**: 推荐选择 `DeepSeek` 或 `Qwen` (国内直连，无需代理)。
2.  **设置 API Key**: 输入你在对应平台的 Key。
3.  **选择接入渠道**: 选择 `WeChat` 或 `Terminal` (仅在终端测试)。

## 3. Hello World

配置完成后，立刻运行你的第一个 Agent：

```bash
openclaw-cn run --agent "hello-world"
```

如果一切正常，你应该会在终端看到 Agent 的回复。

---

### 下一步做什么？

- **想接入微信？** 查看 [接入微信/钉钉](/cookbook/integration-wechat)
- **想了解原理？** 阅读 [官方手册中文版](/core/)
- **遇到问题？** 进入 [社区讨论](https://github.com/yuanchenglu/openclaw-cn-community/issues)

