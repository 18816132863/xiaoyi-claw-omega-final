# 更新日志

所有重要的更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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
- 修复 11 个 SKILL.md 缺字段问题
- 创建 227 个 requirements.txt 文件

### 修复
- 修复 JSON 契约状态值不一致问题
- 修复技能网关执行器类型处理
- 修复断裂的文档链接
- 修复版本号不一致问题

### 工具
- `scripts/skill_health_check.py` 技能健康检查
- `scripts/auto_classify_skills.py` 技能自动分类
- `scripts/cleanup_reports.py` 报告清理自动化

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

[7.0.0]: https://github.com/openclaw/openclaw/compare/v6.0.0...v7.0.0
[6.0.0]: https://github.com/openclaw/openclaw/compare/v5.0.0...v6.0.0
[5.0.0]: https://github.com/openclaw/openclaw/releases/tag/v5.0.0
