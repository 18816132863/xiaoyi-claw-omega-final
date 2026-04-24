# 8.3.0 精确整改 V2 —— 必须直接修改的点

这份不是建议，是按当前 `workspace_v8.3.0_exact_refactor.tar.gz` 实际代码和实际失败结果得出的精确修改清单。

当前包**不能直接认定为最终完成**，因为我这里独立复核时，至少有 3 处已经能稳定复现的问题：

1. `tests/test_real_capability_integration.py::test_schedule_task_creates_real_task` 失败
2. `tests/test_real_capability_integration.py::test_pause_resume_cancel_chain` 失败
3. `tests/test_platform_probe.py::test_detect_environment` 失败

另外，`runtime_probe.py` 和 `xiaoyi_adapter.py` 仍然存在实际语义矛盾：
- 只要设置 `HARMONYOS_VERSION`，`RuntimeProbe.detect_environment()` 就会切到 `platform_enhanced`
- 但 `XiaoyiAdapter.is_available()` 仍返回 `False`
- 这说明“推荐适配器”和“实际可用适配器”还没有真正统一

---

## 一、必须改的 1：修复 platform probe 字段协议不一致

### 现状问题
文件：`platform_adapter/runtime_probe.py`

当前 `detect_environment()` 返回的是：
- `has_local_sqlite`
- `has_external_database`

但测试文件 `tests/test_platform_probe.py` 断言的是：
- `has_database`

这导致测试直接失败。

### 必须怎么改
不要改测试绕过，直接统一协议。

在 `platform_adapter/runtime_probe.py` 的 `detect_environment()` 返回值中新增：

```python
"has_database": env["has_local_sqlite"] or env["has_external_database"]
```

最终环境字典必须同时保留：
- `has_database`
- `has_local_sqlite`
- `has_external_database`

原因：
- `has_database` 给上层和测试使用，语义稳定
- `has_local_sqlite / has_external_database` 给底层细分判断使用

### 验收命令
```bash
pytest -q tests/test_platform_probe.py
```

通过标准：全部通过。

---

## 二、必须改的 2：修复 RuntimeProbe 与 XiaoyiAdapter 的自相矛盾

### 现状问题
文件：
- `platform_adapter/runtime_probe.py`
- `platform_adapter/xiaoyi_adapter.py`

当前行为是：
1. 只要有 `HARMONYOS_VERSION` 或 `XIAOYI_ENV`，`get_recommended_adapter()` 就返回 `xiaoyi`
2. `_determine_mode()` 因为拿到 `xiaoyi`，所以切到 `platform_enhanced`
3. 但 `XiaoyiAdapter` 当前所有 capability 都是 `available=False`
4. `XiaoyiAdapter.is_available()` 返回 `False`

这表示：
- `runtime_probe` 认为平台增强模式可用
- `xiaoyi_adapter` 自己却认为不可用

这和你这次整改报告里“runtime_probe 只返回实际可用适配器”是冲突的。

### 必须怎么改
#### 改法 A（推荐，最稳）
让 `get_recommended_adapter()` 真正探测适配器，而不是只看模块能否导入。

把 `get_recommended_adapter()` 改成下面这个逻辑：

1. 若不在小艺/鸿蒙环境，直接返回 `null`
2. 若在小艺/鸿蒙环境：
   - 实例化 `XiaoyiAdapter`
   - 调用 `probe()`
   - 只有当：
     - `probe()["available"] == True`
     - 且至少一个 capability 为 `True`
   才返回 `xiaoyi`
3. 否则返回 `null`

#### 改法 B（配套）
同时把 `XiaoyiAdapter.probe()` 的 `available` 语义改清楚：

当前它返回：
```python
"available": self._available
```

这不对。

应该改成：
```python
"available": self._available and any(status.available for status in self._capabilities.values())
```

也就是：
- 环境存在，不等于能力可用
- 真正 available 必须是“环境存在 + 至少一个能力已接通”

#### 改法 C（模式判定）
`_determine_mode()` 不要再只靠 `adapter_name != "null"`。

改成：
- `get_recommended_adapter()` 返回 `xiaoyi` 才进入 `platform_enhanced`
- 否则继续检查 self-hosted
- 否则 `skill_default`

### 必须新增测试
新增：`tests/test_runtime_probe_adapter_consistency.py`

至少覆盖这 2 个场景：

#### 场景 1：仅设置 `HARMONYOS_VERSION`，但平台能力未接通
预期：
- `get_recommended_adapter() == "null"`
- `detect_environment()["runtime_mode"] == "skill_default"`

#### 场景 2：未来若 xiaoyi 真接通能力
预期：
- `get_recommended_adapter() == "xiaoyi"`
- `runtime_mode == "platform_enhanced"`

### 验收命令
```bash
pytest -q tests/test_platform_probe.py tests/test_runtime_probe_adapter_consistency.py
```

---

## 三、必须改的 3：修复 `test_schedule_task_creates_real_task` 失败

### 现状问题
文件：
- `tests/test_real_capability_integration.py`
- `infrastructure/task_manager.py`

当前失败原因不是 `schedule_task` 没创建真实任务，
而是测试断言写错了。

现在 `TaskManager.create_scheduled_message()` 的 `goal` 是：
```python
f"在 {run_at} 发送消息: {message[:50]}..."
```

所以数据库里的 `task.goal` 根本不是纯消息文本。

当前测试却写成：
```python
assert task.goal == "Integration test task"
```

这一定会失败。

### 必须怎么改
不要为了迎合测试去破坏 `goal` 语义。

请直接改测试：

把：
```python
assert task.goal == "Integration test task"
```

改成其中一种更稳定的断言：

#### 推荐写法 1
```python
assert "Integration test task" in task.goal
```

#### 更精确写法 2
如果 `TaskSpec.inputs` 可取到 message：
```python
assert task.inputs["message"] == "Integration test task"
```
并同时保留：
```python
assert "Integration test task" in task.goal
```

### 配套建议
`capabilities/schedule_task.py` 的返回值里建议补一个：
```python
"message": message
```
这样技能层调用方不需要反向解析 `goal`。

### 验收命令
```bash
pytest -q tests/test_real_capability_integration.py::test_schedule_task_creates_real_task
```

---

## 四、必须改的 4：修复 pause/resume/cancel 集成测试失败

### 现状问题
文件：
- `tests/test_real_capability_integration.py`
- `application/task_service/service.py`

当前测试流程是：
1. 创建任务
2. 直接调用 `pause_task`
3. 断言 success == True

但 `TaskService.pause_task()` 当前只允许这些状态暂停：
- `QUEUED`
- `RUNNING`

而刚创建的任务状态通常是 `PERSISTED`

所以测试直接失败不是偶发，而是逻辑必然失败。

### 你必须二选一，不能模糊

#### 方案 A（推荐，符合技能产品直觉）
**让已创建但尚未执行的任务也能暂停。**

把 `application/task_service/service.py` 里的可暂停状态从：
```python
(TaskStatus.QUEUED, TaskStatus.RUNNING)
```
改成：
```python
(TaskStatus.PERSISTED, TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.WAITING_RETRY)
```

这样用户刚建好的任务可以直接暂停，更符合技能语义。

同时，`resume_task()` 不能一律恢复到 `QUEUED`，应该恢复到“暂停前状态”或至少区分：
- 原状态是 `PERSISTED` → 恢复到 `PERSISTED`
- 原状态是 `QUEUED` / `RUNNING` / `WAITING_RETRY` → 恢复到 `QUEUED`

#### 必须配套改事件负载
在 `pause_task()` 记录事件时，已经有：
```python
{"previous_status": task.status.value}
```
```
这个值必须被 `resume_task()` 读取并用于恢复目标状态。
```

也就是说：
- 你要从最近一次 `PAUSED` 事件或任务字段里恢复 `previous_status`
- 不能永远写死成 `QUEUED`

#### 方案 B（不推荐，但也行）
如果你坚持“只有 QUEUED/RUNNING 才能暂停”，
那就必须把测试改成先把任务置为 `QUEUED` 再暂停：

```python
await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
```

但这不如方案 A 符合技能用户直觉。

### 我建议你采用方案 A
原因：
- 技能用户一般会认为“刚创建的任务也可以暂停”
- 这比强制先入队再暂停更自然
- 也更符合“强技能产品”定位

### 必须新增测试
新增：`tests/test_pause_resume_semantics.py`

至少覆盖：
1. `PERSISTED -> PAUSED -> PERSISTED`
2. `QUEUED -> PAUSED -> QUEUED`
3. `CANCELLED` 不可恢复
4. `SUCCEEDED` 不可暂停

### 验收命令
```bash
pytest -q tests/test_real_capability_integration.py::test_pause_resume_cancel_chain tests/test_pause_resume_semantics.py
```

---

## 五、必须改的 5：补齐报告与真实测试结果不一致问题

### 现状问题
你提交的 `EXACT_SKILL_REFACTOR_VERIFICATION.txt` 里写的是：
- 路由通过
- schedule_task 通过
- retry_task 通过
- cancel_task 通过
- 新测试都能卡住空实现

但我这里独立复核时，至少以下测试失败：
- `tests/test_real_capability_integration.py::test_schedule_task_creates_real_task`
- `tests/test_real_capability_integration.py::test_pause_resume_cancel_chain`
- `tests/test_platform_probe.py::test_detect_environment`

这说明你的验收报告没有覆盖真实失败点，或者没有在同一代码包上跑。

### 必须怎么改
下一轮不要只给摘要，必须给完整命令输出。

至少附：
```bash
pytest -q tests/test_router_bootstrap.py tests/test_real_capability_integration.py tests/test_no_fake_implementation.py tests/test_platform_probe.py tests/test_runtime_modes.py
```

并把完整控制台输出原样放进：
- `EXACT_SKILL_REFACTOR_VERIFICATION_V2.txt`

不允许再只写“✅ 通过”摘要。

---

## 六、建议顺手补的 2 个增强点（不是阻塞，但应一起改）

### 1. `capabilities/send_message.py`
现在返回：
```python
"status": result.get("delivery_status", "unknown")
```

建议同时补：
```python
"delivery_status": result.get("delivery_status", "unknown")
```

避免上层只有 `status`，和任务状态机里的 `status` 混淆。

### 2. `diagnostics/runtime_self_check.py`
`_check_platform_adapter()` 现在只检查：
- 推荐适配器是否存在

这不够。

应改成检查：
- 推荐适配器是否存在
- 推荐适配器是否真的 `available`
- 若不 available，当前模式应自动回到 `skill_default`

否则“平台增强模式已启用但能力全没接通”的问题还会漏过去。

---

## 七、你下一轮必须交付什么

不要再只发压缩包和一份摘要报告。

下一轮必须一起发：
1. 新完整压缩包
2. `EXACT_SKILL_REFACTOR_VERIFICATION_V2.txt`
3. 完整 pytest 输出
4. 新增测试文件：
   - `tests/test_runtime_probe_adapter_consistency.py`
   - `tests/test_pause_resume_semantics.py`
5. 修正后的：
   - `platform_adapter/runtime_probe.py`
   - `platform_adapter/xiaoyi_adapter.py`
   - `application/task_service/service.py`
   - `capabilities/schedule_task.py`
   - `tests/test_real_capability_integration.py`
   - `tests/test_platform_probe.py`
   - `diagnostics/runtime_self_check.py`

---

## 八、下一轮验收标准（硬标准）

必须同时满足：

### A. platform probe 一致
- `has_database` 存在
- `HARMONYOS_VERSION` 仅存在但平台能力未接通时，不得误判为 `platform_enhanced`
- `runtime_probe` 与 `xiaoyi_adapter.is_available()` 语义一致

### B. 真集成测试通过
- `test_schedule_task_creates_real_task` 通过
- `test_pause_resume_cancel_chain` 通过
- `test_detect_environment` 通过

### C. 报告与代码一致
- 报告里的命令必须可复现
- 不允许再出现“报告通过，包内实际测试失败”

---

## 九、你直接照着改的命令

```text
直接按 00_exact_refactor_fix_v2.md 修改，不要再自己发挥。
这次必须先把下面 3 个失败点修掉：
1. test_detect_environment
2. test_schedule_task_creates_real_task
3. test_pause_resume_cancel_chain

然后补两个新增测试：
- tests/test_runtime_probe_adapter_consistency.py
- tests/test_pause_resume_semantics.py

最后附完整 pytest 原始输出，不要只写摘要。
```
