# 最终交付模式矩阵

## 版本
- V8.4.0 最终交付版
- 日期: 2026-04-24

## 一、运行模式

### 1.1 演示模式

**用途**: 展示功能、测试验证

**特点**:
- 数据由 `seed_platform_invocations.py` 生成
- 固定的标准数据集（100 条记录）
- NOTIFICATION 授权通常为 `not_configured`
- 所有报告输出基于演示数据

**启动方式**:
```bash
python scripts/demo_bootstrap.py
```

**预期输出**:
- 总调用数: 100
- completed: 60
- failed: 12
- timeout: 8
- result_uncertain: 10
- auth_required: 5
- queued_for_delivery: 5

### 1.2 真实运行模式

**用途**: 生产环境、实际使用

**特点**:
- 数据来自实际平台调用
- 记录数随使用增长
- NOTIFICATION 授权需配置
- 报告反映真实状态

**启动方式**:
```bash
# 配置授权
export XIAOYI_AUTH_CODE="your_auth_code"

# 正常使用
# 数据会自动记录到 platform_invocations
```

### 1.3 真实授权模式

**用途**: 解锁 NOTIFICATION 能力

**特点**:
- authCode 已配置且有效
- NOTIFICATION 能力可用
- 授权状态为 `configured`

**配置方式**:
```bash
# 方式 1: 环境变量
export XIAOYI_AUTH_CODE="your_auth_code"

# 方式 2: 配置文件
echo '{"auth_code": "your_auth_code"}' > config/xiaoyi_config.json
```

## 二、状态定义

### 2.1 平台调用状态

| 状态 | 说明 | 用户消息 |
|------|------|----------|
| completed | 成功完成 | "已完成" |
| failed | 执行失败 | "操作失败，请稍后重试" |
| timeout | 请求超时 | "请求超时，请检查实际结果" |
| result_uncertain | 结果不确定 | "结果不确定，请检查实际结果" |
| auth_required | 需要授权 | "需要授权才能使用此功能" |
| queued_for_delivery | 等待处理 | "已提交等待处理" |

### 2.2 确认状态

| 状态 | 说明 |
|------|------|
| confirmed_success | 确认成功 |
| confirmed_failed | 确认失败 |
| confirmed_duplicate | 确认重复 |

### 2.3 NOTIFICATION 授权状态

| 状态 | 说明 | 后续动作 |
|------|------|----------|
| configured | 已配置且有效 | 无需操作 |
| not_configured | 未配置 | 需要配置 |
| invalid | 已配置但无效 | 需要更新 |

## 三、错误码定义

| 错误码 | 说明 | 分类 |
|--------|------|------|
| PLATFORM_TIMEOUT | 请求超时 | 超时 |
| PLATFORM_RESULT_UNCERTAIN | 结果不确定 | 不确定 |
| PLATFORM_AUTH_REQUIRED | 需要授权 | 授权 |
| PLATFORM_EXECUTION_FAILED | 执行失败 | 失败 |
| PLATFORM_INVALID_PARAMS | 参数错误 | 失败 |
| PLATFORM_RATE_LIMITED | 请求过快 | 失败 |

## 四、报告口径

### 4.1 统一口径

所有报告（CLI stats、health_check、daily_report、weekly_report）使用相同的统计逻辑：

- **总调用数**: `COUNT(*)`
- **Uncertain 数**: `COUNT(*) WHERE result_uncertain = 1`
- **已确认数**: `COUNT(*) WHERE confirmed_status IS NOT NULL`
- **失败率**: `failed / total * 100`
- **超时率**: `timeout / total * 100`
- **确认率**: `confirmed / uncertain * 100`

### 4.2 数据一致性保证

1. 所有报告从同一数据库读取
2. 统计函数共用
3. 时间范围一致（日报：当天，周报：本周）

## 五、交付物清单

| # | 项目 | 说明 |
|---|------|------|
| 1 | 压缩包 | `workspace_v8.4.0_final_delivery.tar.gz` |
| 2 | 报告 | `FINAL_OPERATIONS_AND_DEMO_REPORT.txt` |
| 3 | 快速入门 | `DEMO_QUICKSTART.md` |
| 4 | 模式矩阵 | `FINAL_DELIVERY_MODE_MATRIX.md` |
| 5 | 测试输出 | 全量 pytest -q 原始输出 |
| 6 | 演示输出 | demo_bootstrap 原始输出 |
| 7 | 一键演示 | demo_run_all 原始输出 |
| 8 | 健康巡检 | health_check 原始输出 |
| 9 | 日报 | JSON / CSV 样例 |
| 10 | 周报 | JSON / CSV 样例 |
| 11 | 授权检查 | 三态样例 |
| 12 | 错误码统计 | breakdown 输出 |

## 六、验收标准

| 标准 | 要求 |
|------|------|
| 全量测试 | pytest -q 全绿 |
| 演示数据 | seed 后 100 条记录 |
| 统计一致 | CLI/health/report 数字一致 |
| 授权闭环 | 三态检查可用 |
| 一键演示 | demo_run_all.sh 可跑通 |
| 文档一致 | 文档与实际输出一致 |
