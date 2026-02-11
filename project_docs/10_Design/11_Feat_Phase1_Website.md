# 11_Feat_Phase1_Website: OpenClaw 中文文档站

## Dependencies
- [10_Product_Master.md](./10_Product_Master.md)
- 源文件: `root/AGENTS.md` 及其他 Markdown 资料

## 1. 概述 (One-Liner)
搭建 `openclaw.color.vip` 静态网站，提供“官方硬核”与“小白简易”双版本中文文档，支持全站搜索与深色模式。

## 2. 核心功能 (Feature Specs)

### 2.1 双模文档架构 (Dual-Mode Documentation)
- **Core Docs (硬核版)**:
  - **来源**: 1:1 翻译官方 `AGENTS.md` 及技术手册。
  - **受众**: 开发者、架构师。
  - **结构**: 保持与官方一致，方便对照。
  - **同步机制**: 每日自动拉取官方 Repo -> AI 辅助翻译 -> 人工校验 -> 发布。
- **Easy Docs (简易版)**:
  - **来源**: 基于 `ALL_DOCS_零门槛阅读.md` 重构。
  - **受众**: 非技术背景用户。
  - **风格**: 口语化、图文并茂、去除晦涩术语。
  - **结构**:
    1. 快速开始 (5分钟跑通)
    2. 常见问题 (FAQ)
    3. 最佳实践故事

### 2.2 搜索增强 (Search)
- 集成 Algolia 或类似本地搜索引擎。
- 支持关键词高亮。
- 混合搜索：同时索引 Core 和 Easy 文档。

### 2.3 版本控制 (Versioning)
- 页面右上角提供 OpenClaw 版本切换 (如 v1.0, v1.1)。
- 提示当前文档对应的软件版本。

## 3. 用户体验 (UX/UI)
- **风格**: 极简、技术感、护眼。
- **主题**: 支持 Light/Dark 切换 (默认跟随系统)。
- **导航**: 左侧固定目录树，右侧本页大纲 (TOC)。
- **响应式**: 完美适配移动端阅读。

## 4. 技术选型建议 (Tech Stack Suggestion)
*注：具体实现由技术部决定，此处仅为建议*
- **框架**: VitePress (推荐，Vue 生态，轻量高性能) 或 Docusaurus (React 生态)。
- **部署**: Vercel / Netlify / 腾讯云 Webify。
- **CI/CD**: GitHub Actions 实现自动构建与同步。

## 5. 验收标准 (DoD)
1. 域名 `openclaw.color.vip` 可访问，HTTPS 正常。
2. 首页清晰展示“硬核版”与“简易版”入口。
3. 搜索框输入 "Agent" 能搜到相关文档。
4. 手机端访问无排版错乱。
5. 包含 `AGENTS.md` 的完整中文内容。

## 6. Non-Goals (本期不做)
- 用户登录系统。
- 评论功能 (Phase 3)。
- 在线运行/调试代码。
