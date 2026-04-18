---
name: technical-seo-checker
description: 'Technical SEO audit: Core Web Vitals, crawl, indexing, mobile, speed, architecture, redirects. 技术SEO/网站速度'
version: "6.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when checking technical SEO health: site speed, Core Web Vitals, indexing, crawlability, robots.txt, sitemaps, or canonical tags."
argument-hint: "<URL or domain>"
allowed-tools: WebFetch
metadata:
  author: aaron-he-zhu
  version: "6.0.0"
  geo-relevance: "low"
  tags:
    - seo
    - technical-seo
    - core-web-vitals
    - page-speed
    - crawlability
    - indexability
    - mobile-seo
    - site-health
    - lcp
    - cls
    - inp
    - robots-txt
    - xml-sitemap
    - 技术SEO
    - 网站速度
    - テクニカルSEO
    - 기술SEO
    - seo-tecnico
  triggers:
    # EN-formal
    - "technical SEO audit"
    - "check page speed"
    - "Core Web Vitals"
    - "crawl issues"
    - "site indexing problems"
    - "canonical tag issues"
    - "duplicate content"
    - "mobile-friendly check"
    - "site speed"
    - "site health check"
    # EN-casual
    - "my site is slow"
    - "Google can't crawl my site"
    - "Google can't find my pages"
    - "mobile issues"
    - "indexing problems"
    - "why is my site slow"
    # EN-question
    - "how do I fix my page speed"
    - "why is my site not indexed"
    - "how to improve Core Web Vitals"
    - "why did my site disappear from Google"
    # EN-competitor
    - "PageSpeed Insights alternative"
    - "GTmetrix alternative"
    - "Sitebulb alternative"
    # ZH-pro
    - "技术SEO检查"
    - "网站速度优化"
    - "核心网页指标"
    - "爬虫问题"
    - "索引问题"
    - "网站收录"
    - "sitemap提交"
    - "robots设置"
    # ZH-casual
    - "网站加载太慢"
    - "网站太慢了"
    - "Google找不到我的页面"
    - "手机端有问题"
    - "收录不了"
    - "Google收录少"
    # JA
    - "テクニカルSEO"
    - "サイト速度"
    - "コアウェブバイタル"
    - "クロール問題"
    - "インデックス登録"
    - "モバイル最適化"
    # KO
    - "기술 SEO"
    - "사이트 속도"
    - "코어 웹 바이탈"
    - "크롤링 문제"
    - "사이트 왜 이렇게 느려?"
    # ES
    - "auditoría SEO técnica"
    - "velocidad del sitio"
    - "problemas de indexación"
    - "mi sitio no aparece en Google"
    - "velocidad de carga"
    # PT
    - "auditoria SEO técnica"
    - "meu site não aparece no Google"
    - "velocidade de carregamento"

## 详细文档

请参阅 [references/details.md](references/details.md)


## 使用方法

### 命令行调用

```bash
# 查看帮助
python skill.py help

# 执行技能
python skill.py run --template default

# 列出模板
python skill.py list
```

## 示例

```bash
python skill.py run --template default
```
