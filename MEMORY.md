# MEMORY.md - 长期记忆

此文件用于存储跨会话的重要信息、决策和上下文。

## 项目状态

- **版本**: V5.0.0
- **状态**: 规则平台化完成
- **更新时间**: 2026-04-14

## 架构概览

六层架构：
- L1: Core - 核心认知、身份、规则、标准
- L2: Memory Context - 记忆上下文、知识库
- L3: Orchestration - 任务编排、工作流
- L4: Execution - 能力执行、技能网关
- L5: Governance - 稳定治理、安全审计
- L6: Infrastructure - 基础设施、工具链

## V5.0.0 新增模块

### 规则平台化
- `core/RULE_REGISTRY.json`: 统一规则注册表，定义 6 条规则
- `scripts/run_rule_engine.py`: 统一规则引擎 V1.0.0
- `reports/ops/rule_execution_index.json`: 规则执行索引
- `reports/ops/rule_engine_report.json`: 规则引擎报告

### 变更影响强制门禁
- `governance/CHANGE_IMPACT_ENFORCEMENT_POLICY.md`: 变更影响强制门禁策略
- `scripts/check_change_impact.py`: 变更影响分析器 V3.0.0
- `scripts/check_change_impact_enforcement.py`: 强制门禁检查器 V2.0.0
- `reports/ops/change_impact.json`: 变更影响报告
- `reports/ops/change_impact_enforcement.json`: 强制门禁报告
- `reports/ops/followup_requirements.json`: follow-up 要求记录

### 技能安全识别
- `scripts/check_skill_security.py`: 技能安全识别器 V1.0.0
- 检测 8 类高危 Skill（密钥收割型、挖矿注入型、动态拉取型等）
- `reports/ops/skill_security_report.json`: 安全扫描报告

### 循环防护
- `execution/loop_guard.py`: 循环防护模块
- `docs/loop_guard_design.md`: 设计文档

### 规则守卫自测
- `scripts/check_rule_guards.py`: 规则守卫自测入口
- `tests/rule_violations/`: 违规样例目录

## 关键配置

- Embedding: Qwen3-Embedding-8B (1024维)
- LLM: Qwen3-235B-A22B
- API: Gitee AI (https://ai.gitee.com/v1)
- 性能模式: maximum

## Git 认证

- 仓库: https://github.com/18816132863/xiaoyi-claw-omega-final.git
- Token: 见 git remote -v 输出（已配置在远程 URL 中）
- 注意: Token 不应写入文件，使用环境变量或 git credential

## 技能列表

已安装 274 个技能，包括：
- llm-memory-integration (v3.5.1)
- memory-setup
- find-skills
- skillhub-preference

## 注意事项

- 受保护文件不可删除
- 使用 trash 替代 rm
- 敏感操作需确认
- Token 等敏感信息不要写入文件
- 规则检查失败会阻断门禁
