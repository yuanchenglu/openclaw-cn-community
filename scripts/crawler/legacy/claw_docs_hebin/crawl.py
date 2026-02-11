#!/usr/bin/env python3
"""
OpenClaw 中文版文档爬虫
爬取 https://clawd.org.cn 的所有文档页面
"""

import os
import re
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin

BASE_URL = "https://clawd.org.cn"
OUTPUT_DIR = Path(__file__).parent
PLAN_FILE = OUTPUT_DIR / "CRAWL_PLAN.md"
ALL_DOCS_FILE = OUTPUT_DIR / "ALL_DOCS.md"

# 所有需要爬取的页面
PAGES = [
    # 🚀 快速开始
    {"section": "🚀 快速开始", "title": "入门指南", "path": "/start/getting-started.html"},
    {"section": "🚀 快速开始", "title": "安装向导", "path": "/start/wizard.html"},
    {"section": "🚀 快速开始", "title": "设置", "path": "/start/setup.html"},
    {"section": "🚀 快速开始", "title": "配对", "path": "/start/pairing.html"},
    {"section": "🚀 快速开始", "title": "Clawd 助手", "path": "/start/clawd.html"},
    
    # 💬 消息通道
    {"section": "💬 消息通道", "title": "WhatsApp", "path": "/channels/whatsapp.html"},
    {"section": "💬 消息通道", "title": "Telegram", "path": "/channels/telegram.html"},
    {"section": "💬 消息通道", "title": "Discord", "path": "/channels/discord.html"},
    {"section": "💬 消息通道", "title": "Slack", "path": "/channels/slack.html"},
    {"section": "💬 消息通道", "title": "飞书", "path": "/channels/feishu.html"},
    {"section": "💬 消息通道", "title": "iMessage", "path": "/channels/imessage.html"},
    {"section": "💬 消息通道", "title": "Signal", "path": "/channels/signal.html"},
    {"section": "💬 消息通道", "title": "Mattermost", "path": "/channels/mattermost.html"},
    
    # ⚙️ 网关与运维
    {"section": "⚙️ 网关与运维", "title": "网关服务操作手册", "path": "/gateway/"},
    {"section": "⚙️ 网关与运维", "title": "配置示例", "path": "/gateway/configuration-examples.html"},
    {"section": "⚙️ 网关与运维", "title": "安全", "path": "/gateway/security.html"},
    {"section": "⚙️ 网关与运维", "title": "SSL 证书部署", "path": "/guides/ssl-deployment.html"},
    {"section": "⚙️ 网关与运维", "title": "故障排除", "path": "/gateway/troubleshooting.html"},
    {"section": "⚙️ 网关与运维", "title": "Web UI 配对问题", "path": "/gateway/pairing-required-troubleshooting.html"},
    {"section": "⚙️ 网关与运维", "title": "令牌不匹配问题", "path": "/gateway/token-mismatch-troubleshooting.html"},
    {"section": "⚙️ 网关与运维", "title": "远程访问", "path": "/gateway/remote.html"},
    {"section": "⚙️ 网关与运维", "title": "Tailscale", "path": "/gateway/tailscale.html"},
    
    # 🔧 工具与技能
    {"section": "🔧 工具与技能", "title": "工具概述", "path": "/tools/"},
    {"section": "🔧 工具与技能", "title": "浏览器控制", "path": "/tools/browser.html"},
    {"section": "🔧 工具与技能", "title": "斜杠命令", "path": "/tools/slash-commands.html"},
    {"section": "🔧 工具与技能", "title": "技能", "path": "/tools/skills.html"},
    {"section": "🔧 工具与技能", "title": "技能配置", "path": "/tools/skills-config.html"},
    {"section": "🔧 工具与技能", "title": "ClawdHub", "path": "/tools/clawdhub.html"},
    
    # 🤖 模型提供商
    {"section": "🤖 模型提供商", "title": "自定义 AI 供应商", "path": "/guides/custom-ai-providers.html"},
    {"section": "🤖 模型提供商", "title": "OpenAI", "path": "/providers/openai.html"},
    {"section": "🤖 模型提供商", "title": "Anthropic", "path": "/providers/anthropic.html"},
    {"section": "🤖 模型提供商", "title": "MiniMax", "path": "/providers/minimax.html"},
    {"section": "🤖 模型提供商", "title": "Moonshot", "path": "/providers/moonshot.html"},
    {"section": "🤖 模型提供商", "title": "OpenRouter", "path": "/providers/openrouter.html"},
    
    # 📱 平台
    {"section": "📱 平台", "title": "macOS", "path": "/platforms/macos.html"},
    {"section": "📱 平台", "title": "iOS", "path": "/platforms/ios.html"},
    {"section": "📱 平台", "title": "Android", "path": "/platforms/android.html"},
    {"section": "📱 平台", "title": "Windows", "path": "/platforms/windows.html"},
    {"section": "📱 平台", "title": "Linux", "path": "/platforms/linux.html"},
    
    # ⏰ 自动化
    {"section": "⏰ 自动化", "title": "钩子", "path": "/hooks.html"},
    {"section": "⏰ 自动化", "title": "定时任务", "path": "/automation/cron-jobs.html"},
    {"section": "⏰ 自动化", "title": "Webhook", "path": "/automation/webhook.html"},
    {"section": "⏰ 自动化", "title": "Gmail 集成", "path": "/automation/gmail-pubsub.html"},
    
    # 📚 核心概念
    {"section": "📚 核心概念", "title": "架构", "path": "/concepts/architecture.html"},
    {"section": "📚 核心概念", "title": "智能体", "path": "/concepts/agent.html"},
    {"section": "📚 核心概念", "title": "会话", "path": "/concepts/session.html"},
    {"section": "📚 核心概念", "title": "多智能体", "path": "/concepts/multi-agent.html"},
    {"section": "📚 核心概念", "title": "记忆", "path": "/concepts/memory.html"},
    {"section": "📚 核心概念", "title": "模型", "path": "/concepts/models.html"},
    
    # 📦 安装
    {"section": "📦 安装", "title": "安装概述", "path": "/install/"},
    {"section": "📦 安装", "title": "安装脚本", "path": "/install/installer.html"},
    {"section": "📦 安装", "title": "更新", "path": "/install/updating.html"},
    {"section": "📦 安装", "title": "Docker 快速部署", "path": "/install/docker-quick.html"},
    {"section": "📦 安装", "title": "Docker 完整部署", "path": "/install/docker.html"},
    {"section": "📦 安装", "title": "Nix", "path": "/install/nix.html"},
    {"section": "📦 安装", "title": "Node.js", "path": "/install/node.html"},
    {"section": "📦 安装", "title": "Bun", "path": "/install/bun.html"},
    {"section": "📦 安装", "title": "开发渠道", "path": "/install/development-channels.html"},
    {"section": "📦 安装", "title": "Ansible", "path": "/install/ansible.html"},
    {"section": "📦 安装", "title": "卸载", "path": "/install/uninstall.html"},
    
    # 📖 参考
    {"section": "📖 参考", "title": "测试", "path": "/testing.html"},
    
    # 👥 社区
    {"section": "👥 社区", "title": "微信群", "path": "/community/wechat.html"},
]


class ContentExtractor(HTMLParser):
    """从 HTML 中提取主要内容"""
    
    def __init__(self):
        super().__init__()
        self.in_content = False
        self.in_code = False
        self.content = []
        self.current_tag = None
        self.tag_stack = []
        self.skip_tags = {'script', 'style', 'nav', 'aside', 'header', 'footer', 'button'}
        self.code_lang = ""
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        class_attr = attrs_dict.get('class') or ''
        if tag == 'div' and 'vp-doc' in class_attr:
            self.in_content = True
            
        if not self.in_content:
            return
            
        self.tag_stack.append(tag)
        self.current_tag = tag
        
        if tag == 'pre':
            self.in_code = True
            lang_match = re.search(r'language-(\w+)', class_attr)
            if lang_match:
                self.code_lang = lang_match.group(1)
            self.content.append(f"\n```{self.code_lang}\n")
        elif tag == 'code' and not self.in_code:
            self.content.append('`')
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.content.append(f"\n{'#' * level} ")
        elif tag == 'p':
            self.content.append('\n\n')
        elif tag == 'li':
            self.content.append('\n- ')
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            if href and not href.startswith('#'):
                self.content.append('[')
        elif tag == 'strong' or tag == 'b':
            self.content.append('**')
        elif tag == 'em' or tag == 'i':
            self.content.append('*')
        elif tag == 'br':
            self.content.append('\n')
        elif tag == 'blockquote':
            self.content.append('\n> ')
            
    def handle_endtag(self, tag):
        if not self.in_content:
            return
            
        if tag == 'div' and self.tag_stack and self.tag_stack[-1] == 'div':
            pass  # 可能是内容区域结束
            
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
            
        if tag == 'pre':
            self.in_code = False
            self.content.append('\n```\n')
            self.code_lang = ""
        elif tag == 'code' and not self.in_code:
            self.content.append('`')
        elif tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.content.append('\n')
        elif tag == 'a':
            self.content.append(']')
        elif tag == 'strong' or tag == 'b':
            self.content.append('**')
        elif tag == 'em' or tag == 'i':
            self.content.append('*')
            
    def handle_data(self, data):
        if not self.in_content:
            return
        if self.current_tag in self.skip_tags:
            return
        # 跳过一些噪音文本
        if data.strip() in ('​', 'Copy Code', '页面导航', '回到顶部', '菜单'):
            return
        self.content.append(data)
        
    def get_markdown(self):
        text = ''.join(self.content)
        # 清理多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 清理开头空白
        text = text.strip()
        return text


def fetch_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Charset': 'utf-8',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        return resp.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def html_to_markdown(html_content):
    """将 HTML 转换为 Markdown"""
    extractor = ContentExtractor()
    extractor.feed(html_content)
    return extractor.get_markdown()


def update_plan_file(page_path, status):
    """更新爬虫计划文件"""
    content = PLAN_FILE.read_text(encoding='utf-8')
    
    # 替换状态标记
    old_pattern = rf'\[ \] \[.*?\]\({re.escape(page_path)}\)'
    new_mark = '[x]' if status == 'done' else '[!]'
    
    # 找到对应的行并替换
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if page_path in line and '[ ]' in line:
            lines[i] = line.replace('[ ]', new_mark, 1)
            break
    
    # 更新统计
    done_count = sum(1 for l in lines if '[x]' in l)
    fail_count = sum(1 for l in lines if '[!]' in l)
    pending_count = sum(1 for l in lines if '[ ]' in l and '](' in l)
    
    # 更新统计部分
    for i, line in enumerate(lines):
        if line.startswith('- **已完成**:'):
            lines[i] = f'- **已完成**: {done_count}'
        elif line.startswith('- **待处理**:'):
            lines[i] = f'- **待处理**: {pending_count}'
        elif line.startswith('- **失败**:'):
            lines[i] = f'- **失败**: {fail_count}'
    
    PLAN_FILE.write_text('\n'.join(lines), encoding='utf-8')


def append_log(page_title, page_path, status):
    """添加爬虫日志"""
    content = PLAN_FILE.read_text(encoding='utf-8')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    status_emoji = '✅' if status == 'done' else '❌'
    
    log_line = f"| {timestamp} | {page_title} | {status_emoji} |"
    
    # 在日志表格末尾添加
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.strip() == '| - | - | - |':
            lines[i] = log_line
            break
    else:
        # 没找到占位符，在表格末尾添加
        for i, line in enumerate(lines):
            if '## 爬虫日志' in line:
                # 找到表格结束位置
                for j in range(i+4, len(lines)):
                    if not lines[j].startswith('|'):
                        lines.insert(j, log_line)
                        break
                break
    
    PLAN_FILE.write_text('\n'.join(lines), encoding='utf-8')


def crawl_single_page(page_info):
    """爬取单个页面"""
    url = BASE_URL + page_info['path']
    print(f"Crawling: {page_info['title']} ({url})")
    
    html = fetch_page(url)
    if not html:
        update_plan_file(page_info['path'], 'fail')
        append_log(page_info['title'], page_info['path'], 'fail')
        return None
    
    markdown = html_to_markdown(html)
    
    # 更新计划文件
    update_plan_file(page_info['path'], 'done')
    append_log(page_info['title'], page_info['path'], 'done')
    
    return {
        'section': page_info['section'],
        'title': page_info['title'],
        'path': page_info['path'],
        'content': markdown
    }


def build_all_docs_file(results):
    """构建完整的文档文件"""
    content = ["# OpenClaw 中文版完整文档\n"]
    content.append(f"> 爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    content.append("> 来源: https://clawd.org.cn\n\n")
    content.append("---\n\n")
    
    # 按分类组织
    current_section = None
    
    # 生成目录
    content.append("## 目录\n\n")
    for result in results:
        if result is None:
            continue
        if result['section'] != current_section:
            current_section = result['section']
            content.append(f"\n### {current_section}\n")
        anchor = result['title'].lower().replace(' ', '-').replace('.', '')
        content.append(f"- [{result['title']}](#{anchor})\n")
    
    content.append("\n---\n\n")
    
    # 添加内容
    current_section = None
    for result in results:
        if result is None:
            continue
        if result['section'] != current_section:
            current_section = result['section']
            content.append(f"\n# {current_section}\n\n")
            content.append("---\n\n")
        
        content.append(f"## {result['title']}\n\n")
        content.append(f"> 原文链接: {BASE_URL}{result['path']}\n\n")
        content.append(result['content'])
        content.append("\n\n---\n\n")
    
    ALL_DOCS_FILE.write_text(''.join(content), encoding='utf-8')


def main():
    """主函数"""
    print("=" * 50)
    print("OpenClaw 中文版文档爬虫")
    print("=" * 50)
    
    results = []
    total = len(PAGES)
    
    for i, page in enumerate(PAGES, 1):
        print(f"\n[{i}/{total}] ", end="")
        result = crawl_single_page(page)
        results.append(result)
        
        # 礼貌延迟
        if i < total:
            time.sleep(0.5)
    
    # 构建完整文档
    print("\n" + "=" * 50)
    print("正在生成完整文档...")
    build_all_docs_file(results)
    
    # 统计
    success = sum(1 for r in results if r is not None)
    failed = sum(1 for r in results if r is None)
    
    print(f"\n完成!")
    print(f"成功: {success}")
    print(f"失败: {failed}")
    print(f"\n输出文件:")
    print(f"  - {PLAN_FILE}")
    print(f"  - {ALL_DOCS_FILE}")


if __name__ == '__main__':
    main()
