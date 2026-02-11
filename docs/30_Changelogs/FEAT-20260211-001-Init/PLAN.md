# PLAN: VitePress 站点初始化与部署配置

## 1. 目标 (Objective)
初始化 OpenClaw 中文文档站项目结构，配置 VitePress，建立 Core/Cookbook 双目录架构，并产出 GitHub Actions 部署脚本。

## 2. 详细步骤 (Steps)

### Step 1: 项目初始化
- [ ] `pnpm init` & 安装 `vitepress`, `vue`, `tailwindcss`。
- [ ] 配置 `.gitignore`。
- [ ] 创建目录结构: `docs/core`, `docs/cookbook`, `docs/.vitepress`。

### Step 2: VitePress 配置
- [ ] `docs/.vitepress/config.ts`:
  - [ ] 启用 Local Search。
  - [ ] 配置中文 i18n (Locale: zh-CN)。
  - [ ] 配置双侧边栏 (Sidebar): 针对 `/core/` 和 `/cookbook/` 显示不同菜单。
  - [ ] 配置顶部导航 (Nav): 首页, 硬核手册, 入门教程, 官方仓库。

### Step 3: 内容迁移 (Mockup)
- [ ] **首页**: 创建 `docs/index.md` (Hero Section, Features)。
- [ ] **Cookbook**: 创建 `docs/cookbook/index.md` (从 `ALL_DOCS_零门槛阅读.md` 提取大纲)。
- [ ] **Core**: 创建 `docs/core/index.md` (占位，待同步)。

### Step 4: 部署脚本 (CI/CD)
- [ ] 创建 `.github/workflows/deploy.yml`。
- [ ] 配置 `rsync` deployment 到阿里云 ECS。
- [ ] **安全**: 提示用户在 GitHub Secrets 配置 `SSH_PRIVATE_KEY`, `SSH_HOST`, `SSH_USER`。

## 3. 风险评估 (Risks)
- **样式冲突**: Tailwind 可能会与 VitePress 默认样式冲突 -> 需在 `theme/style.css` 中重置。
- **部署权限**: 需要用户在 ECS 上配置 SSH Key 登录。

## 4. 验证 (Verification)
- 本地 `pnpm docs:dev` 可正常启动。
- 搜索功能可用。
- 手机端布局正常。
