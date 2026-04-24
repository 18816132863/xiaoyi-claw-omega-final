# 架构遵循强制机制 V2.0.0

> **唯一真源** - 确保所有任务处理严格按照六层架构流程
> 
> **版本**: V2.0.0 - 增强强制执行机制
> **规则**: R010 (RULE_REGISTRY.json)
> **状态**: active, blocking

---

## 零、强制执行机制

### 0.1 执行前强制检查

**每个任务开始前必须执行**：

```python
from scripts.architecture_compliance_checker import start_task, Layer

# 1. 开始任务
task_id = start_task()

# 2. 按顺序标记各层完成
mark_layer_completed(Layer.L1_CORE, files_read=["..."])
mark_layer_completed(Layer.L2_MEMORY, queries=["..."])
mark_layer_completed(Layer.L3_ORCHESTRATION, ...)
mark_layer_completed(Layer.L4_EXECUTION, ...)
mark_layer_completed(Layer.L5_GOVERNANCE, ...)
mark_layer_completed(Layer.L6_INFRASTRUCTURE, ...)

# 3. 结束任务并验证
trace = end_task()
assert trace.compliant, f"架构违规: {trace.violations}"
```

### 0.2 违规等级

| 等级 | 触发条件 | 处理方式 |
|------|----------|----------|
| **CRITICAL** | 跳过 L1 Core 规则读取 | 立即终止，重新开始 |
| **HIGH** | 跳过 L2 Memory 或 L3 Orchestration | 警告，补充执行 |
| **MEDIUM** | 跳过 L4/L5/L6 或违反 IO 契约 | 警告，修正格式 |
| **LOW** | 缺少执行轨迹 | 记录，补充轨迹 |

### 0.3 强制输出

**每个任务必须输出执行轨迹**：

```json
{
  "task_id": "task_xxx",
  "timestamp": "2026-04-20T08:58:00Z",
  "layers": {
    "L1_core": {"status": "completed", "files_read": [...]},
    "L2_memory": {"status": "completed", "queries": [...]},
    "L3_orchestration": {"status": "completed", ...},
    "L4_execution": {"status": "completed", ...},
    "L5_governance": {"status": "completed", ...},
    "L6_infrastructure": {"status": "completed", ...}
  },
  "compliant": true,
  "violations": []
}
```

---

## 一、强制流程

### 1.1 标准处理流程

**所有任务必须按照以下顺序处理**：

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: L1 Core - 读取规则                                  │
│  ├─ ARCHITECTURE.md (架构定义)                               │
│  ├─ LAYER_DEPENDENCY_MATRIX.md (依赖规则)                    │
│  ├─ LAYER_IO_CONTRACTS.md (IO 契约)                          │
│  └─ SINGLE_SOURCE_OF_TRUTH.md (真源清单)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: L2 Memory Context - 搜索记忆                        │
│  └─ memory_search(query) - 搜索相关记忆                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: L3 Orchestration - 任务编排                         │
│  ├─ TaskEngine.process() - 解析任务                          │
│  ├─ TaskDistributor.distribute() - 分配任务                  │
│  └─ SkillRouter.select_skill() - 选择技能                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: L4 Execution - 技能执行                             │
│  ├─ SkillGateway.execute() - 执行技能                        │
│  └─ 返回 ExecutionResult (符合 IO 契约)                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 5: L5 Governance - 结果验证                            │
│  ├─ Validator.validate_result() - 验证结果                   │
│  └─ Auditor.audit_execution() - 审计执行                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 6: L6 Infrastructure - 工具调用                        │
│  └─ 调用具体工具 (scripts/, infrastructure/)                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 禁止行为

| 禁止行为 | 原因 | 正确做法 |
|----------|------|----------|
| ❌ 跳过 L1 Core | 违反架构规则 | ✅ 先读规则文件 |
| ❌ 跳过 L2 Memory | 丢失上下文 | ✅ 先搜索记忆 |
| ❌ 直接调用工具 | 绕过编排层 | ✅ 通过 TaskEngine |
| ❌ 直接读取脚本 | 违反依赖规则 | ✅ 通过 SkillRouter |
| ❌ 返回不符合契约的结果 | 违反 IO 契约 | ✅ 返回标准格式 |

---

## 二、检查清单

### 2.1 任务开始前检查

```python
# ✅ 必须执行
def pre_task_check():
    checks = [
        ("L1 Core 规则已读取", has_read_core_rules()),
        ("L2 Memory 已搜索", has_searched_memory()),
        ("L3 Orchestration 已调用", has_called_orchestration()),
        ("L4 Execution 已路由", has_routed_skill()),
        ("L5 Governance 已验证", has_validated_result()),
        ("L6 Infrastructure 已调用", has_called_infrastructure()),
    ]
    
    for check_name, check_result in checks:
        if not check_result:
            raise ArchitectureViolationError(f"违反架构: {check_name}")
    
    return True
```

### 2.2 任务结束后检查

```python
# ✅ 必须执行
def post_task_check(result):
    checks = [
        ("结果符合 IO 契约", validate_io_contract(result)),
        ("执行轨迹完整", validate_execution_trace(result)),
        ("审计日志已记录", validate_audit_log()),
    ]
    
    for check_name, check_result in checks:
        if not check_result:
            raise ArchitectureViolationError(f"违反架构: {check_name}")
    
    return True
```

---

## 三、执行轨迹

### 3.1 轨迹格式

**所有任务必须记录执行轨迹**：

```json
{
  "task_id": "task_1234567890",
  "timestamp": "2026-04-20T08:30:00Z",
  "layers": {
    "L1_core": {
      "status": "completed",
      "files_read": [
        "core/ARCHITECTURE.md",
        "core/LAYER_DEPENDENCY_MATRIX.md"
      ],
      "duration_ms": 50
    },
    "L2_memory": {
      "status": "completed",
      "queries": ["定时任务 天气汇报"],
      "results_count": 3,
      "duration_ms": 100
    },
    "L3_orchestration": {
      "status": "completed",
      "task_type": "query",
      "skill_selected": "find-skills",
      "duration_ms": 150
    },
    "L4_execution": {
      "status": "completed",
      "skill_executed": "find-skills",
      "execution_result": {...},
      "duration_ms": 200
    },
    "L5_governance": {
      "status": "completed",
      "validated": true,
      "audited": true,
      "duration_ms": 50
    },
    "L6_infrastructure": {
      "status": "completed",
      "tools_called": ["view_push_result"],
      "duration_ms": 300
    }
  },
  "total_duration_ms": 850,
  "compliance": true
}
```

### 3.2 轨迹存储

**路径**: `reports/ops/architecture_compliance.jsonl`

**格式**: JSONL (每行一个 JSON)

---

## 四、违规处理

### 4.1 违规类型

| 违规类型 | 严重程度 | 处理方式 |
|----------|----------|----------|
| 跳过 L1 Core | CRITICAL | 立即终止，重新开始 |
| 跳过 L2 Memory | HIGH | 警告，补充执行 |
| 直接调用工具 | HIGH | 警告，重新路由 |
| 违反 IO 契约 | MEDIUM | 警告，修正格式 |
| 缺少执行轨迹 | LOW | 记录，补充轨迹 |

### 4.2 违规记录

**路径**: `reports/ops/architecture_violations.jsonl`

**格式**:
```json
{
  "violation_id": "viol_1234567890",
  "timestamp": "2026-04-20T08:30:00Z",
  "type": "skip_core_rules",
  "severity": "CRITICAL",
  "task_id": "task_1234567890",
  "description": "跳过了 L1 Core 规则读取",
  "stack_trace": "...",
  "resolved": false
}
```

---

## 五、强制执行器

### 5.1 架构遵循装饰器

```python
def enforce_architecture(func):
    """强制架构遵循的装饰器"""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 1. 前置检查
        compliance_state = {
            "L1_core": False,
            "L2_memory": False,
            "L3_orchestration": False,
            "L4_execution": False,
            "L5_governance": False,
            "L6_infrastructure": False,
        }
        
        # 2. 执行函数
        try:
            result = await func(*args, compliance_state=compliance_state, **kwargs)
        except Exception as e:
            # 记录违规
            record_violation(compliance_state, str(e))
            raise
        
        # 3. 后置检查
        validate_compliance(compliance_state)
        
        # 4. 记录轨迹
        record_trace(compliance_state, result)
        
        return result
    
    return wrapper
```

### 5.2 使用方式

```python
@enforce_architecture
async def process_user_request(user_input: str, compliance_state: dict = None):
    # Step 1: L1 Core
    read_core_rules()
    compliance_state["L1_core"] = True
    
    # Step 2: L2 Memory
    search_memory(user_input)
    compliance_state["L2_memory"] = True
    
    # Step 3: L3 Orchestration
    task = orchestrate_task(user_input)
    compliance_state["L3_orchestration"] = True
    
    # Step 4: L4 Execution
    result = execute_skill(task)
    compliance_state["L4_execution"] = True
    
    # Step 5: L5 Governance
    validate_result(result)
    compliance_state["L5_governance"] = True
    
    # Step 6: L6 Infrastructure
    call_infrastructure(result)
    compliance_state["L6_infrastructure"] = True
    
    return result
```

---

## 六、自我检查机制

### 6.1 每次回复前检查

**在回复用户之前，必须回答以下问题**：

1. ✅ 我是否读取了 L1 Core 规则？
2. ✅ 我是否搜索了 L2 Memory？
3. ✅ 我是否通过了 L3 Orchestration 编排？
4. ✅ 我是否通过 L4 Execution 执行了技能？
5. ✅ 我是否通过 L5 Governance 验证了结果？
6. ✅ 我是否通过 L6 Infrastructure 调用了工具？
7. ✅ 我的结果是否符合 IO 契约？
8. ✅ 我是否记录了执行轨迹？

**如果有任何一项为 ❌，则必须立即修正，否则违反架构。**

### 6.2 违规自检

```python
def self_check_before_reply():
    """回复前的自我检查"""
    
    violations = []
    
    if not has_read_core_rules():
        violations.append("未读取 L1 Core 规则")
    
    if not has_searched_memory():
        violations.append("未搜索 L2 Memory")
    
    if not has_called_orchestration():
        violations.append("未调用 L3 Orchestration")
    
    if not has_routed_skill():
        violations.append("未路由 L4 Execution")
    
    if not has_validated_result():
        violations.append("未验证 L5 Governance")
    
    if not has_called_infrastructure():
        violations.append("未调用 L6 Infrastructure")
    
    if violations:
        return {
            "compliant": False,
            "violations": violations,
            "action": "必须立即修正后再回复"
        }
    
    return {
        "compliant": True,
        "violations": [],
        "action": "可以回复"
    }
```

---

## 七、版本历史

- V1.0.0: 初始版本，定义强制流程和检查机制

---

**维护者**: OpenClaw 架构团队
**更新日期**: 2026-04-20
