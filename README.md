# OpenClaw 中文社区文档站

> 这是一个基于 VitePress 构建的静态文档站点，旨在为中国开发者提供 OpenClaw 的中文技术支持。

## 快速开始

### 本地开发
```bash
# 安装依赖
npm install

# 启动开发服务器
npm run docs:dev
```
访问 `http://localhost:5173/openclaw/` 进行预览。

### 构建与预览
```bash
# 构建静态文件
npm run docs:build

# 预览构建产物
npm run docs:preview
```

## 部署指南

本项目配置了 GitHub Actions 自动部署至阿里云 ECS。
详细配置步骤请参考：[部署指南 (Deployment Guide)](docs/20_Specs/21_Deployment_Guide.md)

## 目录结构
- `docs/core/`: 官方硬核技术文档 (Synced from upstream)
- `docs/cookbook/`: 中文场景化教程 (Community driven)
- `docs/.vitepress/`: 站点配置与主题

## 贡献
欢迎提交 Pull Request！所有修改请遵循 "Docs as Code" 规范。
