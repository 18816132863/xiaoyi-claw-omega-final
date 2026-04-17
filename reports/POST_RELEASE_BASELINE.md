# POST RELEASE BASELINE - 发布后基线

## 正式版本号

**V7.2.0 Phase3 Final**

- Git Commit: `eaea10a`
- 注册时间: 2026-04-17T21:10:00+08:00
- 通道: `stable`

## 稳定通过的验收入口

| 验收项 | 状态 |
|--------|------|
| verify_phase3_final | ✅ passed |
| verify_phase1_baseline | ✅ passed |
| test_minimum_loop | ✅ passed |
| demo_minimum_loop | ✅ passed |
| unified_inspector (34/34) | ✅ passed |

## 不允许随便改动的核心文件

### 主链核心 (禁止直接修改)

| 目录 | 说明 |
|------|------|
| `governance/control_plane/` | 控制平面 - 决策核心 |
| `orchestration/workflow/` | 工作流引擎 - 执行核心 |
| `skills/runtime/` | 技能运行时 - 路由核心 |
| `skills/lifecycle/` | 技能生命周期 - 管理核心 |
| `memory_context/` | 记忆上下文 - 知识核心 |
| `core/events/` | 事件系统 - 观测核心 |
| `governance/release/` | 发布系统 - 通道核心 |

### 受保护文件 (修改需审批)

- `core/ARCHITECTURE.md`
- `core/RULE_REGISTRY.json`
- `core/LAYER_DEPENDENCY_RULES.json`
- `infrastructure/inventory/skill_registry.json`
- `MEMORY.md`

## 后续改动必须走的流程

### 1. 新真实任务接入

```
定义任务 → dev 验证 → staging 验证 → stable 晋升
```

必须留下：
- control decision
- workflow replay
- skill timeline
- policy timeline
- final result

### 2. 问题修补

```
发现问题 → 定位根因 → 设计修复 → dev 验证 → staging 验证 → stable 晋升
```

必须包含：
- 问题描述
- 影响范围
- 修复方案
- 验证结果

### 3. 小优化

```
基于 metrics → 发现优化点 → 设计方案 → dev 验证 → staging 验证
```

必须包含：
- 优化目标
- 预期收益
- 影响范围
- 验证方式

## 禁止事项

- ❌ 没有真实使用场景就大改架构
- ❌ 没有回放证据就重写主链
- ❌ 为了"更高级"去继续拆层、加层
- ❌ 直接修改 stable 通道的核心文件
- ❌ 绕过 control plane 执行任务
- ❌ 没有审计记录的变更

## 当前阶段原则

**不再大改架构，开始用真实任务养系统。**

---

_此文件由 POST RELEASE BASELINE 流程生成，修改需审批。_
