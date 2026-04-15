# 发布证据策略 V1.0.0

## 概述

定义发布证据包的内容、格式和使用方式。

---

## 一、证据包内容

### 必须包含的证据

| 文件 | 说明 |
|------|------|
| `reports/runtime_integrity.json` | 运行时门禁报告 |
| `reports/quality_gate.json` | 质量门禁报告 |
| `reports/release_gate.json` | 发布门禁报告 |
| `reports/ops/rule_engine_report.json` | 规则引擎报告 |
| `reports/ops/rule_execution_index.json` | 规则执行索引 |
| `reports/ops/rule_registry_snapshot.json` | 规则注册表快照 |
| `reports/ops/rule_exception_status.json` | 例外状态快照 |
| `reports/ops/rule_exception_debt.json` | 例外债务快照 |
| `reports/ops/rule_exception_history.json` | 例外操作历史 |
| `reports/ops/control_plane_state.json` | 控制平面状态 |
| `reports/ops/control_plane_audit.json` | 控制平面审计 |
| `reports/ops/exception_approval_queue.json` | 例外审批队列 |

### 清单文件

每个证据包包含 `manifest.json`，记录：
- 生成时间
- 包含文件列表
- 缺失文件列表
- 总文件数

---

## 二、证据包格式

### 文件名格式

```
release_evidence_<timestamp>.zip
```

示例：`release_evidence_20260415_132106.zip`

### 存放位置

```
reports/bundles/
```

---

## 三、生成时机

### 自动生成

- release 门禁通过后自动生成
- 包含所有门禁证据

### 手动生成

```bash
python infrastructure/release/release_manager.py --bundle
```

---

## 四、审计用途

### 反向审计

通过证据包可以追溯：
1. 发布时的门禁状态
2. 规则执行结果
3. 例外状态
4. 审批记录

### 保留期限

- 证据包保留 90 天
- 可配置更长保留期

---

## 五、使用示例

### 生成证据包

```bash
$ python infrastructure/release/release_manager.py --bundle
{
  "status": "success",
  "bundle_path": "reports/bundles/release_evidence_20260415_132106.zip",
  "included_count": 12,
  "missing_count": 0
}
```

### 解压查看

```bash
$ unzip release_evidence_20260415_132106.zip -d evidence/
$ cat evidence/manifest.json
```

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-15
