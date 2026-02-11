# 20_Tech_Architecture_Master: OpenClaw Community Platform

## 1. 架构总览 (Architecture Overview)
本项目采用 **“渐进式增强 (Progressive Enhancement)”** 架构，从 Phase 1 的静态站点平滑演进至 Phase 3 的全栈社区应用。

- **核心原则**:
  - **Static First**: 优先静态生成 (SSG)，确保极致加载速度和 SEO。
  - **Edge First**: 利用边缘计算 (Edge Functions) 处理动态请求。
  - **China Optimized**: 针对大陆网络环境优化资源加载策略。

---

## 2. Phase 1: 文档站架构 (The Knowledge Base)

### 2.1 技术选型 (Tech Stack)
- **框架**: **VitePress** (Vue 3驱动的静态站点生成器)
  - *理由*: 极速启动，构建快，原生支持 Markdown 扩展，国内社区活跃，方便后期集成 Vue 组件（为 Phase 2 工具铺路）。
- **语言**: TypeScript / Vue SFC.
- **搜索**: **Local Search** (VitePress 内置)
  - *理由*: 相比 Algolia，Local Search 无需外网 API 调用，零延迟，对大陆用户最友好，且完全免费。
- **样式**: Tailwind CSS (可选，用于定制化组件).

### 2.2 部署架构 (Deployment)
- **源码托管**: GitHub.
- **CI/CD**: GitHub Actions (自动构建).
- **Hosting Strategy (CN Optimized)**:
  - **方案 A (推荐)**: **Vercel** (目前国内访问尚可，需配置自定义域名).
  - **方案 B (备选)**: **Cloudflare Pages** (速度较快).
  - **方案 C (终极)**: GitHub Actions -> Build -> Push to **Aliyun OSS / Tencent COS** + CDN.
  - *决策*: Phase 1 暂用 Vercel，若被墙则切换至方案 C。

### 2.3 内容同步流水线 (Content Sync Pipeline)
用于解决“核心文档同步”需求。
1. **Trigger**: 每日定时 (Cron Job) 或 Upstream Repo 有 Commit 时触发。
2. **Action**:
   - `git submodule update` 拉取最新官方文档。
   - **Translator Bot (AI)**: 对比 Diff，调用 LLM API 翻译新增/修改段落。
   - **PR**: 自动提交 Pull Request 供人工/管理员审核。
   - **Merge**: 审核通过后自动发布。

---

## 3. Phase 2: 工具集架构 (The Toolchain)

### 3.1 CLI 工具 (Automation Scripts)
- **技术**: Bash (Linux/macOS) + PowerShell (Windows).
- **分发**: 托管在文档站 `/scripts/` 目录下，提供一行命令安装：
  ```bash
  curl -sSL https://openclaw.color.vip/install.sh | bash
  ```

### 3.2 GUI 客户端 (Desktop App)
- **框架**: **Tauri v2** (Rust + Frontend)
  - *理由*: 相比 Electron，安装包极小 (3-5MB vs 100MB+)，内存占用低。
  - *复用*: 前端直接复用文档站的 Vue 组件库。
- **功能**:
  - 环境检测 (Node/Python/Docker).
  - 镜像源切换 (NPM/Pip/HuggingFace Proxy).
  - 一键启动 OpenClaw Core。

---

## 4. Phase 3: 社区架构 (The Community)

### 4.1 后端服务 (Backend Services)
- **Database**: **Supabase** (PostgreSQL)
  - *理由*: 开源，提供 Auth, DB, Realtime, Storage 一体化服务。
- **API**: Serverless Functions (Vercel Functions).

### 4.2 社区功能实现
- **评论/问答**:
  - *轻量级*: 集成 **Giscus** (基于 GitHub Discussions)。
  - *深度定制*: 基于 Supabase 开发独立问答板块。
- **插件市场**:
  - 静态索引 JSON + GitHub Release 存储大文件。

---

## 5. 安全与合规 (Security & Compliance)
- **ICP**: 若使用国内 CDN/OSS，必须完成 ICP 备案。
- **数据合规**: 社区用户数据（Phase 3）需符合国内数据安全法规。

## 6. 目录结构规划
```
/
├── docs/               # 文档源文件 (Markdown)
│   ├── .vitepress/     # VitePress 配置
│   ├── core/           # 硬核版文档 (Sync from Upstream)
│   └── easy/           # 简易版文档 (Manual Crafted)
├── scripts/            # 自动化脚本 (Phase 2)
├── src/                # 自定义 Vue 组件 (Phase 2/3)
└── package.json
```
