# 快速参考 V2.9.0

## 启动加载 (L1 only)

```
AGENTS.md → SOUL.md → USER.md → TOOLS.md → IDENTITY.md
Token: ~2000 | 延迟: ~30ms
```

## 层级触发

| 触发词 | 加载层级 |
|--------|----------|
| 记得、上次 | L2 |
| 工作流、定时 | L3 |
| 文档、word、pdf | L4-document |
| 数据、分析、excel | L4-data |
| 搜索、查找 | L4-search |
| 图片、照片 | L4-image |
| 代码、git | L4-code |
| 写作、文章 | L4-content |
| 小红书、b站 | L4-social |
| 市场、股票 | L4-business |
| 安全、权限 | L5 |
| 系统、安装 | L6 |

## 技能速查

### 高频技能
| 技能 | 用途 | 类别 |
|------|------|------|
| xiaoyi-web-search | 搜索 | search |
| xiaoyi-image-understanding | 看图 | image |
| docx | Word | document |
| data-analysis | 分析 | data |
| git | 代码 | code |
| article-writer | 写作 | content |

### 小艺专属
| 技能 | 用途 |
|------|------|
| xiaoyi-web-search | 网络搜索 |
| xiaoyi-image-understanding | 图片理解 |
| xiaoyi-image-search | 图片搜索 |
| xiaoyi-doc-convert | 文档转换 |
| xiaoyi-file-upload | 文件上传 |
| xiaoyi-health | 健康查询 |
| xiaoyi-report | 报告生成 |
| xiao-gui-agent | 手机操控 |

## 安全规则

```
✓ trash 代替 rm
✓ 安装前检查 skill-scope
✓ 敏感操作需确认
✗ 禁止禁用 execution-validator
```

## 性能指标

| 指标 | 目标 |
|------|------|
| 启动 | 30ms |
| Token | 2000 |
| 查找 | 5ms |
| 响应 | 60ms |

---

**版本**: V2.9.0
