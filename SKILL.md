# 终极鸽子王 V7.2.0

> 六层架构核心引擎，统一入口、三条主链、自动运行机制

---

## 简介

这是 V7.2.0 统一架构的完整版，包含六层架构核心代码、275+ 技能生态、自动运行机制。

### 核心特性

- **六层架构**: Core → Memory Context → Orchestration → Execution → Governance → Infrastructure
- **三条主链**: 生命周期主链、恢复链主链、Metrics反哺主链
- **统一入口**: 策略引擎.评估策略()、技能路由器.选择技能()、工作流引擎.运行工作流()
- **自动运行**: Git钩子、守护进程管理器、心跳执行器

---

## 六层架构

### 第一层：核心层 (Core)

```
core/
├── cognition/              # 认知系统
│   ├── reasoning.py        # 推理引擎（6种推理模式）
│   ├── decision.py         # 决策系统（3种决策方法）
│   ├── planning.py         # 规划引擎
│   ├── reflection.py       # 反思系统
│   └── learning.py         # 学习系统
├── events/                 # 事件系统
│   ├── event_bus.py        # 事件总线
│   └── event_types.py      # 事件类型
├── state/                  # 状态契约
│   ├── global_state_contract.py
│   ├── profile_state_contract.py
│   └── task_state_contract.py
└── query/                  # 查询处理
    ├── understand.py
    ├── rewriter.py
    └── langdetect.py
```

### 第二层：记忆上下文层 (Memory Context)

```
memory_context/
├── builder/                # 上下文构建
│   ├── context_builder.py
│   ├── priority_ranker.py
│   └── conflict_resolver.py
├── retrieval/              # 检索系统
│   ├── retrieval_router.py
│   ├── hybrid_search.py
│   └── reranker.py
├── session/                # 会话管理
│   ├── session_history.py
│   └── session_state.py
├── long_term/              # 长期记忆
│   └── project_memory_store.py
├── vector/                 # 向量存储（4096维）
│   ├── embedding_4096.py
│   ├── sqlite_vec_client.py
│   └── vector_qdrant.py
└── search/                 # 搜索系统
    ├── fast_search.py
    └── router.py
```

### 第三层：编排层 (Orchestration)

```
orchestration/
├── workflow/               # 工作流引擎
│   ├── workflow_engine.py
│   ├── dag_builder.py
│   └── dependency_resolver.py
├── execution_control/      # 执行控制
│   ├── fallback_policy.py  # 回退策略
│   ├── rollback_manager.py # 回滚管理器
│   └── retry_policy.py     # 重试策略
└── state/                  # 状态管理
    └── checkpoint_store.py
```

### 第四层：执行层 (Execution)

```
execution/
├── skill_router.py         # 技能路由器
├── skill_loader.py         # 技能加载器
├── skill_sandbox.py        # 技能沙箱
├── skill_audit.py          # 技能审计
└── skill_gateway.py        # 技能网关

skills/
├── registry/               # 技能注册表
│   └── skill_registry.py
├── runtime/                # 技能运行时
├── lifecycle/              # 生命周期管理
│   ├── install_manager.py
│   ├── enable_disable_manager.py
│   └── deprecation_manager.py
└── policies/               # 技能策略
    ├── skill_budget_policy.py
    ├── skill_risk_policy.py
    └── skill_permission_policy.py
```

### 第五层：治理层 (Governance)

```
governance/
├── control_plane/          # 控制平面
│   └── policy_engine.py    # 策略引擎（统一入口）
├── budget/                 # 预算管理
│   ├── token_budget_manager.py
│   └── cost_budget_manager.py
├── risk/                   # 风险管理
│   ├── risk_classifier.py
│   └── high_risk_guard.py
├── permissions/            # 权限管理
│   └── permission_engine.py
├── evaluation/             # 评估聚合
│   └── evaluation_aggregator.py
├── recovery/               # 恢复性模块
├── review/                 # 审查性模块
└── rules/                  # 规则管控
```

### 第六层：基础设施层 (Infrastructure)

```
infrastructure/
├── daemon_manager.py       # 守护进程管理器
├── auto_git.py             # 自动Git同步
├── fusion_engine.py        # 融合引擎
├── automation/             # 自动化模块
│   ├── task_automator.py
│   ├── event_trigger.py
│   ├── smart_scheduler.py
│   └── pipeline_executor.py
└── inventory/
    └── skill_registry.json
```

---

## 三条主链

### 1. 技能生命周期主链

```
InstallManager.install() → SkillRegistry.register() → SkillRouter.select_skill()
```

### 2. 工作流恢复链主链

```
WorkflowEngine.run_workflow() → FallbackPolicy.decide() → RollbackManager.rollback()
```

### 3. Metrics反哺主链

```
Benchmarks → EvaluationAggregator → PolicyEngine → SkillRouter
```

---

## 统一入口接口

### 策略引擎.评估策略()

```python
from governance.control_plane.policy_engine import PolicyEngine

engine = PolicyEngine()
decision = engine.evaluate_policy(profile="developer", intent="search")

# 返回
{
    "decision": "allow",
    "allowed": True,
    "risk_level": "low",
    "token_budget": 16000,
    "cost_budget": 50.0
}
```

### 技能路由器.选择技能()

```python
from skills.runtime.skill_router import SkillRouter

router = SkillRouter()
result = router.select_skill(intent="search", profile="developer")

# 返回
{
    "success": True,
    "skill_id": "search",
    "confidence": 0.9
}
```

### 工作流引擎.运行工作流()

```python
from orchestration.workflow.workflow_engine import WorkflowEngine

engine = WorkflowEngine()
result = engine.run_workflow(workflow_def)

# 返回
WorkflowResult(
    workflow_id="xxx",
    status="completed",
    step_results=[...]
)
```

---

## 自动运行机制

### Git 钩子

| 钩子 | 触发时机 | 功能 |
|------|----------|------|
| pre-commit | git commit前 | 融合检查 |
| pre-push | git push前 | 快速巡检 |

### 守护进程管理器

| 服务 | 间隔 | 功能 |
|------|------|------|
| 心跳执行器 | 30分钟 | 执行心跳任务 |
| 永久守护器 | 5分钟 | 刷新关键模块 |
| Metrics生成器 | 60分钟 | 生成指标报告 |
| 融合检查器 | 10分钟 | 检查架构融合 |

### 使用方式

```bash
# 启动守护进程
./scripts/daemon.sh start

# 停止守护进程
./scripts/daemon.sh stop

# 查看状态
./scripts/daemon.sh status
```

---

## 技能生态

| 分类 | 数量 |
|------|------|
| AI | 31 |
| 搜索 | 24 |
| 图像 | 17 |
| 文档 | 13 |
| 视频 | 10 |
| 金融 | 8 |
| 代码 | 8 |
| 电商 | 8 |
| 其他 | 156 |
| **总计** | **275+** |

---

## 验证命令

```bash
# 集成测试
python tests/integration/test_minimum_loop.py

# 统一巡检
python scripts/unified_inspector_v7.py

# Metrics生成
python scripts/generate_metrics.py

# 守护进程状态
python infrastructure/daemon_manager.py status
```

---

## 版本信息

- **版本**: V7.2.0
- **发布日期**: 2026-04-16
- **技能ID**: k977z2jr14tqanspkysfkk1bhh84hvqw
- **ClawHub**: xiaoyi-claw-omega-final
- **作者**: 18816132863
- **融合率**: 99.5%
