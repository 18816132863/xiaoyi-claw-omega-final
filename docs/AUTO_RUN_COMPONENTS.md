# 自动运行组件清单 V7.2.0

> 架构中所有需要自动运行的组件及其状态

---

## 一、自动运行组件清单

| 组件 | 文件 | 触发条件 | 当前状态 | 优先级 |
|------|------|----------|----------|--------|
| 融合引擎 | `infrastructure/fusion_engine.py` | git commit 前 | ✅ 已自动 | P0 |
| 自动 Git 同步 | `infrastructure/auto_git.py` | 心跳 (30分钟) | ✅ 已自动 | P0 |
| 永久守护器 | `scripts/permanent_keeper.py` | 心跳 (5分钟) | ✅ 已自动 | P0 |
| 智能调度器 | `infrastructure/automation/smart_scheduler.py` | 后台服务 | ✅ 已自动 | P1 |
| 自动优化器 | `infrastructure/optimization/auto_optimizer.py` | 性能下降时 | ⚠️ 手动 | P1 |
| 架构巡检器 | `scripts/unified_inspector_v7.py` | 心跳 / CI | ✅ 已自动 | P0 |
| 规则引擎 | `scripts/run_rule_engine.py` | pre-merge | ⚠️ 手动 | P0 |
| 技能分类器 | `scripts/auto_classify_skills.py` | 新增技能时 | ⚠️ 手动 | P1 |
| Metrics 生成器 | `scripts/generate_metrics.py` | 心跳 (60分钟) | ✅ 已自动 | P1 |
| 事件触发器 | `infrastructure/automation/event_trigger.py` | 事件发生时 | ⚠️ 手动 | P1 |
| 任务自动化器 | `infrastructure/automation/task_automator.py` | 任务队列 | ⚠️ 手动 | P1 |
| 流水线执行器 | `infrastructure/automation/pipeline_executor.py` | 流水线触发 | ⚠️ 手动 | P1 |
| **守护进程管理器** | `infrastructure/daemon_manager.py` | 后台持续运行 | ✅ 已创建 | P0 |

---

## 二、守护进程管理器

### 2.1 守护服务列表

| 服务 | 间隔 | 说明 |
|------|------|------|
| 心跳执行器 | 30分钟 | 执行心跳任务 |
| 永久守护器 | 5分钟 | 刷新关键模块 |
| Metrics 生成器 | 60分钟 | 生成指标报告 |
| 融合检查器 | 10分钟 | 检查架构融合 |

### 2.2 使用方式

```bash
# 启动守护进程
./scripts/daemon.sh start

# 停止守护进程
./scripts/daemon.sh stop

# 查看状态
./scripts/daemon.sh status

# 重启守护进程
./scripts/daemon.sh restart

# 安装为 systemd 服务（开机自启）
./scripts/daemon.sh install-systemd
```

### 2.3 systemd 服务

```bash
# 安装后使用
sudo systemctl start openclaw-daemon    # 启动
sudo systemctl stop openclaw-daemon     # 停止
sudo systemctl status openclaw-daemon   # 状态
sudo systemctl enable openclaw-daemon   # 开机自启
```

---

## 三、自动运行机制

### 3.1 Git Hooks

```
.git/hooks/
├── pre-commit      # 提交前：融合检查
├── pre-push        # 推送前：快速巡检
└── post-merge      # 合并后：处理
```

### 3.2 守护进程

```
infrastructure/daemon_manager.py
    ├── 心跳执行器 (30分钟)
    ├── 永久守护器 (5分钟)
    ├── Metrics 生成器 (60分钟)
    └── 融合检查器 (10分钟)
```

### 3.3 心跳机制

```
HEARTBEAT.md 定义心跳任务
    ↓
每 30 分钟触发
    ↓
执行心跳任务列表
```

### 3.4 CI/CD 集成

```
.github/workflows/
├── pre-merge.yml   # 合并前检查
├── nightly.yml     # 每日巡检
└── release.yml     # 发布检查
```

---

## 四、自动运行状态

| 机制 | 状态 | 说明 |
|------|------|------|
| Git pre-commit | ✅ 已启用 | 融合检查 |
| Git pre-push | ✅ 已启用 | 快速巡检 |
| 守护进程管理器 | ✅ 已创建 | 后台持续运行 |
| 心跳执行器 | ✅ 已创建 | 定时任务 |
| systemd 服务 | ⚠️ 需安装 | 开机自启 |
