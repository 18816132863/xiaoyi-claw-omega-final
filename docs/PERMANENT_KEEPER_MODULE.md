# 永久在线守护模块 V1.0.0

## 概述

本模块确保关键组件永久在线，不会因新对话、记忆丢失、时间流逝而失效。

---

## 核心功能

1. **状态检查** - 检查守护对象是否完整
2. **自动刷新** - 定期刷新保持活跃
3. **缺失恢复** - 检测并恢复缺失文件
4. **新对话恢复** - 新会话自动恢复关键状态

---

## 守护对象

### Critical 级别（必须在线）

| ID | 名称 | 类型 | 文件数 | 说明 |
|----|------|------|--------|------|
| fusion_engine | 融合引擎 | engine | 2 | 统一融合索引，保证技能路由 |
| memory_engine | 记忆引擎 | engine | 4 | 长期记忆和向量索引 |
| rule_engine | 规则引擎 | engine | 3 | 规则注册和执行 |
| skill_registry | 技能注册表 | registry | 2 | 技能发现和路由 |
| core_identity | 核心身份 | identity | 5 | 身份和规则 |
| architecture | 架构文档 | docs | 4 | 架构定义 |

### High 级别（重要在线）

| ID | 名称 | 类型 | 文件数 | 说明 |
|----|------|------|--------|------|
| exception_manager | 例外管理器 | module | 3 | 例外操作和历史 |
| dependency_manager | 依赖管理器 | module | 3 | 依赖状态 |
| delete_manager | 删除管理器 | module | 3 | 删除确认和回收站 |

---

## 使用方式

### 初始化
```bash
python scripts/permanent_keeper.py init
```

### 检查状态
```bash
# 检查所有
python scripts/permanent_keeper.py check

# 检查单个
python scripts/permanent_keeper.py check --keeper fusion_engine
```

### 刷新
```bash
# 刷新所有
python scripts/permanent_keeper.py refresh

# 刷新单个
python scripts/permanent_keeper.py refresh --keeper fusion_engine
```

### 列出守护对象
```bash
python scripts/permanent_keeper.py list
```

### 添加守护对象
```bash
python scripts/permanent_keeper.py add \
    --id my_module \
    --name "我的模块" \
    --type module \
    --files "path/to/file1,path/to/file2" \
    --priority high \
    --description "模块说明"
```

### 移除守护对象
```bash
python scripts/permanent_keeper.py remove --id my_module
```

### 恢复缺失文件
```bash
python scripts/permanent_keeper.py restore
```

---

## 文件位置

| 文件 | 说明 |
|------|------|
| `scripts/permanent_keeper.py` | 守护模块脚本 |
| `infrastructure/config/permanent_keepers.json` | 守护配置 |
| `reports/ops/keeper_state.json` | 守护状态 |

---

## 刷新间隔

| 类型 | 默认间隔 |
|------|----------|
| engine | 1 小时 |
| module | 24 小时 |
| registry | 1 小时 |
| identity | 24 小时 |
| docs | 24 小时 |

---

## 新对话恢复流程

1. 新会话开始时，自动调用 `check`
2. 如果发现缺失文件，标记为需要恢复
3. 从备份或缓存恢复关键文件
4. 刷新所有 critical 级别守护对象

---

## 防止失效机制

1. **文件检查** - 每次检查确认文件存在
2. **定期刷新** - 按间隔刷新保持活跃
3. **状态记录** - 记录最后检查时间和刷新次数
4. **优先级保护** - critical 级别优先处理

---

## 版本

- V1.0.0 - 2026-04-15 - 初始版本
