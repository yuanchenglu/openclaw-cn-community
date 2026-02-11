import { defineConfig } from 'vitepress'

export default defineConfig({
  // 部署到子目录必须配置 base
  base: '/openclaw/',

  // SEO 关键: Sitemap (VitePress 1.0 原生支持)
  sitemap: {
    hostname: 'https://ai.7color.vip/openclaw/'
  },

  title: "OpenClaw 中文社区",
  description: "中国开发者首选的 AI Agent 生态入口。提供 OpenClaw 全面中文文档、一键安装脚本及活跃的开发者社区。覆盖 Agent 开发、微信接入、自动化部署等实战教程。",
  lang: 'zh-CN',

  // 忽略死链接 (包括无法解析的图片引用)
  ignoreDeadLinks: true,

  vite: {
    plugins: [
      {
        name: 'ignore-missing-assets',
        enforce: 'pre',
        resolveId(source) {
          if (source.match(/\.(png|jpg|jpeg|gif|svg|webp)$/)) {
            // 尝试解析，如果失败则返回虚拟模块 ID
            return this.resolve(source).then(res => {
              if (!res) {
                console.warn(`[Build] Ignoring missing asset: ${source}`);
                return '\0virtual:missing-asset';
              }
              return res;
            }).catch(() => {
              console.warn(`[Build] Ignoring missing asset: ${source}`);
              return '\0virtual:missing-asset';
            });
          }
        },
        load(id) {
          if (id === '\0virtual:missing-asset') {
            // 返回一个透明的 1x1 GIF
            return `export default "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"`;
          }
        }
      }
    ]
  },

  // 头部 Meta 标签 (SEO 关键)
  head: [
    ['link', { rel: 'icon', href: '/openclaw/favicon.ico' }],
    ['meta', { name: 'keywords', content: 'OpenClaw, AI Agent, 中文文档, 智能体开发, 微信机器人, LLM应用, Clawd, 7Color AI' }],
    ['meta', { name: 'author', content: 'OpenClaw CN Community' }],
    // 百度收录优化 (需替换真实 code)
    ['meta', { name: 'baidu-site-verification', content: 'code-YOUR_CODE' }],
    // Open Graph
    ['meta', { property: 'og:title', content: 'OpenClaw 中文社区 - AI Agent 开发者门户' }],
    ['meta', { property: 'og:description', content: '一站式 OpenClaw 中文文档与工具集。从零构建你的专属 AI 智能体。' }],
    ['meta', { property: 'og:image', content: 'https://ai.7color.vip/openclaw/og-image.png' }]
  ],

  // 简洁的 URL (去掉 .html 后缀)
  cleanUrls: true,

  themeConfig: {
    // 顶部导航栏
    nav: [
      { text: '首页', link: '/' },
      { text: '硬核手册 (Core)', link: '/core/' },
      { text: '场景教程 (Cookbook)', link: '/cookbook/' },
      { text: '工具下载', link: '/tools/' }, // Phase 2 预留
      { text: '社区讨论', link: 'https://github.com/yuanchenglu/openclaw-cn-community/discussions' } // Phase 3 预留 (Giscus)
    ],

    // 侧边栏 (双模架构)
    sidebar: {
      '/core/': [
        {
          text: '入门 (Start)',
          collapsed: false,
          items: [
            { text: '入门指南', link: '/core/start/getting-started' },
            { text: '安装向导', link: '/core/start/wizard' },
            { text: '初始设置', link: '/core/start/setup' },
            { text: '配对设备', link: '/core/start/pairing' }
          ]
        },
        {
          text: '安装部署 (Install)',
          collapsed: true,
          items: [
            { text: '安装概述', link: '/core/install' },
            { text: 'Docker 部署', link: '/core/install/docker' },
            { text: 'Node.js 安装', link: '/core/install/node' },
            { text: '卸载', link: '/core/install/uninstall' }
          ]
        },
        {
          text: '核心概念 (Concepts)',
          collapsed: true,
          items: [
            { text: '架构总览', link: '/core/concepts/architecture' },
            { text: '智能体 (Agent)', link: '/core/concepts/agent' },
            { text: '会话 (Session)', link: '/core/concepts/session' },
            { text: '记忆 (Memory)', link: '/core/concepts/memory' },
            { text: '模型 (Models)', link: '/core/concepts/models' }
          ]
        },
        {
          text: '连接渠道 (Channels)',
          collapsed: true,
          items: [
            { text: 'WhatsApp', link: '/core/channels/whatsapp' },
            { text: 'Telegram', link: '/core/channels/telegram' },
            { text: 'Discord', link: '/core/channels/discord' },
            { text: 'Slack', link: '/core/channels/slack' },
            { text: '飞书 (Feishu)', link: '/core/channels/feishu' },
            { text: '微信 (WeChat)', link: '/core/community/wechat' }
          ]
        },
        {
          text: '工具与技能 (Tools)',
          collapsed: true,
          items: [
            { text: '工具概述', link: '/core/tools' },
            { text: '浏览器控制', link: '/core/tools/browser' },
            { text: '斜杠命令', link: '/core/tools/slash-commands' },
            { text: '技能配置', link: '/core/tools/skills-config' }
          ]
        },
        {
          text: 'AI 供应商 (Providers)',
          collapsed: true,
          items: [
            { text: '自定义供应商', link: '/core/guides/custom-ai-providers' },
            { text: 'OpenAI', link: '/core/providers/openai' },
            { text: 'Anthropic', link: '/core/providers/anthropic' },
            { text: 'MiniMax', link: '/core/providers/minimax' },
            { text: 'Moonshot', link: '/core/providers/moonshot' }
          ]
        },
        {
          text: '网关与安全 (Gateway)',
          collapsed: true,
          items: [
            { text: '操作手册', link: '/core/gateway' },
            { text: '配置示例', link: '/core/gateway/configuration-examples' },
            { text: '安全指南', link: '/core/gateway/security' },
            { text: '故障排除', link: '/core/gateway/troubleshooting' }
          ]
        },
        {
          text: '自动化 (Automation)',
          collapsed: true,
          items: [
            { text: '定时任务 (Cron)', link: '/core/automation/cron-jobs' },
            { text: 'Webhook', link: '/core/automation/webhook' },
            { text: 'Gmail 集成', link: '/core/automation/gmail-pubsub' }
          ]
        }
      ],
      '/cookbook/': [
        {
          text: '场景教程',
          items: [
            { text: '入门指南', link: '/cookbook/' },
            { text: '5分钟快速上手', link: '/cookbook/quick-start' },
            { text: '常见问题 (FAQ)', link: '/cookbook/faq' }
          ]
        },
        {
          text: '实战案例',
          items: [
            { text: '接入微信/钉钉', link: '/cookbook/integration-wechat' },
            { text: '编写第一个 Agent', link: '/cookbook/first-agent' }
          ]
        }
      ]
    },

    // 社交链接 (开源属性)
    socialLinks: [
      { icon: 'github', link: 'https://github.com/yuanchenglu/openclaw-cn-community' }
    ],

    // 页脚配置
    footer: {
      message: '基于 CC-BY-NC-SA 4.0 许可发布',
      copyright: 'Copyright © 2026 OpenClaw CN Community'
    },

    // 搜索配置 (本地搜索 - 国内极速)
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: {
                buttonText: '搜索文档',
                buttonAriaLabel: '搜索文档'
              },
              modal: {
                noResultsText: '无法找到相关结果',
                resetButtonTitle: '清除查询条件',
                footer: {
                  selectText: '选择',
                  navigateText: '切换'
                }
              }
            }
          }
        }
      }
    },

    // Wiki 协作配置
    editLink: {
      pattern: 'https://github.com/yuanchenglu/openclaw-cn-community/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页'
    },

    lastUpdated: {
      text: '最后更新于',
      formatOptions: {
        dateStyle: 'short',
        timeStyle: 'medium'
      }
    },

    // 移动端优化
    docFooter: {
      prev: '上一页',
      next: '下一页'
    }
  }
})
