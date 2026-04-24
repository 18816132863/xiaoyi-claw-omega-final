# 运维中心使用指南 V1.0

## 一、快速开始

```bash
# 查看总状态
python scripts/ops_center.py status

# 运行门禁
python scripts/ops_center.py verify premerge
python scripts/ops_center.py verify nightly
python scripts/ops_center.py verify release

# 管理 incidents
python scripts/ops_center.py incidents list
python scripts/ops_center.py incidents list open
python scripts/ops_center.py incidents ack INC-xxx owner
python scripts/ops_center.py incidents resolve INC-xxx "修复说明"

# 查看告警
python scripts/ops_center.py alerts latest
python scripts/ops_center.py alerts history
python scripts/ops_center.py alerts notifications

# 构建看板
python scripts/ops_center.py dashboard build

# 打包证据
python scripts/ops_center.py bundle
```

## 二、命令详解

### 2.1 status - 查看总状态

显示当前系统总状态，包括：
- 总体状态（健康/警告/阻塞/降级）
- 各模块状态（Runtime/Quality/Release）
- 告警统计
- Incident 统计
- 文件路径

### 2.2 verify - 运行门禁

| Profile | 说明 |
|---------|------|
| premerge | PR 合并前检查 |
| nightly | 每日巡检 |
| release | 发布前检查 |

### 2.3 incidents - 管理 Incidents

| 操作 | 说明 |
|------|------|
| list | 列出所有 incidents |
| list open | 只列出打开的 |
| ack | 确认 incident |
| resolve | 关闭 incident |
| annotate | 添加备注 |

### 2.4 alerts - 查看告警

| 操作 | 说明 |
|------|------|
| latest | 最新告警 |
| history | 历史记录 |
| notifications | 通知结果 |

### 2.5 dashboard - 构建看板

生成运维看板（JSON/MD/HTML）

### 2.6 bundle - 打包证据

打包所有运维证据，用于：
- 故障排查
- 值守交接
- 人工升级处理

## 三、证据包内容

bundle 包含以下文件：

```
ops_bundle_{timestamp}.zip
├── reports/
│   ├── runtime_integrity.json
│   ├── quality_gate.json
│   ├── release_gate.json
│   ├── nightly_audit.json
│   ├── alerts/
│   │   ├── latest_alerts.json
│   │   ├── incident_summary.json
│   │   └── notification_result.json
│   ├── dashboard/
│   │   ├── ops_dashboard.json
│   │   └── ops_dashboard.md
│   └── trends/
│       └── gate_trend.json
├── governance/ops/
│   └── incident_tracker.json
└── ops_state.json
```

## 四、统一状态对象

`ops_state.json` 包含：

| 字段 | 说明 |
|------|------|
| overall_status | 总体状态 |
| runtime_status | Runtime 状态 |
| quality_status | Quality 状态 |
| can_release | 是否可发布 |
| blocking_alerts | 阻塞告警数 |
| warning_alerts | 警告告警数 |
| open_incidents | 打开的 incident 数 |
| latest_bundle_path | 最新证据包路径 |

## 五、何时使用

| 场景 | 命令 |
|------|------|
| 每日检查 | `ops_center.py status` |
| 收到告警 | `ops_center.py alerts latest` |
| 处理 incident | `ops_center.py incidents ack/resolve` |
| 故障排查 | `ops_center.py bundle` |
| 交接文档 | 发送 bundle 文件 |

## 六、文件路径

| 文件 | 路径 |
|------|------|
| 统一状态 | reports/ops/ops_state.json |
| 证据包 | reports/bundles/ops_bundle_*.zip |
| 看板 | reports/dashboard/ops_dashboard.* |
| 告警 | reports/alerts/latest_alerts.json |
| Incidents | governance/ops/incident_tracker.json |

---

**版本**: V1.0  
**更新时间**: 2026-04-12
