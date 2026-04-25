---
name: news-search
description: 查询任意关键字相关的资讯新闻。适用于"有什么新闻"、"查一下XX资讯"等请求。
---

# 资讯查询

查询任意关键字相关的资讯新闻。

## 什么时候用

用户想查询以下内容时：
- 查看某主题的新闻资讯
- 查询热点事件相关资讯
- 获取市场动态、行情分析

## 怎么用

### 脚本调用

```bash
# 查询资讯（默认5条）
python3 scripts/query_news.py 黄金

# 查询资讯（指定条数）
python3 scripts/query_news.py 特朗普 10
python3 scripts/query_news.py A股 5
python3 scripts/query_news.py 股市 3
```

### 意图识别

| 用户说 | 使用脚本 |
|--------|----------|
| 有什么新闻/资讯 | 根据关键字调用 `query_news.py` |
| 查一下X资讯/新闻 | `query_news.py X` |
| X有什么消息 | `query_news.py X` |

## 怎么对用户输出（严格按照以下格式输出）

详细格式规范见 [references/news_output_format.md](./references/news_output_format.md)

Agent 输出时按该文档格式渲染。

## 失败处理

- 接口失败 → "服务异常，请稍后重试"
- 查不到数据 → "未找到关于「关键字」的相关资讯"
