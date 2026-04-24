# 技能重构发布说明

## 版本: 8.3.0

## 核心变更

### 产品定位转变

**从**: 部署型任务系统
**到**: 平台增强型强内核技能

### 架构重构

#### 新增六层架构

1. **skill_entry** - 入口层
   - input_router.py - 输入路由
   - validators.py - 参数校验
   - response_formatter.py - 响应格式化
   - error_codes.py - 错误码定义

2. **orchestration** - 编排层
   - task_orchestrator.py - 任务编排
   - workflow_orchestrator.py - 工作流编排
   - batch_orchestrator.py - 批量编排

3. **capabilities** - 能力层
   - registry.py - 能力注册表
   - 10个能力实现文件

4. **platform_adapter** - 平台适配层
   - base.py - 适配器基类
   - null_adapter.py - 空适配器
   - runtime_probe.py - 运行时探测
   - xiaoyi_adapter.py - 小艺适配器

5. **diagnostics** - 诊断层
   - runtime_self_check.py - 自检
   - event_timeline.py - 事件时间线
   - error_explainer.py - 错误解释
   - capability_report.py - 能力报告

6. **config** - 配置层
   - default_skill_config.py - 默认配置
   - runtime_modes.py - 运行模式
   - feature_flags.py - 功能开关

### 三种运行模式

| 模式 | 说明 | 依赖 |
|------|------|------|
| Skill Default | 默认，零配置 | 无 |
| Platform Enhanced | 平台增强 | 小艺/鸿蒙 |
| Self-hosted Enhanced | 自托管增强 | PostgreSQL/Redis |

### 降级策略

- 平台不可用 → 自动降级到默认模式
- 所有降级都有记录和通知
- 保证基本功能始终可用

## 新增文档

1. SKILL_PRODUCT_ARCHITECTURE.md
2. SKILL_RUNTIME_MODES.md
3. PLATFORM_ENHANCED_SKILL_ARCHITECTURE.md
4. PLATFORM_CAPABILITY_MAPPING.md
5. RUNTIME_ASSUMPTIONS.md
6. DEGRADATION_STRATEGY.md
7. CAPABILITY_MATRIX.md
8. DEFAULT_SKILL_CONFIG.md
9. SKILL_LIMITATIONS_AND_DEGRADATION.md
10. RELEASE_NOTES_SKILL_REFACTOR.md

## 废弃内容

- 不再将 PostgreSQL 作为默认要求
- 不再将 Redis 作为默认要求
- 不再将 Docker 作为默认要求
- 不再将 message_server/task_daemon 作为必须常驻

## 兼容性

- 现有 infrastructure/ 和 domain/ 目录保持不变
- 现有 API 保持兼容
- 现有数据库结构保持兼容

## 下一步

- [ ] 完善小艺平台适配器
- [ ] 添加更多能力实现
- [ ] 完善测试覆盖
- [ ] 性能优化
