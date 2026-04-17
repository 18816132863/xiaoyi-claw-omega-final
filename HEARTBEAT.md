# HEARTBEAT.md - 心跳任务

此文件定义定期执行的任务。

## 心跳触发

当收到心跳提示时，执行：

```bash
python scripts/heartbeat_executor.py
```

## 心跳任务列表

| 任务 | 说明 | 超时 |
|------|------|------|
| 自动 Git 同步 | 提交并推送变更 | 60s |
| 永久守护器刷新 | 刷新关键模块状态 | 60s |
| Metrics 生成 | 生成最新指标 | 60s |
| 快速巡检 | 架构快速巡检 | 120s |
| 自动备份上传 | 自动提交推送变更 | 60s |

## 心跳间隔

- 默认: 30 分钟
- 可通过配置调整

## 手动执行

```bash
# 执行所有心跳任务
python scripts/heartbeat_executor.py

# 单独执行某个任务
python infrastructure/auto_git.py sync "手动提交"
python scripts/permanent_keeper.py --refresh
python scripts/generate_metrics.py
```

## 注意事项

- 心跳会自动提交变更到 GitHub
- 如无变更则跳过提交
- 任务失败不影响其他任务
- 报告保存在 `reports/ops/heartbeat_report.json`

## 回复规则

- 所有任务成功: 回复 `HEARTBEAT_OK`
- 部分任务失败: 回复失败详情
- 无需处理: 回复 `HEARTBEAT_OK`
