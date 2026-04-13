# MEMORY.md - 长期记忆

此文件用于存储跨会话的重要信息、决策和上下文。

## 项目状态

- **版本**: V4.3.3
- **状态**: 架构融合完成
- **更新时间**: 2026-04-12

## 架构概览

六层架构：
- L1: Core - 核心认知、身份、规则、标准
- L2: Memory Context - 记忆上下文、知识库
- L3: Orchestration - 任务编排、工作流
- L4: Execution - 能力执行、技能网关
- L5: Governance - 稳定治理、安全审计
- L6: Infrastructure - 基础设施、工具链

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

已安装 165 个技能，包括：
- llm-memory-integration (v3.5.1)
- memory-setup
- find-skills
- skillhub-preference

## 注意事项

- 受保护文件不可删除
- 使用 trash 替代 rm
- 敏感操作需确认
- Token 等敏感信息不要写入文件
