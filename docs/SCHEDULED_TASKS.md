# 定时任务与汇报机制配置

## 📋 当前定时任务列表

### 1. 心跳任务（每30分钟）

**触发方式**: HEARTBEAT.md 心跳提示

**任务列表**:

| 任务ID | 任务名称 | 说明 | 超时 | 状态 |
|--------|----------|------|------|------|
| auto_git | 自动 Git 同步 | 提交并推送变更 | 60s | ✅ 启用 |
| auto_backup | 自动备份上传 | 自动提交推送变更 | 60s | ✅ 启用 |
| auto_trigger | 自动触发器 | 检测场景并自动触发任务 | 120s | ✅ 启用 |
| permanent_keeper | 永久守护器刷新 | 刷新关键模块状态 | 60s | ✅ 启用 |
| metrics_generator | Metrics 生成 | 生成系统指标 | 60s | ⏸️ 禁用 |
| quick_inspection | 快速巡检 | 架构快速巡检 | 120s | ⏸️ 禁用 |

---

### 2. 自动触发场景

**触发方式**: auto_trigger.py 自动检测

| 场景ID | 场景名称 | 触发条件 | 触发任务 | 状态 |
|--------|----------|----------|----------|------|
| new_python_file | 新增 Python 文件 | 新增 .py 文件 | 技能安全检查 | ✅ 启用 |
| core_file_change | Core 文件变更 | 修改 core/ 文件 | 架构巡检 | ✅ 启用 |
| governance_file_change | Governance 文件变更 | 修改 governance/ 文件 | 规则检查 | ✅ 启用 |
| daily_first_start | 每日首次启动 | 每天首次运行 | 日引导检查 | ✅ 启用 |
| weekly_first_start | 每周首次启动 | 周一首次运行 | 周复盘 | ✅ 启用 |
| **daily_health_reminder** | **每日健康提醒** | **每天 09:00** | **健康提醒** | ✅ **新增** |
| **daily_work_summary** | **每日工作总结** | **每天 18:00** | **工作总结** | ✅ **新增** |
| **weekly_skill_report** | **每周技能报告** | **周一 09:00** | **技能报告** | ✅ **新增** |

---

### 3. 每日引导任务

**触发方式**: daily_first_start 自动触发

**执行脚本**: `scripts/run_daily_growth_check.py`

**时间阶段**:

| 阶段 | 时间范围 | 建议操作 |
|------|----------|----------|
| morning | 06:00 - 12:00 | 启动日引导 |
| midday | 12:00 - 14:00 | 中午检查 |
| afternoon | 14:00 - 18:00 | 继续工作 |
| evening | 18:00 - 23:00 | 晚间复盘 |
| night | 23:00 - 06:00 | 休息 |

**引导内容**:
- 今日状态概览
- 待办事项清单
- 工作建议
- 心情记录

---

### 4. 每周复盘任务

**触发方式**: weekly_first_start 自动触发（周一）

**执行脚本**: `scripts/run_weekly_growth_review.py`

**复盘内容**:
- 本周工作总结
- 目标完成情况
- 下周计划
- 经验教训

---

## 🔧 新增定时任务配置

### ✅ 已新增任务

#### 1. 每日健康提醒 ✅
```json
{
  "id": "daily_health_reminder",
  "name": "每日健康提醒",
  "trigger": "time:daily:09:00",
  "action": "send_health_reminder",
  "command": ["python", "scripts/send_daily_health_reminder.py"],
  "enabled": true,
  "status": "已实现"
}
```

**内容**:
- 睡眠质量提醒
- 运动目标提醒
- 饮水提醒
- 作息建议

**触发时间**: 每天 09:00

---

#### 2. 每日工作总结 ✅
```json
{
  "id": "daily_work_summary",
  "name": "每日工作总结",
  "trigger": "time:daily:18:00",
  "action": "generate_work_summary",
  "command": ["python", "scripts/generate_daily_work_summary.py"],
  "enabled": true,
  "status": "已实现"
}
```

**内容**:
- 今日完成情况
- 明日计划
- 问题与建议

**触发时间**: 每天 18:00

---

#### 3. 每周技能报告 ✅
```json
{
  "id": "weekly_skill_report",
  "name": "每周技能报告",
  "trigger": "time:weekly:monday:09:00",
  "action": "generate_skill_report",
  "command": ["python", "scripts/generate_weekly_skill_report.py"],
  "enabled": true,
  "status": "已实现"
}
```

**内容**:
- 技能使用统计
- 热门技能排行
- 新增技能介绍
- 优化建议

**触发时间**: 每周一 09:00

---

## 📊 定时任务执行流程

```
心跳触发 (每30分钟)
    ↓
heartbeat_executor.py
    ↓
├── auto_git.py (Git同步)
├── auto_backup_uploader.py (备份上传)
├── auto_trigger.py (自动触发器)
│   ├── 检查文件变更
│   ├── 检查时间触发
│   └── 执行对应任务
│       ├── run_daily_growth_check.py (日引导)
│       └── run_weekly_growth_review.py (周复盘)
├── permanent_keeper.py (守护器刷新)
└── generate_metrics.py (指标生成)
```

---

## 🎯 配置建议

### 1. 启用日引导
```bash
# 在 auto_trigger.py 中已配置
# 每日首次启动自动触发
python scripts/run_daily_growth_check.py
```

### 2. 启用周复盘
```bash
# 在 auto_trigger.py 中已配置
# 每周一自动触发
python scripts/run_weekly_growth_review.py
```

### 3. 手动触发
```bash
# 手动执行日引导
make daily-growth-personal

# 手动执行周复盘
make weekly-review

# 手动执行心跳
python scripts/heartbeat_executor.py
```

---

## 📝 日志与报告

### 日志位置
- 心跳报告: `reports/ops/heartbeat_report.json`
- 触发日志: `reports/ops/auto_trigger_log.jsonl`
- 日引导状态: `reports/live_loop/daily_state.json`

### 查看方式
```bash
# 查看心跳报告
cat reports/ops/heartbeat_report.json | jq .

# 查看触发日志
tail -f reports/ops/auto_trigger_log.jsonl

# 查看日引导状态
cat reports/live_loop/daily_state.json | jq .
```

---

**更新时间**: 2026-04-19 03:50
**版本**: V1.1.0

## ✅ 更新记录

### V1.1.0 (2026-04-19 03:50)
- ✅ 新增每日健康提醒脚本 (`scripts/send_daily_health_reminder.py`)
- ✅ 新增每日工作总结脚本 (`scripts/generate_daily_work_summary.py`)
- ✅ 新增每周技能报告脚本 (`scripts/generate_weekly_skill_report.py`)
- ✅ 更新自动触发器 (`scripts/auto_trigger.py`) 支持具体时间触发
- ✅ 所有新增任务已测试通过
