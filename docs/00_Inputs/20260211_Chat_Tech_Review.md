# 00_Review_Product_Feedback: 技术部对 PRD 的评审意见

**Reviewer**: 技术总监 (Status B)
**Date**: 2026-02-11
**Target Doc**: `10_Product_Master.md` & `11_Feat_Phase1_Website.md`

## 1. 总体评价 (General Assessment)
文档结构清晰，愿景明确。分阶段落地的策略符合工程化实施原则。
但作为技术负责人，我发现几个 **高风险点** 和 **可优化项**，建议在开发前修正。

## 2. 核心风险与漏洞 (Critical Risks)

### 2.1 "实时同步"的可行性 (Real-time Sync Feasibility)
- **PRD原文**: “与官方文档实时同步更新”。
- **技术反驳**: 
  - “实时”在工程上意味着极高的维护成本（Webhooks 触发、极速构建）。
  - 且官方文档更新可能包含未翻译的英文，直接同步会导致中英混杂，体验极差。
- **修正建议**: 改为 **“每日构建 (Daily Build)”** 或 **“版本对齐 (Version Pinned)”**。
  - 建立缓冲区：官方更新 -> AI 预翻译 -> 人工/脚本校验 -> 发布。确保发布的中文文档是高质量的。

### 2.2 双版本维护地狱 (Dual-Mode Maintenance Hell)
- **PRD原文**: “Core Docs (硬核)” + “Easy Docs (简易)”。
- **技术反驳**: 
  - 这是一个典型的“文档债务陷阱”。当 OpenClaw 软件逻辑变更（例如 API 参数变了），Core Docs 可以自动拉取更新，但 Easy Docs 是人工重写的，大概率会忘记更新，导致“小白照着简易版做，结果报错”的灾难。
- **修正建议**: 
  - **Core Docs**: 保持自动化同步。
  - **Easy Docs**: **不要做成全量文档的简化版**。而是做成 **“Cookbook / Guides（教程集）”**。
  - 教程是针对特定场景（如“如何安装”、“如何写第一个 Agent”）的，不会像 API 文档那样频繁变动。

### 2.3 国内网络与域名 (Network & Domain)
- **PRD原文**: 域名 `openclaw.color.vip`。
- **技术反驳**: 
  - `.vip` 域名在国内备案审核可能较严（视具体注册商而定）。
  - 如果目标是“中国大陆用户体验”，仅靠 Vercel/GitHub Pages 大概率会被墙或极慢。
- **修正建议**: 
  - Phase 1 可以先跑在 Vercel 上。
  - 但必须预留 **CDN 预算** 或 **OSS 部署方案**。
  - 建议技术部在 `20_Tech_Architecture.md` 中增加“国内镜像源加速”的具体技术方案。

## 3. 架构优化建议 (Architecture Suggestions)

### 3.1 搜索技术选型
- 建议放弃 Algolia（配置繁琐、免费额度限制、国内速度一般）。
- 直接使用 **Minisearch / VitePress Local Search**。纯前端实现，离线可用，速度最快。

### 3.2 社区冷启动
- Phase 3 的社区功能开发成本高。
- 建议在 Phase 1 直接集成 **Giscus** (利用 GitHub Discussions 存储评论)。
- 优点：零后端成本、天然的开发者账户体系、数据在 GitHub 上（安全）。

## 4. 结论 (Conclusion)
请产品经理（小路）确认以上修正案：
1. 同意将“实时同步”降级为“每日/版本同步”。
2. 同意将“简易版文档”重新定义为“入门教程 (Guides/Cookbook)”。
3. 确认是否接受 Phase 1 使用 Giscus 作为轻量级评论系统？

**状态**: 等待产品部确认 (Pending PM Approval)。
