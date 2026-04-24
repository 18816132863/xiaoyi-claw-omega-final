# 六层架构定义 V8.0.0

> **唯一主架构定义** - 本文档是项目唯一正式运行架构定义
> 
> 其他架构文档（ARCHITECTURE_V2.x.x.md、OMEGA_FINAL.md 等）均为历史兼容资料，位于 `docs/archives/`

---

## 六层主架构

| 层级 | 名称 | 职责 | 主目录 |
|------|------|------|--------|
| L1 | Core | 核心认知、身份、规则、标准 | `core/` |
| L2 | Memory Context | 记忆上下文、知识库、统一搜索、向量存储 | `memory_context/` |
| L3 | Orchestration | 任务编排、工作流、路由、策略 | `orchestration/` |
| L4 | Execution | 能力执行、技能网关、交付 | `execution/` |
| L5 | Governance | 稳定治理、安全审计、合规、计费 | `governance/` |
| L6 | Infrastructure | 基础设施、工具链、注册表、运维 | `infrastructure/` |

---

## 顶层目录与六层映射

### 主层目录（6个）

| 目录 | 所属层级 | 说明 |
|------|----------|------|
| `core/` | L1 | 核心层，包含认知、状态、事件、规则 |
| `memory_context/` | L2 | 记忆上下文层，包含检索、会话、构建 |
| `orchestration/` | L3 | 编排层，包含工作流、执行控制、状态管理 |
| `execution/` | L4 | 执行层，包含技能网关、适配器、循环防护 |
| `governance/` | L5 | 治理层，包含安全、权限、审计、预算、风控 |
| `infrastructure/` | L6 | 基础设施层，包含存储、调度、缓存、自动化 |

### 工程模块目录（非主层）

| 目录 | 归属主层 | 说明 |
|------|----------|------|
| `skills/` | L4 Execution | 技能包存放目录 |
| `domain/` | L4 Execution | 领域模型定义 |
| `application/` | L3 Orchestration | 应用服务层 |
| `tests/` | L6 Infrastructure | 测试套件 |
| `scripts/` | L6 Infrastructure | 运维脚本 |
| `reports/` | L6 Infrastructure | 报告输出 |
| `data/` | L6 Infrastructure | 数据存储 |
| `docs/` | L6 Infrastructure | 文档 |

### 根目录文件（L1 Core）

| 文件 | 说明 |
|------|------|
| `AGENTS.md` | 工作空间规则 |
| `SOUL.md` | 身份定义 |
| `USER.md` | 用户信息 |
| `TOOLS.md` | 工具规则 |
| `IDENTITY.md` | 身份标识 |
| `MEMORY.md` | 长期记忆 |
| `HEARTBEAT.md` | 心跳任务 |

---

## memory 与 memory_context 的关系

**重要说明**：本项目只有 **6 层架构**，不是 8 层。

| 目录 | 职责 | 是否主层 |
|------|------|----------|
| `memory/` | 会话数据存储（日记、对话历史） | ❌ 非主层，属于 L2 的数据存储 |
| `memory_context/` | 记忆上下文系统（检索、会话管理、上下文构建） | ✅ L2 主层 |

**区别**：
- `memory/` 是**数据目录**，存放运行时产生的记忆数据
- `memory_context/` 是**架构层**，包含记忆系统的代码逻辑

**不要混淆**：`memory/` 不是第 7 层，`memory_context/` 才是 L2 主层

---

## L4 Execution 目录承载说明

**L4 Execution 层由以下目录共同承载**：

| 目录 | 说明 |
|------|------|
| `execution/` | **主目录**，包含技能网关、适配器、循环防护、任务质量等核心执行组件 |
| `skills/` | 技能包存放目录，由 `execution/skill_gateway.py` 加载和路由 |
| `domain/` | 领域模型定义，为执行层提供任务规格、状态枚举等 |
| `application/` | 应用服务层，协调执行层的任务服务 |

**核心执行组件**：

| 组件 | 路径 | 职责 |
|------|------|------|
| SkillGateway | `execution/skill_gateway.py` | 技能网关入口 |
| SkillRouter | `execution/skill_router.py` | 技能路由 |
| LoopGuard | `execution/loop_guard.py` | 循环防护 |
| TaskReviewer | `execution/task_reviewer.py` | 任务审查 |
| ResultValidator | `execution/result_validator.py` | 结果验证 |

---

## 技能生态

### 技能统计

| 指标 | 数量 |
|------|------|
| 总技能数 | 275 |
| 可路由 | 273 |
| 可测试 | 80 |
| 可调用 | 273 |

### 技能分类

| 分类 | 数量 | 说明 |
|------|------|------|
| AI | 31 | LLM、Embedding、Agent |
| Search | 24 | 搜索、查询、抓取 |
| Image | 17 | 图像生成、处理 |
| Document | 13 | PDF、DOCX、PPTX |
| Video | 10 | 视频生成、处理 |
| Finance | 8 | 股票、加密货币 |
| Code | 8 | Git、Docker、Ansible |
| E-commerce | 8 | 电商、优惠券 |
| Data | 7 | 数据分析、数据库 |
| Memory | 7 | 记忆、知识库 |
| Audio | 5 | 语音、TTS |
| Automation | 5 | 自动化、定时任务 |
| Communication | 2 | 消息、邮件 |
| Utility | 1 | 工具类 |
| Other | 129 | 其他 |

### 核心技能

| 技能 | 版本 | 功能 |
|------|------|------|
| llm-memory-integration | 5.1.5 | LLM + 向量模型集成，4096维 Embedding |
| agent-chronicle | 1.0.0 | 日记生成，记忆集成 |
| find-skills | 1.0.0 | 技能发现 |
| memory-setup | 1.0.0 | 记忆系统配置 |

---

## 高级功能

### 向量存储

| 引擎 | 状态 | 维度 | 说明 |
|------|------|------|------|
| sqlite-vec | ✅ 启用 | 4096 | 主引擎，本地存储 |
| qdrant | ✅ 启用 | 4096 | 副引擎，高性能 |
| tfidf | ✅ 启用 | - | 备份引擎，关键词检索 |

### LLM 配置

| 提供商 | 模型 | 用途 |
|--------|------|------|
| Gitee AI | Qwen3-235B-A22B | LLM |
| Gitee AI | Qwen3-Embedding-8B | Embedding (4096维) |

### 审计系统

| 功能 | 状态 |
|------|------|
| 加密存储 | ✅ AES-256-GCM |
| 工具调用审计 | ✅ 启用 |
| 技能调用审计 | ✅ 启用 |
| 内存读写审计 | ✅ 启用 |

---

## 规则平台化体系

### 规则注册表

**路径**: `core/RULE_REGISTRY.json`

**版本**: V1.2.0

**规则列表**:

| 规则 ID | 名称 | 状态 | Owner |
|---------|------|------|-------|
| R001 | 层间依赖规则 | active | architecture |
| R002 | JSON 契约规则 | active | architecture |
| R003 | 唯一真源规则 | active | architecture |
| R004 | 变更影响规则 | active | governance |
| R005 | 规则自测规则 | active | governance |
| R006 | 仓库完整性规则 | active | infrastructure |
| R007 | 技能安全规则 | experimental | governance |
| R008 | 遗留格式规则 | disabled | infrastructure |

### 规则生命周期

**路径**: `core/RULE_LIFECYCLE_POLICY.md`

**状态定义**:
- `active`: 正式生效，失败阻断
- `experimental`: 实验阶段，失败不阻断
- `deprecated`: 已废弃，失败不阻断
- `disabled`: 已禁用，不执行

### 规则引擎

**路径**: `scripts/run_rule_engine.py`

**版本**: V3.0.0

**功能**:
- 按 profile 执行规则集
- 支持规则生命周期识别
- 支持规则例外识别
- 支持例外债务识别
- 生成规则执行报告

**命令**:
```bash
python scripts/run_rule_engine.py --profile premerge --save
```

---

## 规则例外治理体系

### 例外注册表

**路径**: `core/RULE_EXCEPTIONS.json`

**版本**: V2.0.0

**字段**:
- `exception_id`: 例外 ID
- `rule_id`: 关联规则 ID
- `owner`: 责任人
- `debt_level`: 债务等级 (low/medium/high)
- `max_renewals`: 最大续期次数
- `renewal_count`: 当前续期次数
- `escalation_after_days`: 升级阈值天数
- `ticket_ref`: 关联工单

### 例外债务策略

**路径**: `core/RULE_EXCEPTION_DEBT_POLICY.md`

**债务状态**:
- `healthy`: 健康，正常生效
- `stale`: 陈旧，即将过期或超过 escalation 阈值
- `overused`: 滥用，超过续期次数
- `expired`: 过期，不再生效

### 例外债务快照

**路径**: `reports/ops/rule_exception_debt.json`

**内容**:
- active_count / healthy_count / stale_count / overused_count / expired_count
- exceptions_by_owner / exceptions_by_rule
- high_debt_count

---

## 融合机制

### 融合策略

**路径**: `core/FUSION_POLICY.md`

**职责**: 定义文件融合到架构的规则和流程

### 融合引擎

**路径**: `infrastructure/fusion_engine.py`

**版本**: V2.0.0

**功能**:
- 判断文件是否应该融入架构
- 分类文件到目标目录
- 执行融合操作
- 生成融合报告
- 审查现有结构

**命令**:
```bash
# 审查现有结构
python infrastructure/fusion_engine.py --audit

# 扫描并显示融合建议
python infrastructure/fusion_engine.py --scan

# 实际执行融合
python infrastructure/fusion_engine.py --execute
```

---

## 性能优化体系

### 性能优化器

**路径**: `infrastructure/performance_optimizer.py`

**功能**:
- 规则引擎缓存
- 技能注册表缓存
- 记忆索引懒加载
- 并行检查支持

**命令**:
```bash
python infrastructure/performance_optimizer.py --benchmark
```

### 优化文档

- `docs/OPTIMIZATION_PLAN.md` - 优化方案
- `docs/OPTIMIZATION_CALCULATION.md` - 优化计算
- `docs/COMPRESSION_OPTIMIZATION.md` - 压缩优化策略

---

## 数据库系统

### 数据库文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 任务数据库 | `data/tasks.db` | SQLite 主数据库 |
| 向量数据库 | `data/vectors.db` | sqlite-vec 向量存储 |
| 审计数据库 | `data/audit.db` | 审计日志存储 |

### 迁移脚本

| 文件 | 路径 | 说明 |
|------|------|------|
| 任务系统迁移 | `infrastructure/storage/migrations/001_task_system.sql` | 创建任务相关表 |
| 向量索引迁移 | `infrastructure/storage/migrations/002_vector_index.sql` | 创建向量索引 |

### 初始化脚本

| 文件 | 路径 | 说明 |
|------|------|------|
| 数据库初始化 | `infrastructure/storage/init_db.py` | 初始化所有数据库 |
| 种子数据 | `infrastructure/storage/seed_data.py` | 插入初始数据 |

### 表结构说明

| 表名 | 路径 | 说明 |
|------|------|------|
| `tasks` | `infrastructure/storage/migrations/001_task_system.sql` | 任务主表 |
| `task_steps` | `infrastructure/storage/migrations/001_task_system.sql` | 任务步骤表 |
| `task_events` | `infrastructure/storage/migrations/001_task_system.sql` | 任务事件表 |
| `tool_calls` | `infrastructure/storage/migrations/001_task_system.sql` | 工具调用表 |
| `scheduled_messages` | `infrastructure/storage/migrations/001_task_system.sql` | 定时消息表 |

### Checkpoint 相关路径

| 文件 | 路径 | 说明 |
|------|------|------|
| Checkpoint 存储 | `orchestration/state/checkpoint_store.py` | 检查点存储模块 |
| Checkpoint 数据 | `data/checkpoints/` | 检查点数据目录 |
| 工作流实例存储 | `orchestration/state/workflow_instance_store.py` | 工作流实例持久化 |

### 数据库表命名规范

**所有表名统一使用 snake_case**：

| 正确 | 错误 |
|------|------|
| `task_runs` | ~~taskruns~~ |
| `task_events` | ~~taskevents~~ |
| `tool_calls` | ~~toolcalls~~ |

---

## 文档体系

### 根目录核心文件

| 文件 | 职责 |
|------|------|
| `AGENTS.md` | 工作空间规则 |
| `SOUL.md` | 身份定义 |
| `USER.md` | 用户信息 |
| `TOOLS.md` | 工具规则 |
| `IDENTITY.md` | 身份标识 |
| `MEMORY.md` | 长期记忆 |
| `HEARTBEAT.md` | 心跳任务 |
| `BOOTSTRAP.md` | 启动引导 |
| `SKILL.md` | 技能说明 |
| `README.md` | 项目说明 |
| `Makefile` | 构建目标 |
| `openclaw.bundle.json` | 打包配置 |

### 核心规则文件 (core/)

| 文件 | 职责 |
|------|------|
| `ARCHITECTURE.md` | 本文件，唯一主架构 |
| `RULE_REGISTRY.json` | 规则注册表 |
| `RULE_EXCEPTIONS.json` | 规则例外注册表 |
| `RULE_LIFECYCLE_POLICY.md` | 规则生命周期策略 |
| `RULE_EXCEPTION_POLICY.md` | 规则例外策略 |
| `RULE_EXCEPTION_DEBT_POLICY.md` | 例外债务策略 |
| `FUSION_POLICY.md` | 融合策略 |
| `LAYER_DEPENDENCY_MATRIX.md` | 层间依赖矩阵 |
| `LAYER_DEPENDENCY_RULES.json` | 依赖规则配置 |
| `LAYER_IO_CONTRACTS.md` | IO 契约清单 |
| `CHANGE_IMPACT_MATRIX.md` | 变更影响矩阵 |
| `SINGLE_SOURCE_OF_TRUTH.md` | 唯一真源清单 |
| `contracts/*.schema.json` | Schema 契约 |

### 文档目录 (docs/)

| 目录/文件 | 内容 |
|-----------|------|
| `docs/API_REFERENCE.md` | API 参考文档 |
| `docs/CHANGELOG.md` | 变更日志 |
| `docs/CONTRIBUTING.md` | 贡献指南 |
| `docs/FILE_INVENTORY.md` | 文件清单 |
| `docs/FUSION_REPORT.md` | 融合报告 |
| `docs/OPTIMIZATION_*.md` | 优化文档 |
| `docs/history/` | 升级历史记录 |
| `docs/archives/` | 架构文档归档 |

### 治理文档 (governance/docs/)

| 文件 | 内容 |
|------|------|
| `governance/docs/SAFETY_DECLARATION.md` | 安全声明 |
| `governance/docs/SECURITY.md` | 安全说明 |

---

## 技能体系

### 技能目录

**路径**: `skills/`

**统计**: 168 个技能

### 核心可执行技能

| 技能 | 功能 |
|------|------|
| docx | DOCX 文件校验 |
| pdf | PDF 文件校验 |
| cron | Cron 表达式校验 |
| file-manager | 文件复制 |

### 技能注册表

**路径**: `infrastructure/inventory/skill_registry.json`

---

## 脚本体系

### 检查脚本 (scripts/)

| 脚本 | 功能 |
|------|------|
| `run_rule_engine.py` | 统一规则引擎 V3.0.0 |
| `run_release_gate.py` | Release Gate 执行 |
| `check_layer_dependencies.py` | 层间依赖检查 |
| `check_json_contracts.py` | JSON 契约校验 |
| `check_repo_integrity.py` | 仓库完整性检查 |
| `check_repo_integrity_fast.py` | 快速仓库检查 |
| `check_change_impact.py` | 变更影响分析 |
| `check_skill_security.py` | 技能安全扫描 |
| `render_premerge_summary.py` | Premerge Summary |
| `render_nightly_summary.py` | Nightly Summary |
| `render_release_summary.py` | Release Summary |

---

## 报告体系

### 报告目录结构

```
reports/
├── runtime_integrity.json      # Runtime 完整性
├── quality_gate.json           # Quality Gate
├── release_gate.json           # Release Gate
├── alerts/                     # 告警
├── dashboard/                  # Dashboard
├── ops/
│   ├── rule_registry_snapshot.json      # 规则快照
│   ├── rule_engine_report.json          # 规则引擎报告
│   ├── rule_execution_index.json        # 规则执行索引
│   ├── rule_exceptions_snapshot.json    # 例外快照
│   └── rule_exception_debt.json         # 例外债务快照
├── remediation/                # 处置
└── history/                    # 历史
```

---

## 门禁体系

### Profile 规则

| Profile | 规则集 |
|---------|--------|
| premerge | R001-R008 |
| nightly | R001-R003, R005-R008 |
| release | R001-R003, R005-R008 |

### 命令

```bash
# 规则引擎
python scripts/run_rule_engine.py --profile premerge --save

# Release Gate
python scripts/run_release_gate.py premerge
python scripts/run_release_gate.py nightly
python scripts/run_release_gate.py release
```

---

## Token 预算

| 层级 | Token | 加载模式 |
|------|-------|----------|
| L1 Core | 3000 | 立即加载 |
| L2 Memory Context | 2000 | 按需加载 |
| L3 Orchestration | 1500 | 按需加载 |
| L4 Execution | 1500 | 延迟加载 |
| L5 Governance | 800 | 敏感加载 |
| L6 Infrastructure | 700 | 系统加载 |
| **总计** | **9500** | |

---

## 版本历史

- V5.0.0: 规则平台化 + 例外债务治理 + 融合机制 + 性能优化
- V4.3.6: 融合机制融入架构
- V4.3.5: 文档体系整理
- V4.3.4: 技能体系 + 脚本体系 + 报告体系融入架构
- V4.3.0: 架构收口，统一为六层
- V4.0.0: 完整六层架构

---

## 融合索引

**路径**: `infrastructure/inventory/fusion_index.json`

**功能**: 统一入口，快速定位所有配置和索引

**索引内容**:
- 技能注册表 + 倒排索引
- 规则注册表 + 例外注册表
- 统一配置 + LLM 配置
- 报告目录

---

## 性能优化

| 优化项 | 状态 |
|--------|------|
| 并行巡检 | ✅ 启用 |
| 结果缓存 | ✅ 启用 |
| 懒加载技能 | ✅ 启用 |
| 批量操作 | ✅ 启用 |
| 异步 I/O | ✅ 启用 |

**性能目标**:
- 技能查询: < 1ms
- 规则检查: < 100ms
- 全量巡检: < 15s
- 4096维 Embedding: < 500ms
- 向量搜索: < 100ms

---

## Token 优化体系

### 注入模式

| 模式 | Token | 用途 |
|------|-------|------|
| 全量注入 | 13,000,000 | 完整分析 |
| 精简注入 | ~5,000 | 日常使用 |
| 极简注入 | ~2,800 | 快速响应 |
| 智能注入 | ~2,000 | 自动压缩 |

### 配置文件

| 文件 | 模式 |
|------|------|
| injection_config.json | 精简模式 |
| injection_config_minimal.json | 极简模式 |
| injection_config_smart.json | 智能模式 |

### 工具

| 工具 | 功能 |
|------|------|
| smart_compressor.py | 智能压缩 |
| incremental_updater.py | 增量更新 |
| auto_summarizer.py | 自动摘要 |

### 懒加载

| 资源 | 方式 |
|------|------|
| 技能 | find-skills |
| 记忆 | memory_search |
| 配置 | read 按需 |
| 报告 | read 按需 |

---

## LLM 记忆集成

### 技能信息
- **名称**: llm-memory-integration
- **版本**: 5.1.5
- **分类**: memory

### Embedding 配置
| 配置项 | 值 |
|--------|-----|
| 提供商 | Gitee AI |
| 模型 | Qwen3-Embedding-8B |
| 维度 | **4096** (业界最高) |

### LLM 配置
| 配置项 | 值 |
|--------|-----|
| 提供商 | Gitee AI |
| 模型 | Qwen3-235B-A22B |

### 三引擎架构
| 引擎 | 类型 | 状态 |
|------|------|------|
| sqlite-vec | 主引擎 | ✅ 启用 |
| qdrant | 副引擎 | ✅ 启用 |
| tfidf | 备份引擎 | ✅ 启用 |

### 高级功能
| 功能 | 状态 |
|------|------|
| 用户画像自动更新 | ✅ 启用 |
| 三引擎同步 | ✅ 启用 |
| LLM 辅助 | ✅ 启用 |
| 渐进式启用 | ✅ P0-P3 全启用 |

---

## 依赖管理机制

### 模块信息
- **脚本**: `scripts/dependency_manager.py`
- **配置**: `infrastructure/config/dependency_manifest.json`
- **报告**: `reports/ops/dependency_status.json`

### 依赖分类

| 类别 | 包含依赖 | 必需性 |
|------|----------|--------|
| core | numpy, scipy, scikit-learn | 必需 |
| llm | openai, anthropic, langchain | 可选 |
| embedding | sentence-transformers, transformers | 可选 |
| vector | qdrant-client, chromadb, faiss-cpu | 可选 |
| ml | torch, numba, llvmlite | 可选 |
| performance | numexpr, bottleneck | 可选 |
| document | reportlab, weasyprint, pdfkit | 可选 |

### 使用方式

```bash
# 检查依赖状态
python scripts/dependency_manager.py --check

# 安装缺失依赖
python scripts/dependency_manager.py --install

# 安装特定类别
python scripts/dependency_manager.py --install --category ml
```

---

## 删除确认机制

### 核心原则
**所有删除操作必须经过用户确认！**

### 模块信息
- **脚本**: `scripts/delete_manager.py`
- **回收站**: `archive/trash/`
- **日志**: `reports/ops/delete_log.json`
- **待确认**: `reports/ops/pending_deletes.json`

### 删除流程

```
请求删除 → 创建待确认请求 → 用户确认 → 移至回收站
                ↓
            用户拒绝 → 取消删除
```

### 使用方式

```bash
# 请求删除
python scripts/delete_manager.py --request "path" --reason "原因"

# 查看待确认请求
python scripts/delete_manager.py --list

# 确认删除
python scripts/delete_manager.py --confirm <request_id>

# 拒绝删除
python scripts/delete_manager.py --reject <request_id>

# 从回收站恢复
python scripts/delete_manager.py --restore "path"

# 清空回收站
python scripts/delete_manager.py --empty-trash 7
```

### 受保护文件

| 文件 | 保护原因 |
|------|----------|
| core/ARCHITECTURE.md | 架构文档 |
| core/RULE_REGISTRY.json | 规则注册表 |
| core/SOUL.md | 身份定义 |
| core/USER.md | 用户信息 |
| core/AGENTS.md | 工作空间规则 |
| core/TOOLS.md | 工具规则 |
| MEMORY.md | 长期记忆 |

### 禁止操作

- ❌ 直接使用 `rm` 命令
- ❌ 直接使用 `os.remove()`
- ❌ 直接使用 `shutil.rmtree()`
- ✅ 必须通过 `delete_manager.py`

## V7.1.0 架构扩展

### 认知层 (L1 Core)
新增 `core/cognition/` 认知系统：
- **推理引擎**: 演绎、归纳、溯因、类比、因果、反事实推理
- **决策系统**: 加权求和、AHP层次分析、TOPSIS决策
- **规划引擎**: 目标分解、依赖管理、进度跟踪
- **反思系统**: 行动、结果、过程、策略反思
- **学习系统**: 强化学习、监督学习、元学习、知识迁移

### 治理层扩展 (L5 Governance)
新增子模块：
- **recovery/**: 状态恢复、故障恢复、回滚管理
- **review/**: 变更审查、决策审查、合规审查
- **rules/**: 规则引擎、规则监控、规则生命周期
- **risk/**: 风险分类、高风险护栏、**技能滥用防护 (V2.0)**

#### 技能滥用防护 (Skill Abuse Guard V2.0)

**路径**: `governance/risk/skill_abuse_guard.py`

**检测能力**:
| 攻击类型 | 检测方式 | 处理措施 |
|----------|----------|----------|
| 内存泄漏 | 内存增长趋势分析 | 标记/限流 |
| DDoS | 调用频率统计 | 自动封禁 |
| CPU炸弹 | CPU使用率监控 | 限流/熔断 |
| IO炸弹 | IO速率监控 | 限流 |
| 网络滥用 | 网络流量监控 | 限流 |
| 数据泄露 | 出站数据量检测 | 封禁 |
| 递归炸弹 | 调用链深度检查 | 阻断 |
| 无限循环 | 执行时间监控 | 终止 |
| 载荷炸弹 | 载荷大小检查 | 阻断 |
| 并发溢出 | 并发数监控 | 排队 |
| 可疑模式 | 多维度模式识别 | 警告 |

**防护机制**:
- 自适应限流 (令牌桶算法)
- 智能熔断 (三态熔断器: closed/open/half_open)
- 系统资源监控 (CPU/内存/磁盘)
- 攻击模式学习
- 实时告警回调
- 审计日志 (JSONL)

**集成位置**: `skills/runtime/skill_router.py`

### 基础设施扩展 (L6 Infrastructure)
新增 `automation/` 自动化模块：
- **任务自动化器**: 队列管理、并发执行、自动重试
- **事件触发器**: 事件注册、条件匹配、冷却时间
- **智能调度器**: 周期调度、资源管理、依赖管理
- **流水线执行器**: 阶段管理、并行执行、上下文传递

### 能力矩阵
| 能力维度 | 模块数 | 覆盖率 |
|----------|--------|--------|
| 认知能力 | 5 | 100% |
| 恢复能力 | 3 | 100% |
| 审查能力 | 3 | 100% |
| 规则管控 | 3 | 100% |
| 自动化 | 4 | 100% |
| 滥用防护 | 1 | 100% |

---

| 技能管理 | 1 | 100% |
| 风险管控 | 1 | 100% |
## 运营体系 (POST RELEASE)

### 发布后基线

**路径**: `reports/POST_RELEASE_BASELINE.md`

**当前版本**: V7.2.0 Phase3 Final

**稳定通道**: `stable`

**原则**: 不再大改架构，开始用真实任务养系统

### 真实任务清单

**路径**: `reports/live_tasks/top10_real_tasks.json`

**任务列表**:
1. 每日工作总结生成 (个人/每日/低风险)
2. 会议提醒与准备 (个人/每日/低风险)
3. 重要日期提醒 (个人/每日/低风险)
4. 文档格式转换 (个人/每周/低风险)
5. 信息快速记录 (个人/每日/低风险)
6. 日程冲突检测 (个人/每日/低风险)
7. 联系人信息查询 (个人/每日/低风险)
8. 照片快速查找 (个人/每周/低风险)
9. 定时提醒任务 (个人/每日/低风险)
10. 工作周报生成 (企业/每周/中风险)

### 养成记忆

**路径**: `reports/live_learning/`

| 文件 | 用途 |
|------|------|
| `decision_patterns.json` | 决策模式沉淀 |
| `user_preferences.json` | 用户偏好沉淀 |
| `company_rules.json` | 企业规则沉淀 |

### 迭代原则

只允许三种类型：
1. 新真实任务接入
2. 真实使用中暴露的问题修补
3. 基于 metrics 的小优化

**禁止**:
- 没有真实使用场景就大改架构
- 没有回放证据就重写主链
- 为了"更高级"去继续拆层、加层
