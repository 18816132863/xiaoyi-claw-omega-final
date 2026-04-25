# 双包机制说明

## 📦 版本对比

| 特性 | src/ 版本 | dist/ 版本 |
|------|-----------|------------|
| **SQLite 扩展加载** | ✅ 可选启用 | ❌ 不包含 |
| **subprocess 调用** | ✅ 可选启用 | ❌ 不包含 |
| **向量搜索** | ✅ 高性能 | ✅ 纯 Python |
| **文本搜索** | ✅ FTS5 | ✅ FTS5 |
| **安全标记** | ⚠️ 可能 Suspicious | ✅ 应该安全 |

---

## 📁 目录结构

```
llm-memory-integration/
├── src/                      # 完整功能版本
│   ├── core/                 # 核心模块
│   ├── optional/             # 可选模块（高风险功能）
│   │   ├── sqlite_extension.py   # SQLite 扩展加载
│   │   └── subprocess_utils.py   # subprocess 工具
│   └── scripts/              # 脚本
├── dist/                     # 安全版本
│   ├── core/                 # 核心模块（无高风险功能）
│   │   └── search_safe.py    # 安全搜索
│   └── SKILL.md              # dist 版本说明
└── config/
    └── optional_features.json # 可选功能配置
```

---

## 🔒 安全特性

### src/ 版本

- ⚠️ 包含高风险功能（默认禁用）
- ✅ 所有高风险功能需要用户明确启用
- ✅ 提供完整功能
- ⚠️ 可能被标记为 Suspicious

### dist/ 版本

- ✅ 不包含任何高风险功能
- ✅ 无 SQLite 扩展加载
- ✅ 无 subprocess 调用
- ✅ 纯 Python 实现
- ✅ 应该无 Suspicious 标记

---

## 🚀 使用方法

### 安装

```bash
# 安装 src 版本（完整功能）
clawhub install llm-memory-integration

# 安装 dist 版本（安全版本）
clawhub install llm-memory-integration --dist
```

### 启用可选功能（仅 src 版本）

```bash
# 启用 SQLite 扩展加载
export ENABLE_SQLITE_EXTENSION=true

# 启用 subprocess 调用
export ENABLE_SUBPROCESS=true
```

---

## ⚠️ 性能说明

| 操作 | src/ 版本 | dist/ 版本 |
|------|-----------|------------|
| **文本搜索** | 快（FTS5） | 快（FTS5） |
| **向量搜索** | 快（SQLite 扩展） | 慢（纯 Python） |

**性能差异**：
- 文本搜索：无差异
- 向量搜索：dist 版本慢 10-100 倍

---

## 🎯 适用场景

### 推荐使用 dist 版本

- ✅ 安全要求高的环境
- ✅ 不需要高性能向量搜索
- ✅ 只需要文本搜索功能
- ✅ 不想看到 Suspicious 标记

### 推荐使用 src 版本

- ✅ 需要高性能向量搜索
- ✅ 可以审查高风险代码
- ✅ 需要完整功能
- ✅ 可以接受 Suspicious 标记

---

## 📝 配置文件

### config/optional_features.json

```json
{
  "features": {
    "sqlite_extension": {
      "enabled": false,
      "risk": "high",
      "description": "SQLite 扩展加载（vec0.so）",
      "enable_method": "设置环境变量 ENABLE_SQLITE_EXTENSION=true"
    },
    "subprocess_utils": {
      "enabled": false,
      "risk": "medium",
      "description": "subprocess 调用（读取系统信息）",
      "enable_method": "设置环境变量 ENABLE_SUBPROCESS=true"
    }
  }
}
```

---

**版本**: v6.3.6  
**更新时间**: 2026-04-15
