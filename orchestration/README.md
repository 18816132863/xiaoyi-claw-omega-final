# orchestration/ - L3 任务编排层

## 定位

L3 层是**工作流引擎**，负责任务分解、DAG 执行、状态管理。

## 职责

1. **任务规划** - 意图分析、任务分解、计划生成
2. **工作流引擎** - DAG 构建、并行执行、依赖管理
3. **状态机** - 状态转换、生命周期管理
4. **执行控制** - 重试、回退、检查点

## 目录结构

```
orchestration/
├── contracts/           # JSON Schema 契约
│   ├── workflow.schema.json
│   ├── task_node.schema.json
│   └── step_result.schema.json
├── planner/             # 任务规划
│   └── task_planner.py
├── workflow/            # 工作流引擎
│   ├── workflow_engine.py
│   ├── dag_builder.py
│   └── state_machine.py
├── execution_control/   # 执行控制
├── state/               # 状态管理
├── validators/          # 验证器
└── README.md
```

## 核心接口

### 任务规划

```python
from orchestration.planner.task_planner import TaskPlanner

planner = TaskPlanner()
plan = planner.plan(
    task_id="task_123",
    task_description="Build and deploy the application"
)

# 转换为工作流
workflow_spec = plan.to_workflow_spec()
```

### 工作流执行

```python
from orchestration.workflow.workflow_engine import run_workflow

result = run_workflow(
    workflow_spec={
        "workflow_id": "my_workflow",
        "steps": [
            {"step_id": "step1", "action": "prepare"},
            {"step_id": "step2", "action": "build", "depends_on": ["step1"]},
            {"step_id": "step3", "action": "deploy", "depends_on": ["step2"]}
        ]
    },
    profile="developer"
)

print(result.status)  # completed, failed, etc.
```

### DAG 构建

```python
from orchestration.workflow.dag_builder import DAGBuilder

builder = DAGBuilder()
dag = builder.build_from_steps([
    {"step_id": "a", "depends_on": []},
    {"step_id": "b", "depends_on": ["a"]},
    {"step_id": "c", "depends_on": ["a"]},
    {"step_id": "d", "depends_on": ["b", "c"]}
])

# 获取并行组
groups = dag.get_parallel_groups()  # [['a'], ['b', 'c'], ['d']]
```

## 契约

- `workflow.schema.json` - 工作流定义
- `task_node.schema.json` - 任务节点
- `step_result.schema.json` - 步骤结果

## 纵向能力带

工作流与执行带贯穿：
- orchestration (本层)
- execution (执行)
- infrastructure (基础设施)

## 扩展方式

1. 新增规划策略 → 在 `planner/` 添加 planner
2. 新增执行控制 → 在 `execution_control/` 添加 controller
3. 新增验证器 → 在 `validators/` 添加 validator
