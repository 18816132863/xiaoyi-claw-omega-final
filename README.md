# 小艺 Claw Omega Final

> 七层闭环 · 真实验证 · 证据驱动 · 禁止假成功

## 版本

**V7.0.0** - 2026-04-21 闭环收口版

## 核心特性

| 特性 | 说明 |
|------|------|
| 真实验证 | verify_executor 真实检查文件/数据库/消息证据 |
| 证据驱动 | 没有证据不能标 success |
| 禁止假成功 | result_guard 五重检查总闸 |
| 完整回复 | 固定模板：执行结果/完成项/未完成项/证据/下一步 |

## 运行模式

- **Runtime Mode**: `cloud_broker_mode`
- **Database**: PostgreSQL (Neon)
- **Broker**: Redis (Upstash)
- **Result Backend**: Redis (Upstash)

## 主链流程

```
parse
  ↓
distribute
  ↓
execute
  ↓
verify_executor.verify()      ← 真实验证
  ↓
summarize_executor.summarize() ← 真实总结
  ↓
result_guard.guard()          ← 最终总闸
  ↓
final_response
```

## 最终返回格式

```json
{
  "status": "success | failed",
  "reason": "",
  "user_response": "【执行结果】...",
  "completed_items": [],
  "failed_items": [],
  "evidence": {
    "files": [],
    "db_records": [],
    "messages": [],
    "tool_calls": [],
    "extra": {}
  },
  "next_action": "",
  "execution_trace": [],
  "task_id": "",
  "intent": "",
  "total_latency_ms": 0
}
```

## 禁止空成功

只有下面全部满足，才允许 success：

1. 至少一个真实 skill 执行成功
2. verify 成功
3. evidence 不为空
4. user_response 不为空
5. completed_items 不为空

## 六层架构

| 层级 | 名称 | 目录 | 职责 |
|------|------|------|------|
| L1 | Core | `core/` | 核心认知、身份、规则、标准 |
| L2 | Memory Context | `memory_context/` | 记忆上下文、知识库、统一搜索 |
| L3 | Orchestration | `orchestration/` | 任务编排、工作流、路由 |
| L4 | Execution | `execution/` | 能力执行、技能网关 |
| L5 | Governance | `governance/` | 稳定治理、安全审计 |
| L6 | Infrastructure | `infrastructure/` | 基础设施、工具链 |

## 数据库表

| 表名 | 说明 |
|------|------|
| `tasks` | 任务主表 |
| `task_runs` | 任务运行记录 |
| `task_steps` | 任务步骤表 |
| `task_events` | 任务事件表 |
| `tool_calls` | 工具调用表 |
| `workflow_checkpoints` | 工作流检查点表 |

## 快速启动

```bash
# 环境检查
python --version && node --version

# 依赖安装
pip install -r requirements.txt

# 启动服务
openclaw gateway start

# 健康检查
openclaw gateway status

# 测试
python tests/test_no_fake_success.py
python tests/test_end_to_end.py
```

## 核心文件

| 文件 | 说明 |
|------|------|
| `orchestration/task_engine.py` | 任务引擎 V7.0.0 |
| `orchestration/verify_executor.py` | 真实验证器 |
| `orchestration/summarize_executor.py` | 真实总结器 |
| `orchestration/result_guard.py` | 结果守卫 |
| `application/response_service/` | 响应服务 |
| `memory_context/memory_write_policy.py` | 记忆写入策略 |
| `memory_context/memory_retrieval_policy.py` | 记忆检索策略 |

## 技能生态

- 总技能数: 275
- 可路由: 273
- 可测试: 80

## 许可证

MIT
