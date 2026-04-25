# 定时任务执行机制说明

## 📊 当前状态

**检查时间**: 2026-04-19 08:44
**问题**: 定时任务没有自动执行

---

## 🔍 问题分析

### 1. 心跳任务需要外部触发

**当前机制**:
- 心跳任务定义在 `HEARTBEAT.md`
- 需要外部系统定期触发 `python scripts/heartbeat_executor.py`
- **OpenClaw 本身不会自动触发心跳**

**触发方式**:
1. **手动触发**: `python scripts/heartbeat_executor.py`
2. **Cron 定时任务**: 在系统 crontab 中配置
3. **Systemd 服务**: 创建 systemd timer
4. **外部调度器**: 使用外部调度系统

---

### 2. 定时任务触发窗口

**当前时间**: 08:44

**今日定时任务**:

| 时间 | 任务 | 触发窗口 | 当前状态 |
|------|------|----------|----------|
| 00:00 | 会话清理 | 00:00-00:29 | ❌ 已过 |
| 00:30 | 缓存清理 | 00:30-00:59 | ❌ 已过 |
| 01:00 | 备份清理 | 01:00-01:29 | ❌ 已过 |
| 02:00 | 夜间巡检 | 02:00-02:29 | ❌ 已过 |
| 03:00 | 报告清理 | 03:00-03:29 | ❌ 已过 |
| 04:00 | 控制平面审计 | 04:00-04:29 | ❌ 已过 |
| 05:00 | JSON 契约检查 | 05:00-05:29 | ❌ 已过 |
| 06:00 | 持续改进 | 06:00-06:29 | ❌ 已过 |
| 07:00 | 异常管理 | 07:00-07:29 | ❌ 已过 |
| 08:00 | AI API 检查 | 08:00-08:29 | ❌ 已过 |
| **09:00** | **健康提醒** | **09:00-09:29** | ⏳ **等待中** |
| 12:00 | 中午检查 | 12:00-12:29 | ⏳ 等待中 |
| 18:00 | 工作总结 | 18:00-18:29 | ⏳ 等待中 |
| 21:00 | 晚间复盘 | 21:00-21:29 | ⏳ 等待中 |
| 22:00 | 系统健康报告 | 22:00-22:29 | ⏳ 等待中 |
| 23:00 | 技能使用统计 | 23:00-23:29 | ⏳ 等待中 |

**结论**: 
- 早上 00:00-08:29 的任务都已错过
- 下一个触发窗口是 09:00-09:29（健康提醒）

---

## 💡 解决方案

### 方案 1: 手动触发（临时）

```bash
# 手动执行心跳
python scripts/heartbeat_executor.py

# 手动执行特定任务
python scripts/send_daily_health_reminder.py
python scripts/generate_daily_work_summary.py
```

---

### 方案 2: 配置 Cron 定时任务（推荐）

**创建 crontab**:
```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每 15 分钟执行一次心跳）
*/15 * * * * cd /home/sandbox/.openclaw/workspace && /usr/bin/python3 scripts/heartbeat_executor.py >> /tmp/heartbeat.log 2>&1
```

**验证**:
```bash
# 查看当前 crontab
crontab -l

# 查看日志
tail -f /tmp/heartbeat.log
```

---

### 方案 3: 创建 Systemd 服务（推荐）

**创建服务文件** `/etc/systemd/system/openclaw-heartbeat.service`:
```ini
[Unit]
Description=OpenClaw Heartbeat Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /home/sandbox/.openclaw/workspace/scripts/heartbeat_executor.py
WorkingDirectory=/home/sandbox/.openclaw/workspace
User=sandbox
Environment=PATH=/usr/bin:/usr/local/bin

[Install]
WantedBy=multi-user.target
```

**创建定时器** `/etc/systemd/system/openclaw-heartbeat.timer`:
```ini
[Unit]
Description=OpenClaw Heartbeat Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
Unit=openclaw-heartbeat.service

[Install]
WantedBy=timers.target
```

**启用服务**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable openclaw-heartbeat.timer
sudo systemctl start openclaw-heartbeat.timer

# 查看状态
sudo systemctl status openclaw-heartbeat.timer
sudo systemctl list-timers
```

---

### 方案 4: 使用守护进程（已实现）

**脚本**: `infrastructure/daemon_manager.py`

**启动守护进程**:
```bash
# 启动
python infrastructure/daemon_manager.py start

# 停止
python infrastructure/daemon_manager.py stop

# 状态
python infrastructure/daemon_manager.py status
```

---

## 🎯 推荐方案

### 对于生产环境
- ✅ **Systemd Timer** - 最稳定，开机自启
- ✅ **Cron** - 简单可靠

### 对于开发环境
- ✅ **守护进程** - 灵活可控
- ✅ **手动触发** - 调试方便

---

## 📋 立即行动

### 1. 手动执行今日错过的任务

```bash
# 执行健康提醒（虽然时间不对，但可以手动执行）
python scripts/send_daily_health_reminder.py

# 执行日引导检查
python scripts/run_daily_growth_check.py
```

### 2. 配置自动触发

选择以下任一方案：
- [ ] 配置 Cron
- [ ] 配置 Systemd
- [ ] 启动守护进程

---

## 📊 预期效果

配置自动触发后：
- ✅ 每 15 分钟自动执行心跳
- ✅ 定时任务按时触发
- ✅ 无需手动干预
- ✅ 系统自动运行

---

**更新时间**: 2026-04-19 08:45
**版本**: V1.0.0
