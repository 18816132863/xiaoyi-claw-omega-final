# 六层架构定义 V4.3.4

> **唯一主架构定义** - 本文档是项目唯一正式运行架构定义
> 
> 其他架构文档（ARCHITECTURE_V2.x.x.md、OMEGA_FINAL.md 等）均为历史兼容资料，位于 `archive/deprecated/`

## 六层架构

| 层级 | 名称 | 职责 | 目录 |
|------|------|------|------|
| L1 | Core | 核心认知、身份、规则、标准 | `core/` |
| L2 | Memory Context | 记忆上下文、知识库、统一搜索 | `memory_context/` |
| L3 | Orchestration | 任务编排、工作流、路由、策略 | `orchestration/` |
| L4 | Execution | 能力执行、技能网关、交付 | `execution/` |
| L5 | Governance | 稳定治理、安全审计、合规、计费 | `governance/` |
| L6 | Infrastructure | 基础设施、工具链、注册表、运维 | `infrastructure/` |

---

## 技能体系

### 技能目录

**路径**: `skills/`

**统计**:
- 总技能数: 168
- 已注册: 156
- 可执行: 4 (docx, pdf, cron, file-manager)

### 核心可执行技能

| 技能 | 路径 | 功能 |
|------|------|------|
| docx | `skills/docx/skill.py` | DOCX 文件校验 |
| pdf | `skills/pdf/skill.py` | PDF 文件校验 |
| cron | `skills/cron/skill.py` | Cron 表达式校验 |
| file-manager | `skills/file-manager/skill.py` | 文件复制 |

### 技能注册表

**路径**: `infrastructure/inventory/skill_registry.json`

**核心字段**:
- `name`: 技能名称
- `registered`: 是否已注册
- `routable`: 是否可路由
- `callable`: 是否可调用
- `entry_point`: 入口文件路径
- `test_mode`: 测试模式 (local/integration)

### 技能倒排索引

**路径**: `infrastructure/inventory/skill_inverted_index.json`

**功能**: 按 trigger 快速定位技能

---

## 脚本体系

### 运维脚本 (scripts/)

| 脚本 | 功能 |
|------|------|
| `ops_center.py` | 运维中心统一入口 |
| `remediation_center.py` | 处置中心 |
| `approval_manager.py` | 审批管理器 |
| `control_plane.py` | 控制平面状态聚合 |
| `control_plane_audit.py` | 控制平面审计聚合 |
| `run_release_gate.py` | Release Gate 执行 |
| `run_nightly_audit.py` | Nightly Audit 执行 |
| `generate_alerts.py` | 告警生成 |
| `build_ops_dashboard.py` | Dashboard 构建 |
| `incident_cli.py` | Incident CLI |
| `check_repo_integrity.py` | 仓库完整性检查 |
| `render_premerge_summary.py` | Premerge Summary 渲染 |
| `render_nightly_summary.py` | Nightly Summary 渲染 |
| `render_release_summary.py` | Release Summary 渲染 |

### 基础设施脚本 (infrastructure/)

| 脚本 | 功能 |
|------|------|
| `verify_runtime_integrity.py` | Runtime 完整性验证 |
| `path_resolver.py` | 统一路径解析 |
| `architecture_inspector.py` | 架构巡检 |
| `auto_git.py` | 自动 Git 同步 |
| `backup_*.py` | 备份工具集 |

---

## 报告体系

### 报告目录结构

```
reports/
├── runtime_integrity.json      # Runtime 完整性报告
├── quality_gate.json           # Quality Gate 报告
├── release_gate.json           # Release Gate 报告
├── nightly_audit.json          # Nightly Audit 报告
├── nightly_summary.md          # Nightly Summary
├── alerts/
│   ├── latest_alerts.json      # 最新告警
│   ├── notification_result.json # 通知结果
│   └── incident_summary.json   # Incident 摘要
├── dashboard/
│   ├── ops_dashboard.json      # Dashboard 数据
│   ├── ops_dashboard.md        # Dashboard Markdown
│   └── ops_dashboard.html      # Dashboard HTML
├── ops/
│   ├── ops_state.json          # 运维状态
│   ├── control_plane_state.json # 控制平面状态
│   └── control_plane_audit.json # 控制平面审计
├── remediation/
│   ├── approval_queue.json     # 审批队列
│   ├── approval_history.json   # 审批历史
│   ├── latest_remediation.json # 最新处置
│   ├── remediation_summary.json # 处置摘要
│   ├── auto_execute_audit.json # 自动执行审计
│   ├── auto_execute_summary.json # 自动执行摘要
│   ├── remediation_guard.json  # 熔断状态
│   └── history/                # 处置历史
│       └── rem_*.json          # 处置记录
├── trends/
│   └── gate_trend.json         # 门禁趋势
├── bundles/
│   └── ops_bundle_*.zip        # 证据包
└── history/
    ├── runtime/                # Runtime 历史
    ├── quality/                # Quality 历史
    └── release/                # Release 历史
```

---

## 巡检体系

### 仓库完整性检查

**脚本**: `scripts/check_repo_integrity.py`

**检查项**:
1. 必需文件存在
2. 必需目录存在
3. Makefile 目标
4. Workflow 完整性
5. 脚本依赖
6. 审批历史与 remediation history 一致性

**命令**:
```bash
python scripts/check_repo_integrity.py --strict
```

### 架构巡检

**脚本**: `infrastructure/architecture_inspector.py`

**检查项**:
1. 六层架构完整性
2. 文件保护状态
3. 技能注册一致性
4. 目录结构合规

**命令**:
```bash
python infrastructure/architecture_inspector.py
```

---

## 版本历史

- V4.3.4: 技能体系 + 脚本体系 + 报告体系 + 巡检体系融入架构
- V4.3.3: 第九阶段运维平台收口 + 审批主链做实
- V4.3.2: 第一阶段主链打通 + 第二阶段搜索统一
- V4.3.0: 架构收口，统一为六层
- V4.2.x: 性能优化
- V4.1.0: 纯文档版本
- V4.0.0: 完整六层架构

---
- `executor_type`: 执行类型 (python/script/api/skill_md)
- `entry_point`: 入口文件
- `path`: 技能路径（相对路径）

**状态一致性**:
- `executor_type=skill_md` → `callable=false`
- `callable=true` → `entry_point` 不能是 `SKILL.md`
- `registered=true && routable=true && callable=true` → 进入反向索引

### 反向索引

**路径**: `infrastructure/inventory/skill_inverted_index.json`

**规则**:
- 只索引可执行技能
- 触发词映射到技能名称

### 路由器

**路径**: `infrastructure/shared/router.py`

**功能**:
- 检查技能状态 (registered/routable/callable/status)
- 返回执行所需信息 (executor_type/entry_point/timeout)
- 按评分排序候选技能

### 技能网关

**路径**: `execution/skill_adapter_gateway.py`

**功能**:
- 启动时从 registry 加载技能
- 按 executor_type 分流执行 (python/script/api/skill_md)
- 统一错误码映射

### 任务引擎

**路径**: `orchestration/task_engine.py`

**功能**:
- 动态路由技能
- 五段流程 (validate → execute → verify → summarize)
- 内部步骤特殊处理
- 真实执行检查，无假成功

---

## 第二阶段：搜索与架构统一

### 统一搜索入口

**路径**: `memory_context/unified_search.py`

**组件**:
- `KeywordSearch`: 关键词搜索
- `FTSSearch`: 全文搜索
- `VectorSearch`: 向量搜索
- `RRFFusion`: RRF 融合
- `SemanticDedup`: 语义去重
- `FeedbackLearner`: 反馈学习
- `IndexExcludeList`: 索引排除名单

**搜索模式**:
- `fast`: 仅关键词搜索
- `balanced`: 关键词 + FTS
- `full`: 关键词 + FTS + 向量

### 索引排除配置

**路径**: `infrastructure/inventory/exclude_config.json`

**排除目录**:
- `node_modules`, `__pycache__`, `.git`
- `archive`, `reports`, `backups`
- `dist`, `build`, `.cache`, `logs`

**排除文件类型**:
- 二进制: `.pyc`, `.so`, `.dll`
- 压缩: `.tar`, `.gz`, `.zip`
- 媒体: `.mp3`, `.mp4`, `.jpg`, `.png`
- 锁文件: `package-lock.json`, `yarn.lock`

**大小限制**: 单文件最大 10MB

### 架构完整性规范

**路径**: `core/ARCHITECTURE_INTEGRITY.md`

**内容**:
- 引用本文件作为唯一主架构
- 定义注册表校验规范
- 定义路径规范
- 定义验收规则

### 历史架构归档

**路径**: `archive/deprecated/`

**文件**:
- `ARCHITECTURE_V2.8.1.md`
- `ARCHITECTURE_V2.9.0.md`
- `ARCHITECTURE_V2.9.1.md`

**标注**: "仅历史参考，不作为当前运行依据"

---

## 层级调用规则

```
请求流: 用户请求 → L1解析 → L3路由 → L4执行 → L5验证 → 返回结果
保护流: 删除请求 → L5文件保护 → 人工确认 → L6执行 → L5审计日志
记忆流: L1触发词 → L2统一搜索 → L3编排 → L4执行 → L2存储结果
巡检流: 定时触发 → L5巡检 → L6注册表 → L4技能健康检查 → L5报告
```

---

## Token 预算

| 层级 | Token 预算 | 加载模式 |
|------|-----------|----------|
| L1 Core | 3000 | 立即加载 |
| L2 Memory Context | 2000 | 按需加载 |
| L3 Orchestration | 1500 | 按需加载 |
| L4 Execution | 1500 | 延迟加载 |
| L5 Governance | 800 | 敏感加载 |
| L6 Infrastructure | 700 | 系统加载 |
| **总计** | **9500** | |

---

## 核心文件

### L1 核心认知层
- `AGENTS.md` - 工作空间规则
- `SOUL.md` - 身份定义
- `USER.md` - 用户信息
- `TOOLS.md` - 工具规则
- `IDENTITY.md` - 身份标识
- `ARCHITECTURE.md` - 本文件
- `ARCHITECTURE_INTEGRITY.md` - 完整性规范

### L2 记忆上下文层
- `MEMORY.md` - 长期记忆
- `memory/*.md` - 日记文件
- `memory_context/unified_search.py` - 统一搜索入口
- `memory_context/search/` - 搜索模块
- `memory_context/cache/` - 缓存模块

### L3 任务编排层
- `orchestration/task_engine.py` - 任务引擎
- `orchestration/router/` - 路由配置
- `orchestration/workflows/` - 工作流

### L4 能力执行层
- `execution/skill_adapter_gateway.py` - 技能接入网关
- `execution/skill_gateway.py` - 技能执行网关
- `execution/ecommerce/` - 电商执行器

### L5 稳定治理层
- `governance/security.py` - 安全检查
- `governance/permissions.py` - 权限管理
- `governance/audit/` - 审计日志
- `governance/validators/` - 校验器
- `governance/quality_gate.py` - 质量门禁

### L6 基础设施层
- `infrastructure/path_resolver.py` - 路径解析器
- `infrastructure/shared/router.py` - 统一路由器
- `infrastructure/inventory/skill_registry.json` - 技能注册表
- `infrastructure/inventory/skill_inverted_index.json` - 反向索引
- `infrastructure/inventory/exclude_config.json` - 排除配置
- `infrastructure/manifest/` - Manifest 生成器

---

## 路径规范

**禁止**:
- `Path.home()`
- `~/.openclaw`
- 绝对路径

**必须**:
- 使用 `infrastructure/path_resolver.py`
- `get_project_root()` 获取项目根目录
- `get_skills_dir()` 获取技能目录
- `get_infrastructure_dir()` 获取基础设施目录

---

## 验收规则

### 第一阶段验收
- [ ] 技能注册表字段完整
- [ ] 反向索引与注册表一致
- [ ] 路由能命中可执行技能
- [ ] 技能能真实执行
- [ ] Task 不返回假成功
- [ ] 内部步骤不显示 failed

### 第二阶段验收
- [ ] 统一搜索入口可用
- [ ] 搜索结果经过 RRF 融合
- [ ] 搜索结果经过去重
- [ ] 索引排除名单生效
- [ ] 无硬编码路径
- [ ] 历史架构已归档

---

## 版本历史

- V4.3.3: 第九阶段运维平台收口 + 审批主链做实
- V4.3.2: 第一阶段主链打通 + 第二阶段搜索统一
- V4.3.0: 架构收口，统一为六层
- V4.2.x: 性能优化
- V4.1.0: 纯文档版本
- V4.0.0: 完整六层架构

---

## 第九阶段：运维平台收口

### 控制平面

**路径**: `scripts/control_plane.py`

**功能**:
- 聚合所有运维状态到统一视图
- 输出 `reports/ops/control_plane_state.json`

**聚合内容**:
- `overview`: Runtime/Quality/Release 概览
- `gates`: 门禁状态详情
- `alerts`: 告警状态
- `incidents`: Incident 状态
- `remediation`: 处置状态
- `approvals`: 审批摘要
- `notifications`: 通知状态
- `dashboard`: Dashboard 状态
- `trends`: 趋势状态

### 控制平面审计

**路径**: `scripts/control_plane_audit.py`

**功能**:
- 聚合历史审计记录
- 输出 `reports/ops/control_plane_audit.json`

**聚合内容**:
- `release_gates`: 最近 release gate 记录
- `nightly_audits`: 最近 nightly audit 记录
- `blocking_alerts`: 最近 blocking alerts
- `incidents`: 最近 incidents
- `remediations`: 最近 remediation 记录
- `approvals`: 结构化审批摘要
- `timeline`: 时间线事件

### 审批管理器

**路径**: `scripts/approval_manager.py`

**功能**:
- 管理 semi_auto 动作的审批流程
- 状态归一化：pending/executed/execute_failed/denied/approved_legacy

**核心函数**:
- `normalize_approval_record()`: 状态归一化
- `add_to_queue()`: 添加到审批队列
- `grant()`: 批准并执行
- `deny()`: 拒绝
- `record_execute()`: 回填执行记录

**状态规则**:
| 状态 | 说明 |
|------|------|
| pending | 待审批 |
| executed | 批准后执行成功 |
| execute_failed | 批准后执行失败 |
| denied | 拒绝 |
| approved_legacy | 历史遗留记录 |

**产物**:
- `reports/remediation/approval_queue.json`: 审批队列
- `reports/remediation/approval_history.json`: 审批历史

### 处置中心

**路径**: `scripts/remediation_center.py`

**功能**:
- 统一处置入口
- 支持 safe_auto / semi_auto / forbidden_auto 分类

**命令**:
- `plan`: 输出建议处置动作
- `dry-run`: 模拟执行
- `execute`: 执行动作
- `auto-execute`: 受控自动执行
- `history`: 查看处置历史
- `guard`: 查看熔断状态
- `audit`: 查看审计记录

**动作分类**:
| 类别 | 动作 | 说明 |
|------|------|------|
| safe_auto | rebuild_dashboard, rebuild_ops_state, rebuild_bundle, retry_notifications | 可自动执行 |
| semi_auto | rerun_nightly, rerun_release_gate, rerun_integration, toggle_incident | 需审批 |
| forbidden_auto | modify_core_arch, modify_skill_registry, ... | 禁止自动执行 |

### 运维中心

**路径**: `scripts/ops_center.py`

**命令**:
- `status`: 查看总状态
- `verify`: 运行门禁
- `incidents`: 管理 incidents
- `alerts`: 查看告警
- `dashboard`: 构建看板
- `bundle`: 打包证据
- `remediation`: 处置管理
- `guard`: 查看熔断状态
- `audit`: 查看审计记录
- `control-plane`: 控制平面命令
- `approval`: 审批命令

### 审批主链

**流程**:
```
semi_auto 动作 → 自动入审批队列 → grant 批准 → 真实执行 → 回填 execute_record_id
```

**关键约束**:
1. `execute_record_id` 必须是真实 remediation 记录 ID
2. 对应 `reports/remediation/history/<id>.json` 必须存在
3. 没有 history 文件不能标记为 executed

**产物关联**:
```
approval_history.json
  └─ execute_record_id
      └─ reports/remediation/history/<id>.json
```

### 报告体系扩展

```
reports/
├── ops/
│   ├── control_plane_state.json    # 控制平面状态
│   ├── control_plane_audit.json    # 控制平面审计
│   └── ops_state.json              # 运维状态
├── remediation/
│   ├── approval_queue.json         # 审批队列
│   ├── approval_history.json       # 审批历史
│   ├── latest_remediation.json     # 最新处置
│   ├── remediation_summary.json    # 处置摘要
│   ├── auto_execute_audit.json     # 自动执行审计
│   ├── auto_execute_summary.json   # 自动执行摘要
│   ├── remediation_guard.json      # 熔断状态
│   └── history/                    # 处置历史
│       └── rem_*.json              # 处置记录
└── ...
```

### 第九阶段验收

- [ ] control_plane_state.json 包含 approvals 摘要
- [ ] control_plane_audit.json 结构化输出
- [ ] approval_history.json 状态归一
- [ ] executed 记录有真实 execute_record_id
- [ ] execute_record_id 对应 history 文件存在
- [ ] summary 脚本显示 Approval Summary

---

## 门禁与验收体系

### 统一入口

```bash
# CI 门禁
python scripts/run_release_gate.py {premerge|nightly|release}

# 夜间巡检（带回归检测）
python scripts/run_nightly_audit.py
```

### Profile 规则

| Profile | P0 | Local | Integration | External |
|---------|-----|-------|-------------|----------|
| premerge | =0 | 必须 | 不阻塞 | 不阻塞 |
| nightly | =0 | 必须 | 必须 | 不阻塞 |
| release | =0 | 必须 | 必须 | 无 error |

### 报告体系

```
reports/
├── runtime_integrity.json      # 最新
├── quality_gate.json           # 最新
├── nightly_audit.json          # 审计
├── nightly_summary.md          # 摘要
├── trends/runtime_trend.json   # 趋势
└── history/                    # 历史快照
```

详见 `core/ARCHITECTURE_INTEGRITY.md`
