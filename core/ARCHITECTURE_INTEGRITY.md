# 架构完整性检查 V1.0.0

## 概述

本文档定义 OpenClaw 架构的完整性检查规则，确保六层架构的稳定性和一致性。

## 六层架构

```
L1: Core              → 核心认知、身份、规则
L2: Memory Context    → 记忆上下文、知识库
L3: Orchestration     → 任务编排、工作流
L4: Execution         → 能力执行、技能网关
L5: Governance        → 稳定治理、安全审计
L6: Infrastructure    → 基础设施、工具链
```

## 门禁体系

### Profile 定义

| Profile | P0 | Local | Integration | External | 用途 |
|---------|-----|-------|-------------|----------|------|
| premerge | =0 | 必须 | 不阻塞 | 不阻塞 | PR 合并前 |
| nightly | =0 | 必须 | 必须 | 不阻塞 | 每日巡检 |
| release | =0 | 必须 | 必须 | 无 error | 发布前 |

### 回归规则

**强回归（阻塞发布）：**
- P0 数量上升
- local 从 pass 变 fail/error
- integration 默认样本从 pass 变 fail/error
- quality_gate 任一 pass → fail

**弱回归（警告）：**
- P1/P2 数量上升
- external skipped 原因变化
- skill 总数异常波动

## 验收入口

```bash
# CI 统一入口
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py nightly
python scripts/run_release_gate.py release

# 夜间巡检（带回归检测）
python scripts/run_nightly_audit.py
```

## 报告体系

```
reports/
├── runtime_integrity.json      # 最新运行时报告
├── quality_gate.json           # 最新质量报告
├── nightly_audit.json          # 夜间审计报告
├── nightly_summary.md          # 夜间摘要
├── trends/
│   └── runtime_trend.json      # 趋势数据
└── history/
    ├── runtime/                # 运行时历史快照
    ├── quality/                # 质量历史快照
    └── release/                # 发布历史
```

## 受保护文件

见 `governance/guard/protected_files.json`

核心原则：
- `core/` 目录为唯一主架构真源
- 根目录的 AGENTS.md/SOUL.md 等为兼容副本
- 禁止删除或移动受保护文件

## 路径解析

统一使用 `infrastructure/path_resolver.py`：
- 基于模块位置解析项目根
- 不依赖当前工作目录
- 支持从任意目录执行

## 技能分层

| 层级 | 条件 | 阻塞 |
|------|------|------|
| local | smoke_test=true, test_mode=local | 是 |
| integration | registered+routable+callable, test_mode=integration | nightly 必须 |
| external | test_mode=external, requires_env | 仅检测 error |

## 更新记录

- 2026-04-12: V1.0.0 初始版本
