# 模块索引 - V7.1.0

## L1 Core 核心层

### 认知系统 (core/cognition/)
| 模块 | 文件 | 功能 |
|------|------|------|
| 推理引擎 | reasoning.py | 6种推理模式 |
| 决策系统 | decision.py | 3种决策方法 |
| 规划引擎 | planning.py | 任务分解与执行 |
| 反思系统 | reflection.py | 自我评估与改进 |
| 学习系统 | learning.py | 知识积累与迁移 |

### 核心文档
| 文件 | 功能 |
|------|------|
| ARCHITECTURE.md | 架构定义 |
| RULE_REGISTRY.json | 规则注册表 |
| COGNITION_SYSTEM.md | 认知系统文档 |

## L2 Memory Context 记忆层

| 模块 | 功能 |
|------|------|
| VECTOR_CONFIG.md | 向量存储配置 |
| MEMORY_INTEGRATION.md | 记忆集成策略 |
| RETRIEVAL_STRATEGY.md | 检索策略 |
| INDEXING_POLICY.md | 索引策略 |

## L3 Orchestration 编排层

| 模块 | 文件 | 功能 |
|------|------|------|
| 任务引擎 | task_engine.py | 任务编排 |
| 工作流引擎 | workflow_engine.py | 工作流管理 |
| 优先级队列 | priority_queue.py | 任务优先级 |
| 技能路由器 | router/skill_router.py | 技能路由 |

## L4 Execution 执行层

| 模块 | 文件 | 功能 |
|------|------|------|
| 技能网关 | skill_gateway.py | 技能执行 |
| 技能适配 | skill_adapter_gateway.py | 技能适配 |
| 执行器池 | executor_pool.py | 并发执行 |
| 速率限制 | rate_limiter.py | 流量控制 |
| 循环防护 | loop_guard.py | 循环检测 |

## L5 Governance 治理层

### 安全模块
| 模块 | 文件 | 功能 |
|------|------|------|
| 安全检查 | security.py | 安全验证 |
| 权限管理 | permissions.py | 权限控制 |
| 审计日志 | audit.py | 操作审计 |
| 结果验证 | validator.py | 结果校验 |
| 合规检查 | compliance.py | 合规验证 |

### 恢复模块 (governance/recovery/)
| 模块 | 文件 | 功能 |
|------|------|------|
| 状态恢复 | state_recovery.py | 恢复点管理 |
| 故障恢复 | fault_recovery.py | 故障处理 |
| 回滚管理 | rollback_manager.py | 变更回滚 |

### 审查模块 (governance/review/)
| 模块 | 文件 | 功能 |
|------|------|------|
| 变更审查 | change_review.py | 风险评级 |
| 决策审查 | decision_review.py | 推理质量 |
| 合规审查 | compliance_review.py | 规则检查 |

### 规则模块 (governance/rules/)
| 模块 | 文件 | 功能 |
|------|------|------|
| 规则引擎 | rule_engine.py | 规则执行 |
| 规则监控 | rule_monitor.py | 执行统计 |
| 规则生命周期 | rule_lifecycle.py | 版本管理 |

## L6 Infrastructure 基础设施层

### 自动化模块 (infrastructure/automation/)
| 模块 | 文件 | 功能 |
|------|------|------|
| 任务自动化器 | task_automator.py | 队列管理 |
| 事件触发器 | event_trigger.py | 事件驱动 |
| 智能调度器 | smart_scheduler.py | 周期调度 |
| 流水线执行器 | pipeline_executor.py | 阶段管理 |

### 库存模块 (infrastructure/inventory/)
| 模块 | 功能 |
|------|------|
| skill_registry.json | 技能注册表 |
| skill_inverted_index.json | 倒排索引 |

### 优化模块 (infrastructure/optimization/)
| 模块 | 功能 |
|------|------|
| token_optimizer.py | Token优化 |
| 性能监控 | PERFORMANCE_MONITORING.md |

## 统计

| 层级 | 模块数 | 文件数 |
|------|--------|--------|
| L1 Core | 6 | 10+ |
| L2 Memory | 4 | 15+ |
| L3 Orchestration | 4 | 5+ |
| L4 Execution | 5 | 8+ |
| L5 Governance | 13 | 20+ |
| L6 Infrastructure | 10 | 30+ |
| **总计** | **42** | **88+** |
