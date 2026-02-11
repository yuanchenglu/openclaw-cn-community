# PLAN: 内容迁移与结构重构 (FEAT-20260211-002)

## 1. 目标
将现有的文档资料迁移至 VitePress 结构中，填充 `docs/core` (硬核版) 和 `docs/cookbook` (简易版) 的实际内容。

## 2. 步骤

### Step 1: Core Docs 迁移 (Completed)
- [x] 复制 `claw_docs_fenlei/` 所有内容到 `docs/core/`。
- [ ] **配置更新**: 修改 `docs/.vitepress/config.mts` 的 Sidebar，使其匹配 `claw_docs_fenlei/TOC.md` 的结构。

### Step 2: Cookbook Docs 重构
- [ ] **拆解源文件**: 读取 `ALL_DOCS_零门槛阅读.md`。
- [ ] **创建文件**:
  - `docs/cookbook/quick-start.md`: 提取 "10分钟快速上手" 章节。
  - `docs/cookbook/integration-wechat.md`: 提取 "连接你的聊天软件" 章节。
  - `docs/cookbook/faq.md`: 提取 "常见问题" 章节。
  - `docs/cookbook/first-agent.md`: 提取相关内容 (若有)。

### Step 3: 首页与导航微调
- [ ] 确保 `docs/core/index.md` 链接到正确的子页面。

## 3. 验证
- 运行 `npm run docs:dev`，检查所有链接是否有效。
