# 能力性能报告

## 一、Benchmark 结果

### 1.1 测试配置

- 迭代次数: 10 次/能力
- 模式: dry_run

### 1.2 四大能力性能

| 能力 | 平均延迟 | P95 延迟 | 成功率 |
|------|---------|---------|--------|
| MESSAGE_SENDING | ~50ms | ~100ms | 100% |
| TASK_SCHEDULING | ~30ms | ~60ms | 100% |
| STORAGE | ~20ms | ~40ms | 100% |
| NOTIFICATION | ~40ms | ~80ms | 100% |

---

## 二、Timeout 配置

**配置文件**: `config/capability_timeouts.json`

| 能力 | Timeout | 重试次数 | 说明 |
|------|---------|---------|------|
| MESSAGE_SENDING | 30s | 0 | 短信发送 |
| TASK_SCHEDULING | 60s | 0 | 日程调度 |
| STORAGE | 30s | 0 | 存储 |
| NOTIFICATION | 30s | 0 | 通知推送 |
| query_* | 10-15s | 1 | 查询类 |
| update_* | 30s | 0 | 更新类 |
| delete_* | 30s | 0 | 删除类 |

---

## 三、性能监控

### 3.1 导出性能报告

```bash
python scripts/export_capability_performance_report.py
```

**输出内容**:
- 按能力统计的成功率/超时率
- Top 错误码
- Top 慢调用
- 最慢调用样本

### 3.2 Benchmark 脚本

```bash
python scripts/benchmark_capabilities.py --iterations 10 --dry-run
```

### 3.3 压测脚本

```bash
python scripts/stress_capabilities.py --duration 10 --rps 5 --dry-run
```

---

## 四、性能指标

### 4.1 按能力统计

| 指标 | 说明 |
|------|------|
| total | 总调用数 |
| success | 成功数 |
| failed | 失败数 |
| timeout | 超时数 |
| uncertain | 不确定数 |
| success_rate | 成功率 |
| timeout_rate | 超时率 |

### 4.2 错误码统计

| 错误码 | 说明 |
|--------|------|
| PLATFORM_TIMEOUT | 平台超时 |
| PLATFORM_RESULT_UNCERTAIN | 结果不确定 |
| PLATFORM_AUTH_REQUIRED | 需要授权 |
| PLATFORM_EXECUTION_FAILED | 执行失败 |

---

## 五、重放与诊断

### 5.1 重放最慢调用

```python
from capabilities.replay_run import replay_slowest

result = replay_slowest(capability="MESSAGE_SENDING", limit=10)
```

### 5.2 重放失败样例

```python
from capabilities.replay_run import replay_failed

result = replay_failed(capability="MESSAGE_SENDING", limit=10)
```

---

## 六、压测结果示例

```json
{
  "MESSAGE_SENDING": {
    "total_requests": 50,
    "successes": 50,
    "failures": 0,
    "success_rate": 100.0,
    "avg_latency_ms": 45.2,
    "actual_rps": 5.0
  }
}
```
