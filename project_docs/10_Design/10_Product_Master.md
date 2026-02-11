# OpenClaw Project Architecture Design

## 1. 核心设计理念 (Core Philosophy)
作为 OpenClaw 中文社区，我们的目标不仅仅是翻译文档，而是构建一个**开发者生态系统 (Developer Ecosystem)**。结构设计应遵循以下原则：

1.  **单一事实来源 (Single Source of Truth)**：`docs/` 是唯一的官方文档网站源码，所有其他文档（如 `claw_docs_*`）应归档或合并。
2.  **功能模块化 (Modularity)**：文档、工具 (GUI)、插件 (Plugins)、社区 (Community) 应物理分离，但在逻辑上通过统一门户（网站）连接。
3.  **Wiki 协作模式**：采用类似 Wikipedia 的协作机制，明确“维护者”与“贡献者”的权责。

---

## 2. 目录结构详解 (Directory Structure)

我们将项目根目录重构为以下清晰的模块：

```
openclawtools/
├── docs/                   # [核心] 官方文档网站 (VitePress Source Root)
│   ├── core/               # 核心概念与手册 (The "Truth" - Synced from upstream)
│   ├── cookbook/           # 实战教程与案例 (Community driven)
│   ├── public/             # 静态资源 (图片、favicon 等)
│   └── .vitepress/         # 网站配置 (Config, Theme)
│
├── gui/                    # [新增] 图形化安装配置工具 (GUI Installer)
│   ├── src/                # 源码 (Electron/Tauri/Web)
│   ├── build/              # 构建产物
│   └── README.md           # 开发指南
│
├── plugins/                # [新增] 插件生态 (Plugin Registry)
│   ├── official/           # 官方维护的核心插件
│   ├── community/          # 社区提交的插件 (或 git submodule)
│   └── templates/          # 插件开发模版
│
├── community/              # [新增] 社区治理 (Governance)
│   ├── RFCs/               # 请求意见稿 (Request for Comments)
│   └── DISCUSSIONS.md      # 论坛/Issue 引导页
│
├── scripts/                # [工具] 项目维护脚本
│   ├── crawler/            # 文档爬取与处理
│   │   └── legacy/         # 归档的历史数据 (原 claw_docs_*)
│   └── release/            # 发布脚本
│
├── project_docs/           # [管理] 项目管理 (Inputs, Design, Specs) - 仅限维护者
│
├── README.md               # 项目总入口
└── LICENSE                 # 开源协议
```

### 2.1 网站内容架构 (Website Content Architecture)
网站基于 **VitePress** 构建，采用双模内容架构：

1.  **Core (硬核手册)**:
    *   **位置**: `docs/core/`
    *   **定位**: 权威参考，通常同步自官方英文文档或由核心维护者编写。
    *   **结构**: 包含 `concepts`, `guides`, `reference` 等子目录。
    *   **侧边栏**: 在 `.vitepress/config.mts` 中通过 `/core/` 路径前缀独立配置。

2.  **Cookbook (场景教程)**:
    *   **位置**: `docs/cookbook/`
    *   **定位**: 社区驱动的实战案例，“手把手教你做”。
    *   **现状**: 目前包含 `quick-start.md`, `integration-wechat.md` 等起步教程。
    *   **扩展**: 未来随着社区贡献增加，将包含更多特定场景的解决方案。

---

## 3. 角色与权限体系 (Roles & Responsibilities)

仿照 Wikipedia 和成熟开源项目，设立以下角色：

### 核心维护者 (Core Maintainers) - "Admin"
*   **职责**：架构决策、合并 PR、发布版本、管理 `project_docs/`。
*   **权限**：Git Write 权限，NPM 发布权限。

### 建园者 (Gardeners) - "Editors"
*   **职责**：主要负责 `docs/` 的翻译、校对和更新。确保文档的准确性和可读性。
*   **权限**：对 `docs/` 目录的 Review 权限。

### 工具匠 (Toolsmiths)
*   **职责**：专注于 `gui/` 工具的开发和 `scripts/` 的维护。
*   **权限**：对 `gui/` 和 `scripts/` 目录的 Review 权限。

### 插件开发者 (Plugin Devs)
*   **职责**：在 `plugins/` 目录提交插件或维护自己的插件仓库。

---

## 4. 运作流程 (Workflows)

### 4.1 文档协作 (The Wiki Way)
*   所有文档修改必须包含在该 PR 的 `docs/30_Changelogs` 中。
*   对于重大修改（如术语变更），需先在 `community/RFCs` 提交 Proposal。

### 4.2 插件提交
*   开发者 Fork 仓库 -> 在 `plugins/community/` 添加子模块或描述文件 -> 提交 PR -> 自动化测试验证 -> 合并。

### 4.3 社区讨论
*   **GitHub Issues**: 仅用于 Bug 报告和具体任务追踪。
*   **GitHub Discussions / 论坛**: 用于“怎么做”、“好主意”等开放式讨论。
