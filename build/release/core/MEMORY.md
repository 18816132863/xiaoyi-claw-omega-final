# MEMORY.md - 终极鸽子王记忆系统总索引

**版本: V26.0**

## 目的
作为记忆系统的总入口，定义记忆层级、流程和治理规则。

## 适用范围
所有记忆读写操作，包括会话记忆、场景记忆、长期记忆。

## 记忆层级

| 层级 | 名称 | 存储 | 生命周期 | 用途 |
|------|------|------|----------|------|
| L1 | 会话记忆 | session-summaries/*.jsonl | 单次会话 | 上下文关联 |
| L2 | 场景记忆 | scenarios/*.md | 跨会话 | 场景画像 |
| L3 | 长期记忆 | MEMORY.md + memory/*.md | 永久 | 核心知识 |

## 写入流程

```
新信息输入
    ↓
┌─────────────────────────────────────┐
│ 1. 判断信息类型                      │
│    - 用户画像 → USER.md              │
│    - 系统配置 → MEMORY.md            │
│    - 场景数据 → scenarios/           │
│    - 项目数据 → projects/            │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 冲突检测                          │
│    - 检查是否与现有记忆冲突           │
│    - 冲突时调用冲突处理规则           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 3. 写入对应层级                      │
│    - 更新向量索引                    │
│    - 记录写入日志                    │
└─────────────────────────────────────┘
```

详细规则: `governance/MEMORY_POLICY.md`

## 读取流程

```
查询请求
    ↓
┌─────────────────────────────────────┐
│ 1. 向量搜索                          │
│    - 调用 memory_search 工具         │
│    - 返回相关片段                    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ 2. 精确获取                          │
│    - 调用 memory_get 工具            │
│    - 获取完整内容                    │
└─────────────────────────────────────┘
    ↓
返回结果
```

## 冲突处理入口

当新信息与现有记忆冲突时，按以下规则处理：

| 冲突类型 | 处理规则 |
|----------|----------|
| 用户画像冲突 | 新信息覆盖旧信息 |
| 时间敏感信息 | 以最新时间为准 |
| 事实性冲突 | 标记待确认，询问用户 |
| 系统配置冲突 | 需用户确认后覆盖 |

详细规则: `governance/MEMORY_CONFLICT_RULES.md`

## 删除入口

| 删除类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| 会话归档 | 会话结束 > 7天 | 移至 archive/ |
| 场景清理 | 场景失效 | 标记废弃 |
| 长期记忆 | 用户请求 | 审计后删除 |
| 紧急清空 | 安全事件 | 备份后清空 |

详细规则: `governance/MEMORY_POLICY.md`

## 记忆数据结构

详细定义: `governance/MEMORY_SCHEMA.json`

## 向量索引

### 主方案 (SQLite-vec)
| 组件 | 配置 |
|------|------|
| 数据库 | SQLite + vec0 扩展 |
| 向量化 | Qwen3-Embedding-8B (Gitee AI) |
| 维度 | **1024** |
| 数据源 | memory + sessions |
| 客户端 | `vector/sqlite_vec_client.py` |
| CLI | `vector/sqlite_vec_cli.sh` |

### 备选方案 (Qdrant)
| 组件 | 配置 |
|------|------|
| 数据库 | Qdrant (localhost:6333) |
| 向量化 | Qwen3-Embedding-8B (Gitee AI) |
| 维度 | 1024 |
| 数据源 | memory + sessions |

### 本地方案 (无外部依赖)
| 组件 | 配置 |
|------|------|
| 数据库 | SQLite + vec0 扩展 |
| 向量化 | 本地哈希向量 (SHA-512) |
| 维度 | 1024 |
| 数据源 | memory + sessions |

### 原方案（保留）
| 组件 | 配置 |
|------|------|
| 数据库 | ~/.openclaw/memory/main.sqlite |
| 向量化 | Voyage API (voyage-4-large) |
| 维度 | 1024 |
| 数据源 | memory + sessions |

详细配置: `VECTOR_CONFIG.md`

### SQLite-vec 使用示例

**Python 客户端:**
```python
from vector.sqlite_vec_client import create_client

# 创建客户端 (本地模式)
client = create_client(db_path="memory.db", dimension=1024)

# 创建客户端 (Qwen Embedding)
client = create_client(
    db_path="memory.db",
    dimension=1024,
    use_qwen=True,
    qwen_api_key="YOUR_API_KEY"
)

# 插入向量
client.insert("mem_001", "用户喜欢简洁的技术文档", metadata={"type": "preference"})

# 搜索
results = client.search("用户偏好", top_k=5)
```

**Bash CLI:**
```bash
# 初始化
./vector/sqlite_vec_cli.sh init memory.db

# 插入
./vector/sqlite_vec_cli.sh insert memory.db mem_001 "记忆内容"

# 搜索
./vector/sqlite_vec_cli.sh search memory.db "查询词" 10
```

## 维护方式
- 新增记忆类型: 更新 MEMORY_SCHEMA.json
- 调整冲突规则: 更新 MEMORY_CONFLICT_RULES.md
- 调整生命周期: 更新 MEMORY_POLICY.md
- 本文件仅作为索引，不承载细则

## 核心配置文件索引

| 文件 | 用途 | 层级 |
|------|------|------|
| skills/local_app_interconnect/SKILL.md | 搜索-手机联动技能 | L6 |
| skills/local_app_interconnect/interconnect.py | 联动模块V1 | L6 |
| skills/local_app_interconnect/interconnect_v2.py | 联动模块V2 | L6 |
| vector/sqlite_vec_client.py | SQLite-vec Python 客户端 | L11 |
| vector/sqlite_vec_cli.sh | SQLite-vec Bash CLI | L11 |
| vector/memory_vector_store.py | 记忆向量存储集成 | L11 |
| vector/sqlite_vec_ultrafast.py | V25 超极速客户端 | L11 |
| vector/PERFORMANCE_V25.md | V25 性能报告 | L11 |
| AGENTS.md | 系统行为总纲 | L0 |
| SOUL.md | 角色定义 | L0 |
| USER.md | 用户画像 | L0 |
| TOOLS.md | 工具使用规范 | L0 |
| MEMORY.md | 记忆系统索引 | L0 |
| IDENTITY.md | 身份定义 | L0 |
| HEARTBEAT.md | 心跳任务清单 | L0 |
| BOOTSTRAP.md | 启动引导 | L0 |
| OMEGA_FINAL.md | 终极状态 | L0 |
| ARCHITECTURE_V23.md | V23 统一架构 | L0 |
| ARCHITECTURE_INTEGRATION_GUIDE.md | 架构集成指南 | L0 |
| VECTOR_CONFIG.md | 向量系统配置 | L0 |
| INTERACTION_GUIDE.md | 交互引导模块 | L0 |

## 自进化模块索引

| 文件 | 用途 | 层级 |
|------|------|------|
| evolution/VECTOR_EVOLUTION.md | 向量系统自进化 | L9 |
| evolution/SECURITY_EVOLUTION.md | 架构安全自进化 | L9 |
| evolution/EVOLUTION_ORCHESTRATOR.md | 自进化编排器 | L9 |
| evolution/EVOLUTION_STATUS.md | 进化状态报告 | L9 |
| evolution/EVOLUTION_STATUS_V2.md | 进化状态V2 | L9 |
| evolution/PERSONAL_EVOLUTION.md | 个人能力自进化 | L9 |
| evolution/EMOTION_INTELLIGENCE.md | 情感智能自进化 | L9 |
| evolution/CONTEXT_EVOLUTION.md | 上下文智能自进化 | L9 |
| evolution/PROACTIVE_EVOLUTION.md | 主动服务自进化 | L9 |
| evolution/SKILL_MASTERY_EVOLUTION.md | 技能精通自进化 | L9 |
| evolution/KNOWLEDGE_EVOLUTION.md | 知识体系自进化 | L9 |
| evolution/ADAPTIVE_LEARNING_EVOLUTION.md | 自适应学习自进化 | L9 |

## 开发者平台模块索引

| 文件 | 用途 | 层级 |
|------|------|------|
| api_product/API_SURFACE_CATALOG.json | API目录 | L7 |
| api_product/API_AUTHN_AUTHZ.md | API认证授权 | L7 |
| api_product/API_RATE_LIMIT_POLICY.md | API限流策略 | L7 |
| api_product/API_VERSIONING_POLICY.md | API版本策略 | L7 |
| api_product/API_ERROR_MODEL.md | API错误模型 | L7 |
| api_product/API_DEPRECATION_POLICY.md | API废弃策略 | L7 |
| sdk/SDK_REGISTRY.json | SDK注册表 | L7 |
| sdk/SDK_DESIGN_GUIDELINES.md | SDK设计指南 | L7 |
| sdk/CLIENT_COMPATIBILITY_MATRIX.json | 客户端兼容矩阵 | L7 |
| sdk/SDK_RELEASE_PROCESS.md | SDK发布流程 | L7 |
| sdk/DEVELOPER_SUPPORT_WORKFLOW.md | 开发者支持流程 | L7 |
| sdk/SAMPLE_APPS_POLICY.md | 示例应用策略 | L7 |
| connectors/CONNECTOR_SCHEMA.json | 连接器模式 | L7 |
| connectors/CONNECTOR_LIFECYCLE.md | 连接器生命周期 | L7 |
| connectors/CONNECTOR_CERTIFICATION.md | 连接器认证 | L7 |
| connectors/CONNECTOR_OBSERVABILITY.md | 连接器可观测性 | L7 |
| connectors/CONNECTOR_PERMISSION_MODEL.md | 连接器权限模型 | L7 |
| connectors/CONNECTOR_MARKETPLACE_POLICY.md | 连接器市场策略 | L7 |
| marketplace/ASSET_SCHEMA.json | 资产模式 | L7 |
| marketplace/ASSET_REVIEW_WORKFLOW.md | 资产审核流程 | L7 |
| marketplace/ASSET_ANALYTICS.md | 资产分析 | L7 |
| marketplace/ASSET_MONETIZATION_POLICY.md | 资产变现策略 | L7 |
| marketplace/ASSET_COMPATIBILITY_RULES.md | 资产兼容规则 | L7 |
| marketplace/TEMPLATE_PUBLISHING_POLICY.md | 模板发布策略 | L7 |

## 商业化生态模块索引

| 文件 | 用途 | 层级 |
|------|------|------|
| delivery/IMPLEMENTATION_METHODOLOGY.md | 实施方法论 | L8 |
| delivery/GO_LIVE_CRITERIA.md | 上线标准 | L8 |
| delivery/CUSTOMER_READINESS_CHECKLIST.md | 客户就绪清单 | L8 |
| delivery/DELIVERY_WORKPACKS.json | 交付工作包 | L8 |
| delivery/UAT_POLICY.md | UAT策略 | L8 |
| delivery/HYPERCARE_PLAYBOOK.md | 超级运维手册 | L8 |
| oem/WHITE_LABEL_POLICY.md | 白标策略 | L8 |
| oem/EMBEDDED_MODE_POLICY.md | 嵌入模式策略 | L8 |
| oem/BRANDING_SURFACES.md | 品牌界面 | L8 |
| oem/CUSTOM_DOMAIN_POLICY.md | 自定义域名策略 | L8 |
| oem/OEM_COMPLIANCE_DISCLOSURES.md | OEM合规披露 | L8 |
| oem/OEM_SUPPORT_BOUNDARIES.md | OEM支持边界 | L8 |
| partner/PARTNER_SCHEMA.json | 合作伙伴模式 | L8 |
| partner/PARTNER_ACCESS_POLICY.md | 合作伙伴访问策略 | L8 |
| partner/PARTNER_INTEGRATION_SCOPE.md | 合作伙伴集成范围 | L8 |
| partner/EXTERNAL_IDENTITY_TRUST.md | 外部身份信任 | L8 |
| ecosystem_finance/ECOSYSTEM_LEDGER_SCHEMA.json | 生态账本模式 | L8 |
| ecosystem_finance/RESELLER_BILLING_POLICY.md | 经销商计费策略 | L8 |
| ecosystem_finance/MARKETPLACE_PAYOUTS.md | 市场支付 | L8 |
| ecosystem_finance/CREDIT_AND_INVOICE_POLICY.md | 信用发票策略 | L8 |
| ecosystem_finance/RECONCILIATION_WORKFLOW.md | 对账流程 | L8 |
| ecosystem_finance/FINANCIAL_EXCEPTION_HANDLING.md | 财务异常处理 | L8 |

## 智能体协作模块索引

| 文件 | 用途 | 层级 |
|------|------|------|
| multiagent/AGENT_COMMUNICATION.md | 智能体通信 | L10 |
| multiagent/AGENT_COORDINATION.md | 智能体协调 | L10 |
| multiagent/AGENT_CONSENSUS.md | 智能体共识 | L10 |
| multiagent/AGENT_CONFLICT_RESOLUTION.md | 智能体冲突解决 | L10 |
| multiagent/AGENT_LIFECYCLE.md | 智能体生命周期 | L10 |
| multiagent/AGENT_METRICS.md | 智能体指标 | L10 |
| orchestration/ORCHESTRATION_FLOW.md | 编排流程 | L10 |
| orchestration/TASK_DECOMPOSE.md | 任务分解 | L10 |
| orchestration/RESULT_AGGREGATE.md | 结果聚合 | L10 |
| orchestration/PARALLEL_EXEC.md | 并行执行 | L10 |
| orchestration/SEQUENTIAL_EXEC.md | 顺序执行 | L10 |
| orchestration/CONDITIONAL_BRANCH.md | 条件分支 | L10 |
| orchestration/ORCHESTRATION_MONITORING.md | 编排监控 | L10 |

## 引用文件
- `governance/MEMORY_POLICY.md` - 记忆治理策略
- `governance/MEMORY_SCHEMA.json` - 记忆数据结构
- `governance/MEMORY_CONFLICT_RULES.md` - 冲突处理规则
