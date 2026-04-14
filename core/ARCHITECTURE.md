# 六层架构定义 V5.2.0

> **唯一主架构定义** - 本文档是项目唯一正式运行架构定义
> 
> 其他架构文档（ARCHITECTURE_V2.x.x.md、OMEGA_FINAL.md 等）均为历史兼容资料，位于 `docs/archives/`

---

## 六层架构

| 层级 | 名称 | 职责 | 目录 |
|------|------|------|------|
| L1 | Core | 核心认知、身份、规则、标准 | `core/` |
| L2 | Memory Context | 记忆上下文、知识库、统一搜索、向量存储 | `memory_context/` |
| L3 | Orchestration | 任务编排、工作流、路由、策略 | `orchestration/` |
| L4 | Execution | 能力执行、技能网关、交付 | `execution/` |
| L5 | Governance | 稳定治理、安全审计、合规、计费 | `governance/` |
| L6 | Infrastructure | 基础设施、工具链、注册表、运维 | `infrastructure/` |

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
