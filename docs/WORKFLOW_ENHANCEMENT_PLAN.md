# 工作流增强计划

## 一、工作流引擎增强

### 1.1 条件分支

**文件**: `orchestration/workflows/branching.py`

**支持的条件**:
- `SUCCESS`: 上一步成功
- `FAILURE`: 上一步失败
- `TIMEOUT`: 上一步超时
- `UNCERTAIN`: 上一步结果不确定
- `CUSTOM`: 自定义条件

**使用示例**:
```python
from orchestration.workflows.branching import execute_branching_workflow, Branch, BranchCondition

steps = [{"name": "send_msg", "capability": "send_message", "params": {...}}]

branches = [
    Branch(
        condition=BranchCondition.SUCCESS,
        steps=[{"name": "notify", "capability": "send_notification", "params": {...}}]
    ),
    Branch(
        condition=BranchCondition.FAILURE,
        steps=[{"name": "retry", "capability": "resend_message", "params": {...}}]
    )
]

result = execute_branching_workflow(steps, branches)
```

---

### 1.2 并行步骤

**文件**: `orchestration/workflows/parallel_steps.py`

**支持的特性**:
- 并行执行多个步骤
- 可配置最大并行数
- 支持 fail_fast 模式（任一步骤失败则终止其他）
- 支持 dry_run 预演

**使用示例**:
```python
from orchestration.workflows.parallel_steps import execute_parallel_steps

steps = [
    {"name": "msg1", "capability": "send_message", "params": {"to": "phone1", "message": "..."}},
    {"name": "msg2", "capability": "send_message", "params": {"to": "phone2", "message": "..."}}
]

result = execute_parallel_steps(steps, max_workers=5, fail_fast=True)
```

---

### 1.3 人工确认节点

**文件**: `orchestration/workflows/human_confirm.py`

**支持的特性**:
- 创建待确认节点
- 获取待确认列表
- 响应确认节点
- 自动更新 invocation 的 confirmed_status

**使用示例**:
```python
from orchestration.workflows.human_confirm import create_human_confirm_node, respond_to_confirm

# 创建确认节点
node = create_human_confirm_node(
    invocation_id=123,
    reason="消息发送结果不确定，需要人工确认"
)

# 响应确认
result = respond_to_confirm(
    confirm_id=node["confirm_id"],
    response="confirmed_success"
)
```

---

### 1.4 补偿动作

**文件**: `orchestration/workflows/compensation.py`

**支持的特性**:
- 注册补偿动作
- 主流程失败时自动执行补偿
- 逆序执行补偿
- 支持回滚日程、消息、备忘录

**使用示例**:
```python
from orchestration.workflows.compensation import execute_with_compensation

primary_steps = [
    {"name": "create_event", "capability": "schedule_task", "params": {...}},
    {"name": "send_msg", "capability": "send_message", "params": {...}}
]

compensation_steps = [
    {"name": "delete_event", "capability": "delete_calendar_event", "params": {"event_id": "..."}}
]

result = execute_with_compensation(primary_steps, compensation_steps)
```

---

### 1.5 预览模式

**文件**: `orchestration/workflows/preview.py`

**支持的特性**:
- 预览工作流执行效果
- dry_run 干运行（不产生实际副作用）
- 比较预览和实际执行结果

**使用示例**:
```python
from orchestration.workflows.preview import preview_workflow, dry_run_workflow

steps = [...]

# 预览
preview = preview_workflow(steps)

# 干运行
dry_result = dry_run_workflow(steps)
```

---

## 二、场景模板

### 2.1 提醒联动模板

**文件**: `orchestration/templates/reminder_bundle.py`

**功能**: 创建日程 + 生成备忘录 + 推送通知 + 可选短信

**使用示例**:
```python
from orchestration.templates.reminder_bundle import reminder_bundle

result = reminder_bundle(
    title="会议提醒",
    start_time="2026-04-25T10:00:00",
    end_time="2026-04-25T11:00:00",
    location="会议室A",
    send_sms=True,
    sms_recipient="13800138000"
)
```

---

### 2.2 批量通知模板

**文件**: `orchestration/templates/batch_notify_bundle.py`

**功能**: 批量发送 + 失败汇总 + uncertain汇总 + 执行报告

**使用示例**:
```python
from orchestration.templates.batch_notify_bundle import batch_notify_bundle

result = batch_notify_bundle(
    notifications=[
        {"title": "通知1", "content": "内容1"},
        {"title": "通知2", "content": "内容2"}
    ],
    max_batch_size=20,
    require_approval=True
)
```

---

### 2.3 人工确认闭环模板

**文件**: `orchestration/templates/manual_confirmation_bundle.py`

**功能**: 查询待确认 -> 用户确认 -> 写入状态 -> 输出结果

**使用示例**:
```python
from orchestration.templates.manual_confirmation_bundle import manual_confirmation_bundle

result = manual_confirmation_bundle(check_uncertain=True)
```

---

### 2.4 日报模板

**文件**: `orchestration/templates/daily_report_bundle.py`

**功能**: 拉取数据 -> 统计 -> 输出日报 -> 可选推送

**使用示例**:
```python
from orchestration.templates.daily_report_bundle import daily_report_bundle

result = daily_report_bundle(date="2026-04-24", push_result=True)
```

---

### 2.5 故障补偿模板

**文件**: `orchestration/templates/failure_compensation_bundle.py`

**功能**: 主路径失败 -> fallback -> 审计补偿 -> 输出最终状态

**使用示例**:
```python
from orchestration.templates.failure_compensation_bundle import failure_compensation_bundle

result = failure_compensation_bundle(
    primary_action={"capability": "send_message", "params": {...}},
    fallback_actions=[{"capability": "send_notification", "params": {...}}],
    compensation_actions=[{"capability": "log_failure", "params": {...}}]
)
```

---

## 三、统计

| 类别 | 数量 |
|------|------|
| 工作流增强模块 | 5 |
| 场景模板 | 5 |
| **总模块数** | **10** |
