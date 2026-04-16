# 自动运行组件清单 V7.2.0

> 架构中所有需要自动运行的组件及其状态

---

## 一、自动运行组件清单

| 组件 | 文件 | 触发条件 | 当前状态 | 优先级 |
|------|------|----------|----------|--------|
| 融合引擎 | `infrastructure/fusion_engine.py` | git commit 前 | ✅ 已自动 | P0 |
| 自动 Git 同步 | `infrastructure/auto_git.py` | 心跳 (30分钟) | ❌ 未自动 | P0 |
| 永久守护器 | `scripts/permanent_keeper.py` | 心跳 | ❌ 未自动 | P0 |
| 智能调度器 | `infrastructure/automation/smart_scheduler.py` | 后台服务 | ❌ 未自动 | P1 |
| 自动优化器 | `infrastructure/optimization/auto_optimizer.py` | 性能下降时 | ❌ 未自动 | P1 |
| 架构巡检器 | `scripts/unified_inspector_v7.py` | 心跳 / CI | ⚠️ 手动 | P0 |
| 规则引擎 | `scripts/run_rule_engine.py` | pre-merge | ⚠️ 手动 | P0 |
| 技能分类器 | `scripts/auto_classify_skills.py` | 新增技能时 | ⚠️ 手动 | P1 |
| Metrics 生成器 | `scripts/generate_metrics.py` | 心跳 / CI | ⚠️ 手动 | P1 |
| 事件触发器 | `infrastructure/automation/event_trigger.py` | 事件发生时 | ❌ 未自动 | P1 |
| 任务自动化器 | `infrastructure/automation/task_automator.py` | 任务队列 | ❌ 未自动 | P1 |
| 流水线执行器 | `infrastructure/automation/pipeline_executor.py` | 流水线触发 | ❌ 未自动 | P1 |

---

## 二、需要自动运行的场景

### 2.1 Git 提交时 (pre-commit)

| 组件 | 动作 |
|------|------|
| 融合引擎 | 检查新文件是否融入架构 |
| 规则引擎 | 检查规则合规性 |
| 架构巡检 | 快速巡检 |

### 2.2 心跳时 (每30分钟)

| 组件 | 动作 |
|------|------|
| 自动 Git 同步 | 提交并推送变更 |
| 永久守护器 | 刷新关键模块状态 |
| Metrics 生成器 | 生成最新指标 |
| 架构巡检器 | 完整巡检 |

### 2.3 CI/CD 时 (pre-merge / release)

| 组件 | 动作 |
|------|------|
| 规则引擎 | 完整规则检查 |
| 架构巡检器 | 完整巡检 |
| 技能安全检查 | 扫描所有技能 |
| 变更影响分析 | 分析变更影响 |

### 2.4 事件触发时

| 事件 | 触发组件 |
|------|----------|
| 新增技能 | 技能分类器 |
| 性能下降 | 自动优化器 |
| 任务入队 | 任务自动化器 |
| 流水线触发 | 流水线执行器 |

---

## 三、自动运行机制

### 3.1 Git Hooks

```
.git/hooks/
├── pre-commit      # 提交前检查
├── pre-push        # 推送前检查
└── post-merge      # 合并后处理
```

### 3.2 心跳机制

```
HEARTBEAT.md 定义心跳任务
    ↓
每 30 分钟触发
    ↓
执行心跳任务列表
```

### 3.3 CI/CD 集成

```
.github/workflows/
├── pre-merge.yml   # 合并前检查
├── nightly.yml     # 每日巡检
└── release.yml     # 发布检查
```

---

## 四、待实现的自动运行

### 4.1 心跳自动运行

```python
# 心跳任务列表
HEARTBEAT_TASKS = [
    "infrastructure/auto_git.py sync",
    "scripts/permanent_keeper.py --refresh",
    "scripts/generate_metrics.py",
    "scripts/unified_inspector_v7.py --quick"
]
```

### 4.2 事件自动触发

```python
# 事件触发配置
EVENT_TRIGGERS = {
    "skill_added": ["scripts/auto_classify_skills.py"],
    "performance_drop": ["infrastructure/optimization/auto_optimizer.py"],
    "task_queued": ["infrastructure/automation/task_automator.py"]
}
```

### 4.3 后台服务

```python
# 后台服务列表
BACKGROUND_SERVICES = [
    "infrastructure/automation/smart_scheduler.py",
    "infrastructure/automation/event_trigger.py"
]
```
