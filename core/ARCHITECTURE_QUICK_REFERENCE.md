# 架构快速参考卡片 V2.0.0

> **每次处理任务前，必须阅读此卡片**
> 
> **版本**: V2.0.0 - R010 规则增强版
> **强制**: 所有任务必须记录执行轨迹

---

## 🚨 强制要求

**每个任务必须**：
1. ✅ 调用 `start_task()` 开始任务
2. ✅ 按顺序标记各层完成
3. ✅ 调用 `end_task()` 结束任务
4. ✅ 输出执行轨迹到 `reports/ops/task_trace_*.json`

**违规后果**：
- CRITICAL: 立即终止任务
- HIGH: 警告并补充执行
- MEDIUM: 警告并修正
- LOW: 记录违规

---

## 🎯 标准流程（必须按顺序执行）

```
1️⃣ L1 Core      → 读取规则文件
2️⃣ L2 Memory    → 搜索相关记忆
3️⃣ L3 Orch      → 编排任务
4️⃣ L4 Exec      → 执行技能
5️⃣ L5 Gov       → 验证结果
6️⃣ L6 Infra     → 调用工具
```

---

## 📋 每步必做

### 1️⃣ L1 Core - 读取规则

**必须读取**：
- `core/ARCHITECTURE.md`
- `core/LAYER_DEPENDENCY_MATRIX.md`
- `core/SINGLE_SOURCE_OF_TRUTH.md`

**目的**：了解架构约束和依赖规则

---

### 2️⃣ L2 Memory - 搜索记忆

**必须调用**：
```python
memory_search(query="...")
```

**目的**：获取相关上下文和历史经验

---

### 3️⃣ L3 Orchestration - 编排任务

**必须调用**：
```python
TaskEngine.process(user_input)
TaskDistributor.distribute(task)
SkillRouter.select_skill(query)
```

**目的**：解析任务、分配子任务、选择技能

---

### 4️⃣ L4 Execution - 执行技能

**必须调用**：
```python
SkillGateway.execute(skill_id, inputs)
```

**目的**：执行具体技能，返回结果

---

### 5️⃣ L5 Governance - 验证结果

**必须调用**：
```python
Validator.validate_result(result)
Auditor.audit_execution(trace)
```

**目的**：验证结果正确性，记录审计日志

---

### 6️⃣ L6 Infrastructure - 调用工具

**最后调用**：
```python
# 具体工具调用
```

**目的**：执行底层操作

---

## ❌ 禁止行为

| 禁止 | 原因 |
|------|------|
| ❌ 跳过任何层级 | 违反架构流程 |
| ❌ 直接调用工具 | 绕过编排层 |
| ❌ 直接读取脚本 | 违反依赖规则 |
| ❌ 返回非契约格式 | 违反 IO 契约 |

---

## ✅ 自检清单

**回复前必须确认**：

- [ ] 1. 已读取 L1 Core 规则
- [ ] 2. 已搜索 L2 Memory
- [ ] 3. 已调用 L3 Orchestration
- [ ] 4. 已执行 L4 Execution
- [ ] 5. 已验证 L5 Governance
- [ ] 6. 已调用 L6 Infrastructure
- [ ] 7. 结果符合 IO 契约
- [ ] 8. 已记录执行轨迹

**如有任何 ❌，必须立即修正！**

---

## 📊 执行轨迹模板

```json
{
  "task_id": "task_xxx",
  "layers": {
    "L1_core": {"status": "completed"},
    "L2_memory": {"status": "completed"},
    "L3_orchestration": {"status": "completed"},
    "L4_execution": {"status": "completed"},
    "L5_governance": {"status": "completed"},
    "L6_infrastructure": {"status": "completed"}
  },
  "compliant": true
}
```

---

## 🔧 快速工具

```bash
# 检查合规性
python scripts/architecture_compliance_checker.py --check

# 生成报告
python scripts/architecture_compliance_checker.py --report
```

---

**记住**：架构是强制性的，不是可选的！
