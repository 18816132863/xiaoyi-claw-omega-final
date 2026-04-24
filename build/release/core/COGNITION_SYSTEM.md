# 认知系统 - V1.0.0

## 概述

认知系统提供思考、推理、决策、规划和学习能力，是智能行为的核心。

## 模块组成

### 1. 推理引擎 (reasoning.py)

提供六种推理模式：

| 推理类型 | 说明 | 示例 |
|----------|------|------|
| 演绎推理 | 从一般到特殊 | 所有人都会死，苏格拉底是人，所以苏格拉底会死 |
| 归纳推理 | 从特殊到一般 | 观察多个实例，归纳出规律 |
| 溯因推理 | 从结果推断原因 | 观察现象，寻找最佳解释 |
| 类比推理 | 基于相似性推断 | A和B相似，A有X属性，B也可能有 |
| 因果推理 | 分析因果关系 | A导致B，因此A是B的原因 |
| 反事实推理 | 假设性思考 | 如果A没发生，结果会怎样 |

### 2. 决策系统 (decision.py)

提供三种决策方法：

| 方法 | 说明 | 适用场景 |
|------|------|----------|
| 加权求和 | 简单快速 | 单一目标决策 |
| AHP层次分析 | 考虑准则权重 | 多准则决策 |
| TOPSIS | 贴近理想解 | 复杂多属性决策 |

### 3. 规划引擎 (planning.py)

提供任务分解和执行监控：

- 目标分解：将大目标分解为子任务
- 依赖管理：自动识别任务依赖
- 进度跟踪：实时监控执行进度
- 动态重规划：根据情况调整计划

### 4. 反思系统 (reflection.py)

提供自我评估能力：

- 行动反思：评估动作是否正确
- 结果反思：分析成功/失败原因
- 过程反思：优化执行流程
- 策略反思：调整整体策略
- 学习反思：提取经验教训

### 5. 学习系统 (learning.py)

提供知识积累能力：

- 强化学习：从成功/失败中学习
- 监督学习：从明确反馈中学习
- 元学习：学习如何学习
- 知识迁移：跨领域应用知识

## 使用示例

### 推理
```python
from core.cognition import ReasoningEngine, ReasoningType, Premise

engine = ReasoningEngine()
premises = [
    Premise(content="所有技能都需要配置", confidence=0.9),
    Premise(content="pdf是一个技能", confidence=1.0)
]
result = engine.reason(premises, "pdf需要配置吗?", ReasoningType.DEDUCTIVE)
```

### 决策
```python
from core.cognition import DecisionMaker, Option, Criterion, DecisionCriteria

maker = DecisionMaker()
options = [
    Option(id="1", name="方案A", attributes={"cost": 100, "quality": 0.9}),
    Option(id="2", name="方案B", attributes={"cost": 50, "quality": 0.7})
]
criteria = [
    Criterion(name="cost", weight=0.3, criteria_type=DecisionCriteria.MINIMIZE),
    Criterion(name="quality", weight=0.7, criteria_type=DecisionCriteria.MAXIMIZE)
]
result = maker.decide(options, criteria)
```

### 规划
```python
from core.cognition import get_planning_engine

engine = get_planning_engine()
plan = engine.create_plan("完成项目开发")
ready_tasks = engine.get_ready_tasks(plan.id)
```

### 反思
```python
from core.cognition import get_reflection_system, ReflectionType

system = get_reflection_system()
reflection = system.reflect(
    context="用户请求帮助",
    action="调用技能",
    outcome="成功完成",
    reflection_type=ReflectionType.OUTCOME
)
```

### 学习
```python
from core.cognition import get_learning_system, Experience

system = get_learning_system()
experience = Experience(
    id="exp_1",
    situation="处理用户请求",
    action="使用技能A",
    outcome="成功",
    success=True,
    lessons=["技能A适合此类请求"]
)
result = system.learn(experience)
```

## 性能指标

| 指标 | 目标 |
|------|------|
| 推理准确率 | > 85% |
| 决策质量 | > 80% |
| 规划效率 | < 1s |
| 学习速度 | < 100ms |

## 集成方式

认知系统通过以下方式与其他模块集成：

1. **与执行层集成**：决策结果驱动技能调用
2. **与记忆层集成**：学习结果存入知识库
3. **与治理层集成**：反思结果触发规则更新
