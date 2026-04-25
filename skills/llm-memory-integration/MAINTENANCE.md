# 维护指南

## 手动维护任务

**重要提示**：所有维护任务都需要用户手动执行，没有自动定时任务。

### 维护任务列表

| 任务 | 说明 | 脚本 |
|------|------|------|
| 完整维护 | 检查覆盖率、清理孤立向量、优化数据库 | `run_maintenance.py` |
| 覆盖率检查 | 检查向量覆盖率 | `check_coverage.py` |
| FTS 重建 | 重建全文搜索索引 | `rebuild_fts.py` |
| 向量优化 | VACUUM、重建索引、清理孤立向量 | `vector_system_optimizer.py` |

## 手动执行

```bash
# 完整维护（推荐每周执行一次）
python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/run_maintenance.py

# 检查覆盖率（推荐每日执行一次）
python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/check_coverage.py

# 重建 FTS（当搜索失效时执行）
python3 ~/.openclaw/workspace/skills/llm-memory-integration/scripts/rebuild_fts.py

# 向量系统优化（当数据库过大时执行）
python3 ~/.openclaw/workspace/skills/llm-memory-integration/src/scripts/vector_system_optimizer.py status
python3 ~/.openclaw/workspace/skills/llm-memory-integration/src/scripts/vector_system_optimizer.py run
```

## 监控阈值

| 指标 | 阈值 | 说明 |
|------|------|------|
| L1 覆盖率 | ≥ 95% | 结构化记忆向量覆盖 |
| L0 覆盖率 | ≥ 60% | 原始对话向量覆盖 |
| 数据库大小 | < 100 MB | 定期清理 |
| 零向量 | < 5 条 | 需要修复 |

## 日志位置

- 维护日志: `~/.openclaw/memory-tdai/.metadata/maintenance.log`
- 推送记录: `~/.openclaw/workspace/skills/today-task/push_records/`

## 故障排查

### 覆盖率下降
1. 检查向量 API 是否正常
2. 运行 `optimize_vector_system.py` 修复
3. 检查 memory-tencentdb 插件状态

### 数据库过大
1. 运行 VACUUM 清理
2. 检查是否有孤立向量
3. 考虑归档旧数据

### FTS 搜索失效
1. 运行 `rebuild_fts.py` 重建索引
2. 检查 FTS 表是否存在
3. 验证分词器配置

## ⚠️ 重要声明

- **无自动定时任务**：所有维护任务都需要用户手动执行
- **无后台守护进程**：没有自动运行的后台进程
- **无自动修复**：所有修复操作都需要用户确认
