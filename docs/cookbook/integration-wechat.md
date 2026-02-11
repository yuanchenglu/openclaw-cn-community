# 接入聊天软件

本教程将引导你将 OpenClaw 接入到常用的聊天平台。

## 接入微信 (WeChat)

> **注意**: 微信接入基于开源协议，存在封号风险，请使用小号测试。

### 1. 登录
在终端运行：
```bash
openclaw-cn channels login wechat
```

### 2. 扫码
终端会输出一个二维码。打开手机微信，扫描该二维码确认登录。

### 3. 验证
登录成功后，找个朋友（或用主号）给这个小号发消息："Hello"。
如果配置正确，AI 会自动回复。

---

## 接入 WhatsApp

### 1. 登录
在终端运行：
```bash
openclaw-cn channels login whatsapp
```

### 2. 扫码
打开 WhatsApp 手机端 -> 设置 -> 已连接设备 -> 连接设备 -> 扫描终端二维码。

---

## 接入 Telegram

> **前置条件**: 需要能够访问 Telegram 服务器的网络环境。

1. 在 Telegram 中搜索 `@BotFather`。
2. 发送 `/newbot` 创建一个机器人，获取 `API Token`。
3. 运行配置命令：
```bash
openclaw-cn config set telegram.token YOUR_API_TOKEN
```
4. 启动服务：
```bash
openclaw-cn gateway
```
