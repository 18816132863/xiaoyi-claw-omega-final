# 演示快速入门

## 版本
- V8.4.0 最终交付版
- 日期: 2026-04-24

## 一、3 分钟快速演示

### 步骤 1: 初始化演示环境

```bash
python scripts/demo_bootstrap.py
```

**预期输出**:
- 数据库初始化完成
- 演示数据预热完成（100 条记录）
- NOTIFICATION 授权状态检查
- 统计信息显示

### 步骤 2: 查看统计

```bash
python scripts/invocation_audit_cli.py stats
```

**预期输出**:
```
==================================================
平台调用审计统计
==================================================
总调用数: 100
Uncertain 记录: 18
已确认记录: 9

按状态分布:
  completed: 60 (60.0%)
  failed: 12 (12.0%)
  timeout: 8 (8.0%)
  result_uncertain: 10 (10.0%)
  auth_required: 5 (5.0%)
  queued_for_delivery: 5 (5.0%)
```

### 步骤 3: 查看健康状态

```bash
python scripts/platform_health_check.py
```

**预期输出**:
- 总调用数: 100
- 失败率: 12.00%
- 超时率: 8.00%
- NOTIFICATION 授权状态

### 步骤 4: 导出报告

```bash
# 日报 JSON
python scripts/export_daily_platform_report.py --format json

# 日报 CSV
python scripts/export_daily_platform_report.py --format csv --output daily_report.csv

# 周报 JSON
python scripts/export_weekly_platform_report.py --format json
```

### 步骤 5: 一键运行所有演示

```bash
bash scripts/demo_run_all.sh
```

## 二、演示数据说明

### 2.1 标准演示数据集

运行 `seed_platform_invocations.py --preset demo_standard` 后生成的数据：

| 状态 | 数量 | 说明 |
|------|------|------|
| completed | 60 | 成功完成 |
| failed | 12 | 执行失败 |
| timeout | 8 | 请求超时 |
| result_uncertain | 10 | 结果不确定 |
| auth_required | 5 | 需要授权 |
| queued_for_delivery | 5 | 等待处理 |
| **总计** | **100** | |

### 2.2 确认状态分布

| 确认状态 | 数量 | 说明 |
|----------|------|------|
| confirmed_success | 6 | 确认成功 |
| confirmed_failed | 2 | 确认失败 |
| confirmed_duplicate | 1 | 确认重复 |
| **已确认总计** | **9** | |

### 2.3 能力分布

| 能力 | 数量 |
|------|------|
| MESSAGE_SENDING | 25 |
| TASK_SCHEDULING | 20 |
| STORAGE | 10 |
| NOTIFICATION | 5 |

## 三、常见失败排查

### Q1: 数据库不存在

**现象**: 运行脚本时报 "数据库不存在"

**解决**:
```bash
python scripts/seed_platform_invocations.py --preset demo_standard --reset-before-seed
```

### Q2: 统计数字为 0

**现象**: stats 显示总调用数为 0

**解决**:
```bash
# 重置并重新预热
python scripts/seed_platform_invocations.py --preset demo_standard --reset-before-seed
```

### Q3: NOTIFICATION 显示 not_configured

**现象**: 授权状态显示 not_configured

**说明**: 这是正常的演示状态。如需配置，请参考 `NOTIFICATION_AUTH_GUIDE.md`。

### Q4: 健康巡检返回非零退出码

**现象**: health_check 返回退出码 1

**说明**: 这是正常的，表示有警告（如失败率过高、授权未配置）。

## 四、演示模式 vs 真实运行

| 模式 | 数据来源 | 授权状态 | 说明 |
|------|----------|----------|------|
| 演示模式 | seed 脚本生成 | 通常 not_configured | 用于展示功能 |
| 真实运行 | 实际平台调用 | 需配置 authCode | 用于生产环境 |

## 五、下一步

1. 查看 `PLATFORM_AUDIT_OPERATIONS.md` 了解审计操作
2. 查看 `NOTIFICATION_AUTH_GUIDE.md` 配置授权
3. 查看 `PLATFORM_HEALTH_CHECK.md` 了解健康巡检
