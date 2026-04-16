# governance/ - L5 治理层

## 定位

L5 层是**控制平面**，负责策略执行、预算管理、风险控制、降级处理。

## 职责

1. **策略引擎** - 策略定义、评估、执行
2. **预算管理** - 资源预算、使用追踪、超限处理
3. **风险管理** - 风险评估、缓解措施
4. **降级管理** - 降级模式、熔断开关
5. **权限管理** - 权限检查、访问控制
6. **评估闭环** - 指标聚合、回归检测、推广推荐

## 目录结构

```
governance/
├── control_plane/       # 控制平面
│   └── policy_engine.py
├── budget/              # 预算管理
│   └── budget_manager.py
├── risk/                # 风险管理
│   └── risk_manager.py
├── permissions/         # 权限管理
├── degradation/         # 降级管理
│   └── degradation_manager.py
├── exceptions/          # 例外管理
├── release/             # 发布管理
├── evaluation/          # 评估闭环
│   └── evaluation_aggregator.py
└── README.md
```

## 核心接口

### 策略引擎

```python
from governance.control_plane.policy_engine import PolicyEngine, Policy, PolicyType

engine = PolicyEngine()

policy = Policy(
    policy_id="deny_high_risk",
    name="Deny High Risk",
    policy_type=PolicyType.RISK,
    effect=PolicyEffect.DENY,
    conditions=[{"field": "risk_level", "operator": "eq", "value": "high"}]
)

engine.register(policy)

# 评估
effect, applied = engine.evaluate(PolicyType.RISK, {"risk_level": "high"})
```

### 预算管理

```python
from governance.budget.budget_manager import BudgetManager, ResourceType, BudgetPeriod

manager = BudgetManager()

# 创建预算
manager.create_budget(
    budget_id="daily_tokens",
    resource_type=ResourceType.TOKENS,
    period=BudgetPeriod.DAILY,
    limit=100000
)

# 使用预算
allowed, remaining = manager.use_budget("daily_tokens", 1000, source="task_123")
```

### 风险管理

```python
from governance.risk.risk_manager import RiskManager

risk_mgr = RiskManager()

# 评估风险
assessment = risk_mgr.assess("file_delete", {"path": "/important/file.txt"})

print(assessment.level)  # LOW, MEDIUM, HIGH, CRITICAL
print(assessment.requires_approval)  # True/False
```

### 降级管理

```python
from governance.degradation.degradation_manager import DegradationManager, DegradationTrigger

degr = DegradationManager()

# 触发降级
degr.degrade(
    trigger=DegradationTrigger.BUDGET_EXCEEDED,
    disable_features=["expensive_skill"],
    fallback_modes={"search": "local_only"}
)

# 激活熔断开关
switch_id = degr.activate_kill_switch("problematic_skill", reason="Causing errors")

# 恢复
degr.recover(reason="Budget restored")
```

### 评估闭环

```python
from governance.evaluation.evaluation_aggregator import EvaluationAggregator, MetricType

aggregator = EvaluationAggregator()

# 记录指标
aggregator.record(Metric(
    metric_type=MetricType.TASK_SUCCESS_RATE,
    name="skill_x_success",
    value=0.95,
    unit="ratio"
))

# 获取回归告警
alerts = aggregator.get_alerts(severity="high")

# 获取趋势
trend = aggregator.get_aggregated(MetricType.SKILL_LATENCY, "skill_x", period="day")
```

## 纵向能力带

控制平面带贯穿：
- governance (本层)
- execution (执行控制)
- reports (报告输出)

评估与进化带贯穿：
- tests (测试)
- reports (报告)
- governance (本层)

## 扩展方式

1. 新增策略类型 → 在 `control_plane/` 添加 policy
2. 新增预算类型 → 在 `budget/` 添加 resource type
3. 新增风险评估 → 在 `risk/` 添加 assessor
