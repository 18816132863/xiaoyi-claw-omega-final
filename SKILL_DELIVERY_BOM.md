# 技能交付物清单 (BOM)

## 版本
- V8.4.0 最终发布版
- 日期: 2026-04-24

## 一、代码文件

### 1.1 脚本目录 (scripts/)

| 文件 | 说明 |
|------|------|
| seed_platform_invocations.py | 演示数据预热 |
| demo_bootstrap.py | 演示环境初始化 |
| demo_run_all.sh | 一键演示脚本 |
| invocation_audit_cli.py | 审计 CLI |
| platform_health_check.py | 健康巡检 |
| export_daily_platform_report.py | 日报导出 |
| export_weekly_platform_report.py | 周报导出 |
| check_notification_auth.py | 授权检查 |
| release_check.py | 发布检查 |
| skill_preflight_check.py | 技能上传前检查 |
| security_sanity_check.py | 安全检查 |
| package_release.py | 发布打包 |
| ci_local.sh | 本地 CI |
| run_daily_backup.sh | 每日备份 |
| run_weekly_cleanup.sh | 每周清理 |
| run_hourly_health_check.sh | 每小时巡检 |

### 1.2 平台适配器 (platform_adapter/)

| 文件 | 说明 |
|------|------|
| xiaoyi_adapter.py | 小艺平台适配器 |
| invoke_guard.py | 统一防护层 |
| result_normalizer.py | 结果归一化 |
| error_codes.py | 错误码定义 |
| user_messages.py | 用户消息 |
| invocation_ledger.py | 审计台账 |

### 1.3 能力目录 (capabilities/)

| 文件 | 说明 |
|------|------|
| audit_queries.py | 审计查询 |
| confirm_invocation.py | 手动确认 |
| explain_invocation_status.py | 状态解释 |

### 1.4 配置目录 (config/)

| 文件 | 说明 |
|------|------|
| crontab.example | Crontab 示例 |
| systemd.example | Systemd 示例 |

## 二、文档文件

### 2.1 根目录文档

| 文件 | 说明 |
|------|------|
| DEMO_QUICKSTART.md | 快速入门 |
| FINAL_DELIVERY_MODE_MATRIX.md | 运行模式 |
| NOTIFICATION_AUTH_GUIDE.md | 授权指南 |
| PLATFORM_HEALTH_CHECK.md | 健康巡检 |
| PLATFORM_AUDIT_OPERATIONS.md | 审计操作 |
| PLATFORM_EXPORT_AND_BACKUP.md | 导出备份 |
| MANUAL_CONFIRMATION_PLAYBOOK.md | 手动确认 |
| USER_RESULT_MESSAGE_MATRIX.md | 用户消息 |
| RELEASE_READINESS.md | 发布就绪 |
| SKILL_UPLOAD_CHECKLIST.md | 上传检查 |
| SKILL_DELIVERY_BOM.md | 交付物清单 |

### 2.2 核心文档

| 文件 | 说明 |
|------|------|
| AGENTS.md | Agent 配置 |
| SOUL.md | 身份定义 |
| USER.md | 用户信息 |
| IDENTITY.md | 身份信息 |
| TOOLS.md | 工具规范 |
| MEMORY.md | 长期记忆 |
| HEARTBEAT.md | 心跳任务 |

## 三、测试文件 (tests/)

| 文件 | 说明 |
|------|------|
| test_seed_invocations.py | 预热测试 |
| test_audit_cli.py | CLI 测试 |
| test_audit_queries.py | 查询测试 |
| test_manual_confirmation.py | 确认测试 |
| test_cleanup_policy.py | 清理测试 |
| test_user_result_matrix.py | 消息测试 |
| test_confirm_invocation_capability.py | 能力测试 |
| test_redact_export.py | 脱敏测试 |
| test_health_check.py | 巡检测试 |
| test_check_notification_auth.py | 授权测试 |
| test_platform_reports.py | 报告测试 |
| test_automation_scripts.py | 自动化测试 |
| test_extended_redaction.py | 扩展脱敏测试 |

## 四、数据库文件

| 文件 | 说明 |
|------|------|
| infrastructure/storage/migrations/002_platform_invocations.sql | 数据库迁移 |

## 五、排除文件

以下文件不包含在发布包中：

| 类型 | 文件/目录 |
|------|-----------|
| 缓存 | __pycache__/, .pytest_cache/, *.pyc |
| 依赖 | node_modules/, .venv/ |
| 版本控制 | .git/ |
| 日志 | logs/ |
| 备份 | backups/ |
| 输出 | demo_outputs/, reports/ |
| 临时 | *.tmp, *.log |

## 六、文件统计

| 类型 | 数量 |
|------|------|
| Python 脚本 | 16 |
| Shell 脚本 | 4 |
| Markdown 文档 | 15+ |
| 测试文件 | 13 |
| 配置文件 | 2 |

## 七、总大小

- 发布包大小: ~5 MB
- 解压后大小: ~15 MB
