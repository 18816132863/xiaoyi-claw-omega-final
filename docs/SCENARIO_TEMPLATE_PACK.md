# 场景模板包

## 一、模板列表

### 1. 提醒联动模板 (reminder_bundle)

**用途**: 一键创建完整提醒链

**包含动作**:
1. 创建日程事件
2. 生成备忘录
3. 推送通知
4. 可选短信提醒

**输入参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 是 | 日程标题 |
| start_time | string | 是 | 开始时间 |
| end_time | string | 否 | 结束时间 |
| location | string | 否 | 地点 |
| note_content | string | 否 | 备忘录内容 |
| send_sms | boolean | 否 | 是否发送短信 |
| sms_recipient | string | 否 | 短信接收人 |
| send_notification | boolean | 否 | 是否推送通知 |
| dry_run | boolean | 否 | 预演模式 |

**输出**:
- created_event_id: 创建的日程ID
- created_note_id: 创建的备忘录ID
- summary: 执行摘要

---

### 2. 批量通知模板 (batch_notify_bundle)

**用途**: 批量发送通知并汇总结果

**包含动作**:
1. 并行发送多条通知
2. 汇总成功/失败/uncertain
3. 生成执行报告

**输入参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| notifications | array | 是 | 通知列表 |
| max_batch_size | integer | 否 | 最大批次大小（默认20） |
| require_approval | boolean | 否 | 是否需要审批 |
| dry_run | boolean | 否 | 预演模式 |

**输出**:
- total: 总数
- success_count: 成功数
- failed_count: 失败数
- uncertain_count: 不确定数
- success_list / failed_list / uncertain_list: 详细列表

---

### 3. 人工确认闭环模板 (manual_confirmation_bundle)

**用途**: 处理 uncertain 记录的人工确认流程

**包含动作**:
1. 查询 uncertain 记录
2. 获取待确认节点
3. 等待用户确认
4. 写入 confirmed_status

**输入参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| check_uncertain | boolean | 否 | 是否检查 uncertain 记录 |
| auto_confirm_timeout | boolean | 否 | 是否自动确认超时 |
| dry_run | boolean | 否 | 预演模式 |

**输出**:
- uncertain_records: uncertain 记录列表
- pending_confirms: 待确认节点列表
- next_steps: 下一步操作建议

---

### 4. 日报模板 (daily_report_bundle)

**用途**: 自动生成每日运营报告

**包含动作**:
1. 拉取 platform_invocations 数据
2. 统计失败率/超时率/确认率
3. 输出日报
4. 可选推送结果

**输入参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期（默认今天） |
| push_result | boolean | 否 | 是否推送结果 |
| dry_run | boolean | 否 | 预演模式 |

**输出**:
- date: 日期
- summary: 统计摘要
- report: 完整报告

---

### 5. 故障补偿模板 (failure_compensation_bundle)

**用途**: 主路径失败时的自动补偿流程

**包含动作**:
1. 执行主要动作
2. 失败时执行 fallback
3. fallback 失败时执行补偿
4. 发送故障通知

**输入参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| primary_action | object | 是 | 主要动作 |
| fallback_actions | array | 是 | 降级动作列表 |
| compensation_actions | array | 是 | 补偿动作列表 |
| notify_on_failure | boolean | 否 | 失败时是否通知 |
| dry_run | boolean | 否 | 预演模式 |

**输出**:
- final_status: 最终状态
- execution_log: 执行日志
- used_fallback: 是否使用了 fallback
- used_compensation: 是否执行了补偿

---

## 二、模板特性

| 特性 | 说明 |
|------|------|
| dry_run | 所有模板支持预演模式 |
| preview | 可预览执行效果 |
| audit | 所有动作记录审计日志 |
| summary | 输出执行摘要 |

---

## 三、使用方式

```python
# 方式1: 直接导入
from orchestration.templates.reminder_bundle import reminder_bundle
result = reminder_bundle(...)

# 方式2: 通过 run 入口
from orchestration.templates.reminder_bundle import run
result = run(**kwargs)
```
