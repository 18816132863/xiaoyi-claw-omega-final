---
name: keyword-research
description: 'Find high-value SEO keywords: search volume, difficulty, intent classification, topic clusters. 关键词研究/内容选题'
version: "6.0.0"
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem. No system packages required. Optional: MCP network access for SEO tool integrations."
homepage: "https://github.com/aaron-he-zhu/seo-geo-claude-skills"
when_to_use: "Use when starting keyword research for a new page, topic, or campaign. Also when the user asks about search volume, keyword difficulty, topic clusters, long-tail keywords, or what to write about."
argument-hint: "<topic or seed keyword> [market/language]"
metadata:
  author: aaron-he-zhu
  version: "6.0.0"
  geo-relevance: "medium"
  tags:
    - seo
    - geo
    - keywords
    - keyword-research
    - search-volume
    - keyword-difficulty
    - topic-clusters
    - long-tail-keywords
    - search-intent
    - content-calendar
    - ahrefs
    - semrush
    - google-keyword-planner
    - 关键词研究
    - SEO关键词
    - キーワード調査
    - 키워드분석
    - palabras-clave
  triggers:
    # EN-formal
    - "keyword research"
    - "find keywords"
    - "keyword analysis"
    - "keyword discovery"
    - "search volume analysis"
    - "keyword difficulty"
    - "topic research"
    - "identify ranking opportunities"
    # EN-casual
    - "what should I write about"
    - "what are people searching for"
    - "what are people googling"
    - "find me topics to write"
    - "give me keyword ideas"
    - "which keywords should I target"
    - "why is my traffic low"
    - "I need content ideas"
    # EN-question
    - "how do I find good keywords"
    - "what keywords should I target"
    - "how competitive is this keyword"
    # EN-competitor
    - "Ahrefs keyword explorer alternative"
    - "Semrush keyword magic tool"
    - "Google Keyword Planner alternative"
    - "Ubersuggest alternative"
    # ZH-pro
    - "关键词研究"
    - "关键词分析"
    - "搜索量查询"
    - "关键词难度"
    - "SEO关键词"
    - "长尾关键词"
    - "词库整理"
    - "关键词布局"
    - "关键词挖掘"
    # ZH-casual
    - "写什么内容好"
    - "找选题"
    - "帮我挖词"
    - "不知道写什么"
    - "查关键词"
    - "选词"
    - "帮我找词"
    # JA
    - "キーワード調査"
    - "キーワードリサーチ"
    - "SEOキーワード分析"
    - "検索ボリューム"
    - "ロングテールキーワード"
    - "検索意図分析"
    # KO
    - "키워드 리서치"
    - "키워드 분석"
    - "검색량 분석"
    - "키워드 어떻게 찾아요?"
    - "검색어 분석"
    - "경쟁도 낮은 키워드는?"
    # ES
    - "investigación de palabras clave"
    - "análisis de palabras clave"
    - "volumen de búsqueda"
    - "posicionamiento web"
    - "cómo encontrar palabras clave"
    # PT
    - "pesquisa de palavras-chave"

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
