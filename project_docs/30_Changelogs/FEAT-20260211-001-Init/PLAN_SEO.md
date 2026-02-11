# PLAN: SEO & GEO 优化实施 (FEAT-20260211-004)

## 1. 目标
通过技术手段提升搜索引擎 (Baidu/Bing/Google) 收录率，并针对生成式 AI (Perplexity/Kimi) 优化内容结构。

## 2. 实施步骤

### Step 1: 基础 SEO 配置 (Completed)
- [x] **Meta Tags**: 在 `config.mts` 中添加 `keywords`, `description`, `author`, `og:image`。
- [x] **Sitemap**: 启用 VitePress 内置 Sitemap 生成功能 (VitePress v1.0+ 原生支持，无需插件)。
- [x] **Robots.txt**: 创建 `public/robots.txt` 指引爬虫。

### Step 2: 结构化数据 (Schema.org) (Pending)
- [ ] **JSON-LD**: 针对首页和教程页注入 Schema。
  - 首页: `SoftwareApplication`
  - 教程: `HowTo`
  - FAQ: `FAQPage`

### Step 3: 主动推送 (Action)
- [ ] **Baidu Push**: 编写脚本，在 CI/CD 成功部署后调用百度 API 推送链接。

## 3. 验证
- 构建后检查 `dist/sitemap.xml` 是否存在。
- 使用 Google Rich Results Test 验证 JSON-LD。
