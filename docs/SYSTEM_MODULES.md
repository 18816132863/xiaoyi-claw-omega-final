# 系统模块清单 V1.0.0

> 自动生成于 2026-04-17

---

## 一、核心引擎 (5个)

| 名称 | 路径 | 功能 | 使用频率 |
|------|------|------|----------|
| **融合引擎** | `infrastructure/fusion_engine.py` | 文件自动归档、压缩包清理 | 心跳自动 |
| **文档同步引擎** | `infrastructure/doc_sync_engine.py` | 代码变更→文档自动同步 | 心跳自动 |
| **自动触发器** | `scripts/auto_trigger.py` | 检测场景→自动触发任务 | 心跳自动 |
| **自动备份上传器** | `infrastructure/auto_backup_uploader.py` | Git自动提交推送 | 心跳自动 |
| **心跳执行器** | `scripts/heartbeat_executor.py` | 统一执行定时任务 | 每30分钟 |

---

## 二、检查脚本 (10个)

| 名称 | 命令 | 功能 |
|------|------|------|
| **统一巡检器** | `make inspect` | 34项全面检查 |
| **层间依赖检查** | `python scripts/check_layer_dependencies.py` | 检查六层架构依赖 |
| **JSON契约检查** | `python scripts/check_json_contracts.py` | 检查JSON格式正确性 |
| **仓库完整性检查** | `python scripts/check_repo_integrity.py` | 检查文件完整性 |
| **技能安全检查** | `python scripts/check_skill_security.py` | 检查技能安全性 |
| **变更影响检查** | `python scripts/check_change_impact.py` | 分析变更影响范围 |
| **规则守卫检查** | `python scripts/check_rule_guards.py` | 检查规则执行 |
| **AI API检查** | `python scripts/check_ai_apis.py` | 检查AI接口可用性 |
| **深度巡检** | `python scripts/deep_inspection.py` | 深度架构检查 |
| **快速巡检** | `python scripts/unified_inspector_v7.py --quick` | 快速检查 |

---

## 三、日引导系统 (5个)

| 名称 | 命令 | 功能 | 触发时机 |
|------|------|------|----------|
| **日引导循环** | `make daily-growth-personal` | 早上启动、选任务、生成计划 | 每天早上 |
| **中午检查** | `make midday-check` | 检查进度、纠偏 | 每天中午 |
| **晚间复盘** | `make daily-review` | 总结、沉淀经验 | 每天晚上 |
| **每周复盘** | `make weekly-review` | 周总结、下周建议 | 每周一 |
| **引导检查** | `scripts/run_daily_growth_check.py` | 自动检查是否需要引导 | 心跳自动 |

---

## 四、治理模块 (L5)

| 模块 | 路径 | 功能 |
|------|------|------|
| **控制平面** | `governance/control_plane/` | 策略引擎、决策系统 |
| **滥用防护** | `governance/risk/skill_abuse_guard.py` | 防DDoS/内存泄漏/攻击 |
| **预算管理** | `governance/budget/` | Token/成本预算 |
| **审计系统** | `governance/audit/` | 操作审计日志 |
| **恢复系统** | `governance/recovery/` | 状态恢复、故障恢复 |
| **规则引擎** | `governance/rules/` | 规则执行、监控 |

---

## 五、自动化任务

### 心跳任务 (每30分钟)

```
1. auto_git        → 自动Git同步
2. auto_backup     → 自动备份上传
3. auto_trigger    → 自动触发器
4. permanent_keeper → 守护器刷新
```

### 自动触发场景

```
新增 .py 文件      → 技能安全检查
修改 core/ 文件    → 架构巡检
修改 governance/   → 规则检查
每日首次启动       → 日引导检查
每周首次启动       → 周复盘
```

---

## 六、简化方案

### 问题

- 模块太多 (299个Python文件)
- 名字难记
- 功能重叠

### 方案：三层入口

```
┌─────────────────────────────────────────┐
│  第一层：Makefile (日常使用)            │
│  make inspect        → 巡检             │
│  make daily-growth   → 日引导           │
│  make fusion-check   → 融合检查         │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│  第二层：心跳 (自动执行)                │
│  每30分钟自动运行                       │
│  - Git同步                             │
│  - 备份上传                            │
│  - 自动触发                            │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│  第三层：脚本 (高级用户)                │
│  python scripts/xxx.py                  │
│  需要时才手动调用                       │
└─────────────────────────────────────────┘
```

### 记忆口诀

```
日常用 Makefile：
  inspect (巡检)
  daily-growth (日引导)
  fusion-check (融合)

自动靠心跳：
  每30分钟自动跑
  不用管

高级用脚本：
  需要时再查
```

---

## 七、核心命令速查

| 场景 | 命令 |
|------|------|
| **巡检系统** | `make inspect` |
| **开始一天** | `make daily-growth-personal` |
| **中午检查** | `make midday-check` |
| **晚上复盘** | `make daily-review` |
| **周总结** | `make weekly-review` |
| **融合检查** | `make fusion-check` |
| **文档同步** | `make fusion-sync` |
| **门禁验证** | `make verify-premerge` |

---

_记住这8个命令就够了，其他都是自动的。_
