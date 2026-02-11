# 快速开始 (Quick Start)

> **目标**: 在 10 分钟内完成 OpenClaw 的安装与运行。
> **适用**: 所有新手用户。

## 1. 准备工作

### 硬件要求
- 一台电脑 (Windows / macOS / Linux)
- 网络连接正常

### 软件准备
- 一个聊天软件账号 (微信 / WhatsApp / Telegram 等)

---

## 2. 一键安装

根据你的操作系统选择对应的安装命令。

### macOS 用户
打开终端 (Terminal)，复制并运行：
```bash
curl -fsSL https://clawd.org.cn/install.sh | bash
```

### Windows 用户
打开 PowerShell (管理员模式)，复制并运行：
```powershell
iwr -useb https://clawd.org.cn/install.ps1 | iex
```

### Linux 用户
```bash
curl -fsSL https://clawd.org.cn/install.sh | bash
```

> **注意**: 如果下载速度慢，请检查网络设置或尝试更换时间段。

---

## 3. 设置向导 (Onboarding)

安装完成后，在终端输入以下命令启动向导：

```bash
openclaw-cn onboard
```

向导会引导你完成以下配置：
1. **选择 AI 模型**: 推荐 `DeepSeek` 或 `Qwen (通义千问)`，国内访问速度快且免费额度高。
2. **选择聊天平台**: 选择你希望 Agent 接入的平台。
3. **其他设置**: 一路回车保持默认即可。

---

## 4. 下一步

配置完成后，你的 OpenClaw 核心服务已经运行起来了。
接下来，请查看 [接入微信/钉钉](/cookbook/integration-wechat) 来让它真正“活”在你的聊天窗口里。
