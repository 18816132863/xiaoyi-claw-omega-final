# 执行语义状态表

## 版本
- V8.3.0 路径统一版 + 平台能力真接线
- 更新日期: 2026-04-24

## 一、任务状态 (TaskStatus)

| 状态 | 值 | 语义层级 | 用户可见 | 可转换到 |
|------|-----|----------|----------|----------|
| DRAFT | draft | - | 草稿 | validated |
| VALIDATED | validated | accepted | 已校验 | persisted |
| PERSISTED | persisted | accepted | 已保存 | queued |
| QUEUED | queued | accepted | 已排队 | running |
| RUNNING | running | - | 执行中 | delivery_pending, succeeded, failed |
| DELIVERY_PENDING | delivery_pending | queued_for_delivery | 已提交，等待确认 | delivery_confirmed, failed |
| WAITING_RETRY | waiting_retry | - | 重试中 | running, failed |
| WAITING_HUMAN | waiting_human | - | 等待确认 | running, cancelled |
| PAUSED | paused | - | 已暂停 | resumed |
| RESUMED | resumed | - | 已恢复 | running |
| SUCCEEDED | succeeded | completed | ✅ 完成 | - |
| FAILED | failed | - | ❌ 失败 | - |
| CANCELLED | cancelled | - | 已取消 | - |

## 二、步骤状态 (StepStatus)

| 状态 | 值 | 语义层级 | 说明 |
|------|-----|----------|------|
| PENDING | pending | accepted | 待执行 |
| RUNNING | running | - | 执行中 |
| SUCCEEDED | succeeded | completed | 成功完成 |
| FAILED | failed | - | 失败 |
| SKIPPED | skipped | - | 已跳过 |

## 三、事件类型 (EventType)

| 事件 | 值 | 语义层级 | 触发时机 |
|------|-----|----------|----------|
| CREATED | created | - | 任务创建 |
| VALIDATED | validated | accepted | 校验通过 |
| PERSISTED | persisted | accepted | 持久化完成 |
| QUEUED | queued | accepted | 入队完成 |
| STARTED | started | - | 开始执行 |
| STEP_STARTED | step_started | - | 步骤开始 |
| STEP_COMPLETED | step_completed | completed | 步骤完成 |
| STEP_FAILED | step_failed | - | 步骤失败 |
| RETRYING | retrying | - | 开始重试 |
| WAITING_HUMAN | waiting_human | - | 等待人工 |
| RESUMED | resumed | - | 已恢复 |
| PAUSED | paused | - | 已暂停 |
| CANCELLED | cancelled | - | 已取消 |
| SUCCEEDED | succeeded | completed | 任务成功 |
| FAILED | failed | - | 任务失败 |
| DELIVERY_PENDING | delivery_pending | queued_for_delivery | 等待送达确认 |
| DELIVERY_CONFIRMED | delivery_confirmed | completed | 送达已确认 |

## 四、消息发送状态 (MessageSendResult)

| 状态 | 值 | 语义层级 | 用户可见 |
|------|-----|----------|----------|
| SUCCESS | success | completed | ✅ 已送达 |
| QUEUED | queued_for_delivery | queued | ⏳ 已提交，等待处理 |
| FAILED | failed | - | ❌ 发送失败 |

## 五、状态流转图

### 任务状态流转

```
draft
  │
  ▼
validated ─────────────────────────────────────────┐
  │                                                │
  ▼                                                │
persisted                                          │
  │                                                │
  ▼                                                │
queued                                             │
  │                                                │
  ▼                                                │
running ───────────────────────────────────────────┤
  │                                                │
  ├─────────────────┬─────────────────┐            │
  │                 │                 │            │
  ▼                 ▼                 ▼            │
delivery_pending   succeeded        failed         │
  │                 │                 │            │
  ▼                 │                 │            │
delivery_confirmed │                 │            │
  │                 │                 │            │
  └─────────────────┴─────────────────┴────────────┘
                    │
                    ▼
              (终态)
```

### 步骤状态流转

```
pending
  │
  ▼
running ───────────────────────────────────────────┐
  │                                                │
  ├─────────────────┬─────────────────┐            │
  │                 │                 │            │
  ▼                 ▼                 ▼            │
succeeded         failed           skipped         │
  │                 │                 │            │
  └─────────────────┴─────────────────┴────────────┘
                    │
                    ▼
              (终态)
```

## 六、语义层级对照表

| 语义层级 | TaskStatus | EventType | MessageSendResult |
|----------|------------|-----------|-------------------|
| accepted | validated, persisted, queued | validated, persisted, queued | - |
| queued_for_delivery | delivery_pending | delivery_pending | queued_for_delivery |
| completed | succeeded | delivery_confirmed, succeeded | success |
| - | running, failed, etc. | started, failed, etc. | failed |

## 七、关键区分

### ❌ 错误理解

| 错误 | 正确 |
|------|------|
| `delivery_pending` = "已完成" | `delivery_pending` = "已提交，等待确认" |
| `queued_for_delivery` = "成功" | `queued_for_delivery` = "已入队，等待处理" |
| "消息已发送" (实际只是入队) | "消息已提交，等待网关处理" |

### ✅ 正确理解

| 状态 | 含义 | 用户消息 |
|------|------|----------|
| `queued` | 已排队 | "任务已排队" |
| `running` | 执行中 | "正在执行..." |
| `delivery_pending` | 等待确认 | "已提交，等待送达确认" |
| `delivery_confirmed` | 已确认 | "已完成" |
| `succeeded` | 成功 | "✅ 成功完成" |

## 八、平台能力与状态映射

| 平台状态 | 执行结果 | 最终状态 | 确认级别 |
|----------|----------|----------|----------|
| connected | success | succeeded | Level 1/2 |
| connected | queued | delivery_pending → delivery_confirmed | Level 1/2 |
| probe_only | queued | delivery_pending (无确认) | Level 3 |
| fallback | queued | delivery_pending (无确认) | Level 3 |

## 九、测试覆盖

| 测试 | 文件 |
|------|------|
| 状态语义 | test_platform_execution_semantics.py |
| 状态流转 | test_delivery_confirmation_semantics.py |
| 消息状态 | test_platform_execution_semantics.py |
