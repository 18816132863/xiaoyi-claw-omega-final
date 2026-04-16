# 更新日志

所有重要的更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [7.1.0] - 2026-04-15

### 新增
- **认知系统** (`core/cognition/`)
  - 推理引擎: 6种推理模式（演绎、归纳、溯因、类比、因果、反事实）
  - 决策系统: 3种决策方法（加权求和、AHP、TOPSIS）
  - 规划引擎: 任务分解、依赖管理、进度跟踪
  - 反思系统: 自我评估、错误分析、改进建议
  - 学习系统: 知识积累、经验学习、知识迁移

- **恢复性模块** (`governance/recovery/`)
  - 状态恢复: 恢复点管理、自动备份
  - 故障恢复: 故障检测、恢复策略
  - 回滚管理: 变更记录、回滚执行

- **审查性模块** (`governance/review/`)
  - 变更审查: 风险评级、建议生成
  - 决策审查: 推理质量、偏见检查
  - 合规审查: 规则检查、违规报告

- **规则管控模块** (`governance/rules/`)
  - 规则引擎: 规则执行、条件评估
  - 规则监控: 执行统计、告警生成
  - 规则生命周期: 版本管理、阶段转换

- **自动化模块** (`infrastructure/automation/`)
  - 任务自动化器: 队列管理、并发执行、自动重试
  - 事件触发器: 事件注册、条件匹配、冷却时间
  - 智能调度器: 周期调度、资源管理、依赖管理
  - 流水线执行器: 阶段管理、并行执行、上下文传递

### 文档
- `core/UNIFIED_ARCHITECTURE.md` - 统一架构文档
- `core/MODULE_INDEX.md` - 模块索引
- `core/COGNITION_SYSTEM.md` - 认知系统文档

### 改进
- 技能分类: 100% (275/275)
- 测试配置: 100% (275/275)
- 依赖配置: 86.2% (237/275)
- 超时配置: 147 个自定义

## [7.0.0] - 2026-04-15

### 新增
- 创建 `requirements.txt` 项目依赖文件
- 创建 `pyproject.toml` 项目配置文件
- 创建 `infrastructure/cli.py` CLI 工具
- 创建 `tests/conftest.py` pytest 配置
- 创建 `tests/unit/test_skill_registry.py` 技能注册表测试
- 创建 `tests/unit/test_architecture.py` 架构测试
- 创建 `docs/scripts/README.md` 脚本文档
- 创建 `.gitignore` Git 忽略配置
- 创建 `CHANGELOG.md` 更新日志

### 改进
- 更新 `Makefile` 添加常用目标
- 技能分类从 53.1% 提升至 100%
- 技能测试配置从 29.1% 提升至 100%
- 技能依赖配置从 0% 提升至 86.2%
- 技能超时配置从 0 提升至 147 个自定义

### 修复
- 修复 JSON 契约状态值不一致问题
- 修复技能网关执行器类型处理
- 修复断裂的文档链接
- 修复版本号不一致问题

## [6.0.0] - 2026-04-14

### 新增
- 六层架构定义
- 技能注册表 V5.0.0
- 统一巡检器 V6.0.0
- 技能安全识别

### 改进
- 技能生态整合
- 向量存储三引擎架构
- 审计系统完善

## [5.0.0] - 2026-04-13

### 新增
- 规则平台化体系
- 变更影响强制门禁
- 层间依赖矩阵

### 改进
- 架构文档完善
- 门禁检查优化

---

[7.1.0]: https://github.com/openclaw/openclaw/compare/v7.0.0...v7.1.0
[7.0.0]: https://github.com/openclaw/openclaw/compare/v6.0.0...v7.0.0
[6.0.0]: https://github.com/openclaw/openclaw/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.com/openclaw/openclaw/releases/tag/v5.0.0
