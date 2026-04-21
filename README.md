# 小艺 Claw Omega Final

> 六层架构 · 任务系统 · 持久化 · 可恢复

## 版本

**V8.0.0** - 2026-04-21

## 运行模式

- **Runtime Mode**: `cloud_broker_mode`
- **Database**: PostgreSQL (Neon)
- **Broker**: Redis (Upstash)
- **Result Backend**: Redis (Upstash)

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

# 冒烟测试
python tests/test_architecture.py
```

## 核心文件

| 文件 | 说明 |
|------|------|
| `package_info.json` | 包信息 |
| `DEPLOY.md` | 部署指南 |
| `core/ARCHITECTURE.md` | 架构定义 |
| `AGENTS.md` | 工作空间规则 |
| `MEMORY.md` | 长期记忆 |

## 技能生态

- 总技能数: 275
- 可路由: 273
- 可测试: 80

## 许可证

MIT
