# 基于当前 `workspace_v8.3.0_skill_refactor` 的精确整改清单

这份清单不是泛泛建议，而是**基于当前压缩包已存在代码的逐项推进指令**。  
要求：后续修改必须直接在当前 8.3.0 包基础上完成，不允许另起一套平行实现。

---

## 一、先定结论：当前 8.3.0 已经做对的部分

当前包里，下面这些方向已经有了雏形，可以保留：

1. 已经有技能分层目录：
   - `skill_entry/`
   - `orchestration/`
   - `capabilities/`
   - `execution/`
   - `platform_adapter/`
   - `diagnostics/`
   - `config/`

2. 已经有运行模式定义：
   - `config/runtime_modes.py`

3. 已经有平台探测和适配器骨架：
   - `platform_adapter/runtime_probe.py`
   - `platform_adapter/base.py`
   - `platform_adapter/null_adapter.py`
   - `platform_adapter/xiaoyi_adapter.py`

4. 已经有已验收的任务内核可复用：
   - `infrastructure/task_manager.py`
   - `application/task_service/service.py`
   - `infrastructure/workers/executor.py`
   - `infrastructure/storage/repositories/sqlite_repo.py`

5. 已经有执行链路落库能力：
   - `tasks`
   - `task_runs`
   - `task_steps`
   - `task_events`

**后续原则：**
- 保留 8.3.0 的技能分层外壳
- 但默认执行链路必须统一落到**已验收的任务内核**
- 不允许让 `capabilities/`、`orchestration/` 再造一套脱离实际落库链路的“新玩具实现”

---

## 二、当前 8.3.0 的核心问题（已从包内代码直接定位）

### 问题 1：`capabilities/` 目前大多还是假实现，没接真实内核

当前这些文件返回的是硬编码结果，不是实际系统行为：

- `capabilities/send_message.py`
- `capabilities/schedule_task.py`
- `capabilities/retry_task.py`
- `capabilities/pause_task.py`
- `capabilities/resume_task.py`
- `capabilities/cancel_task.py`
- `capabilities/diagnostics.py`
- `capabilities/export_history.py`
- `capabilities/replay_run.py`
- `capabilities/self_repair.py`

现状特征：
- `schedule_task.py` 只是生成 UUID，**没有真正持久化任务**
- `pause/resume/cancel/retry` 只是返回状态字符串，**没有真正调用 `TaskManager`**
- `send_message.py` 只是返回 `message_id`，**没有经过真实 `MessageAdapter` / `task_steps` 链路**
- `export_history.py` / `replay_run.py` 返回空数组
- `diagnostics.py` / `self_repair.py` 是硬编码 PASS

**结论：当前“能力层”大多是 UI 级包装，不是内核级能力。**

### 问题 2：能力注册表存在，但没有真正自动装配

文件：
- `capabilities/registry.py`

问题：
- 注册表本身没问题
- 但包内没有一套**默认启动时自动注册全部能力**的统一 bootstrap
- `RuntimeSelfCheck` 检查注册表时，很可能拿到空注册表或不完整注册表
- `skill_entry/input_router.py` 也没有自动把请求类型和能力注册表绑定起来

**结论：能力注册表现在是“有容器，没装线”。**

### 问题 3：`skill_entry/input_router.py` 只有路由壳，没有默认布线

文件：
- `skill_entry/input_router.py`

问题：
- 只定义了 `RequestType`
- 只支持“有人手动注册 handler”的情况
- 当前包里没有可靠的默认 wiring，把请求类型统一映射到能力注册表
- 没有在 `get_router()` 时自动完成 bootstrap
- 没有把 `validators.py`、`response_formatter.py` 真正串起来

**结论：入口层还没有形成真正的技能入口闭环。**

### 问题 4：`platform_adapter/runtime_probe.py` 和 `xiaoyi_adapter.py` 现在语义不一致

文件：
- `platform_adapter/runtime_probe.py`
- `platform_adapter/xiaoyi_adapter.py`

具体问题：
- `get_recommended_adapter()` 会返回 `"harmonyos"`，但当前包里没有 `platform_adapter/harmonyos_adapter.py`
- `_determine_mode()` 只看环境变量，不看真实能力探测结果
- `xiaoyi_adapter.py` 里的 `_check_task_scheduling()` / `_check_message_sending()` / `_check_notification()` 全是 `return False`
- `invoke()` 成功分支只是返回 `"result": "invoked"`，不是真调用

**结论：平台增强层目前只有骨架，没有形成一致的“探测 -> 能力声明 -> 调用/降级”闭环。**

### 问题 5：你现在其实有两套“任务编排模型”，默认路径会打架

文件：
- 已验收真实内核：`infrastructure/task_manager.py`、`application/task_service/service.py`
- 新增平行模型：`orchestration/task_orchestrator.py`
- 新增平行模型：`orchestration/batch_orchestrator.py`
- 新增平行模型：`orchestration/workflow_orchestrator.py`

问题：
- `infrastructure/task_manager.py` 走的是已验收的 `TaskSpec / TaskStatus / SQLite repo / executor / task_runs / task_steps / task_events`
- 但 `orchestration/task_orchestrator.py` 又定义了一套自己的 `TaskState / Task / 内存 _tasks`
- `batch_orchestrator.py` / `workflow_orchestrator.py` 也是各自维护内存状态，不默认接 `TaskManager`

**结论：现在不是一个强内核，而是“一个真内核 + 三个平行新壳子”。**

### 问题 6：诊断层现在查到的是“结构存在”，不是“默认链路真实可用”

文件：
- `diagnostics/runtime_self_check.py`

问题：
- `_check_capabilities()` 只看注册表里有多少能力，不保证这些能力都接了真实内核
- `_check_platform_adapter()` 只看 `RuntimeProbe.detect_environment()`，不看推荐适配器是否真的存在 / 能 probe / 能 fallback
- `_check_storage()` 只看数据库文件是否存在，不看核心表是否齐全
- 没检查 `tasks / task_runs / task_steps / task_events / workflow_checkpoints`
- 没检查默认技能路径是否能“路由 -> 能力 -> 任务内核 -> 落库”

**结论：自检层还不够硬。**

### 问题 7：测试现在只证明“新壳子能 import”，没有证明“新壳子接上了真内核”

当前新增测试：
- `tests/test_runtime_modes.py`
- `tests/test_platform_probe.py`
- `tests/test_degradation_strategy.py`
- `tests/test_capability_registry.py`
- `tests/test_batch_tasks.py`
- `tests/test_workflow_resume.py`
- `tests/test_diagnostics_export.py`

问题：
- 这些测试大部分只证明类能创建、函数能返回、dict 有字段
- 但没证明：
  - `schedule_task` 真的写入 `tasks`
  - `pause/retry/cancel/resume` 真的命中 `TaskManager`
  - `send_message` 真的走到 `MessageAdapter`
  - `export_history` 真的导出 `task_runs/task_steps/task_events`
  - `replay_run` 真的读出某个 `run_id` 的真实步骤链路
  - 平台增强不可用时，是否真的自动降级到 `NullAdapter`

**结论：测试还没有卡住“假实现”。**

---

## 三、必须直接改的内容（按文件点名，不准自由发挥）

### A. 统一默认执行主链：新壳子必须接入旧内核

#### A1. 保留 `infrastructure/task_manager.py` 作为默认唯一任务内核入口
要求：
- `capabilities/` 默认一律通过 `get_task_manager()` 操作真实任务
- 不允许 `capabilities/` 继续直接返回硬编码假结果

#### A2. `orchestration/task_orchestrator.py` 不得再作为默认路径使用
要求二选一：
1. **优先方案：**
   - 把 `orchestration/task_orchestrator.py` 标成 experimental
   - 默认技能路径不再走它
2. **如果一定要保留：**
   - 彻底改成包装 `TaskManager`
   - 删除自定义 `TaskState`
   - 删除内存 `_tasks`
   - 状态、持久化、执行统一走 `domain.tasks.TaskStatus` 和 SQLite repo

#### A3. `orchestration/batch_orchestrator.py` 与 `workflow_orchestrator.py` 必须接入真实任务内核
要求：
- `BatchOrchestrator.create_batch()` 不再只存内存 `BatchJob`
- 批量项必须调用真实 `schedule_task` / `TaskManager`
- `WorkflowOrchestrator.execute_workflow()` 的步骤执行结果必须能关联真实 `task_runs / task_steps`
- 如果暂时做不到完整落库，就明确标记 experimental，不得放进默认能力矩阵里冒充已完成

### B. 逐个替换假能力实现

#### B1. 修改 `capabilities/schedule_task.py`
必须改成：
- 使用 `from infrastructure.task_manager import get_task_manager`
- 有 `cron_expr` -> 调 `tm.create_recurring_message(...)`
- 有 `run_at` -> 调 `tm.create_scheduled_message(...)`
- 返回真实 `success / task_id / status / idempotent`
- 不得再手工 `uuid.uuid4()`

#### B2. 修改 `capabilities/retry_task.py`
必须改成：
- 调 `tm.retry_task(task_id)`
- 返回真实 `status / delivery_status`
- 不得只返回 `"queued"`

#### B3. 修改 `capabilities/pause_task.py`
必须改成：
- 调 `tm.pause_task(task_id)`
- 返回真实结果 dict

#### B4. 修改 `capabilities/resume_task.py`
必须改成：
- 调 `tm.resume_task(task_id)`
- 返回真实结果 dict

#### B5. 修改 `capabilities/cancel_task.py`
必须改成：
- 调 `tm.cancel_task(task_id)`
- 返回真实结果 dict

#### B6. 修改 `capabilities/send_message.py`
必须改成：
- 不要伪造 `message_id`
- 走真实发送链路：
  - 优先 `MessageAdapter.send_message(...)`
  - 或 `TOOL_REGISTRY["send_message"]`
- 输入参数至少支持 `user_id / message / task_id / run_id`
- 返回必须保留真实语义：`success / status / task_id / run_id`
- `queued_for_delivery` 必须保留，不得重新发明假状态

#### B7. 修改 `capabilities/diagnostics.py`
必须改成：
- 调 `RuntimeSelfCheck().run_all_checks()`
- 不允许硬编码 PASS

#### B8. 修改 `capabilities/export_history.py`
必须改成真实导出：
- 读取 `tasks / task_runs / task_steps / task_events`
- 最少支持按 `task_id` 导出
- 返回 `task / runs / steps / events / record_count`
- 直接调用：
  - `SQLiteTaskRepository`
  - `SQLiteTaskRunRepository`
  - `SQLiteTaskStepRepository`
  - `SQLiteTaskEventRepository`

#### B9. 修改 `capabilities/replay_run.py`
必须改成真实回放：
- 输入：`run_id`
- 读取 `task_runs / task_steps / task_events`
- 返回 `run / steps / events / timeline`
- 不允许再返回空 `steps=[]`

#### B10. 修改 `capabilities/self_repair.py`
必须改成二选一：
1. **推荐：**做最小真实自修复
   - 检查 orphan `task_steps`
   - 检查 orphan `task_events`
   - 检查 pending_sends 文件是否可写
   - 检查 DB schema 是否完整
2. **若来不及：**降级为只做检测，不自动修复
   - 但绝不能继续硬编码“全部正常”

### C. 增加真正的 bootstrap，让能力和入口层连起来

#### C1. 新增 `capabilities/bootstrap.py`
职责：
- 实例化所有 Capability 类
- 把每个 `.execute` 注册到 `CapabilityRegistry`
- 提供：
  - `bootstrap_capabilities()`
  - `register_default_capabilities()`

必须注册：
- `send_message`
- `schedule_task`
- `retry_task`
- `pause_task`
- `resume_task`
- `cancel_task`
- `diagnostics`
- `export_history`
- `replay_run`
- `self_repair`

#### C2. 修改 `capabilities/__init__.py`
要求：
- 导出 bootstrap
- 不要只导出类名

#### C3. 修改 `skill_entry/input_router.py`
必须增加：
- 在 `get_router()` 第一次初始化时自动调用 bootstrap
- 自动把 `RequestType` 映射到 `registry.execute(...)`
- 不要求调用方手动注册 handler 才能用

建议新增私有函数：
- `_wire_default_handlers(router)`

映射至少包括：
- `SEND_MESSAGE -> send_message`
- `SCHEDULE_TASK -> schedule_task`
- `RETRY_TASK -> retry_task`
- `PAUSE_TASK -> pause_task`
- `RESUME_TASK -> resume_task`
- `CANCEL_TASK -> cancel_task`
- `DIAGNOSTICS -> diagnostics`
- `EXPORT_HISTORY -> export_history`
- `REPLAY_RUN -> replay_run`
- `SELF_REPAIR -> self_repair`

#### C4. 修改 `skill_entry/input_router.py` 的执行逻辑
必须改成：
- 兼容 sync / async handler
- 兼容 sync / async middleware
- 在路由前先调 `validators.py`
- 在返回前统一过 `response_formatter.py`

### D. 修正平台增强层，别再自相矛盾

#### D1. 修改 `platform_adapter/runtime_probe.py`
必须改：
1. `get_recommended_adapter()` 不得再返回不存在实现的 `"harmonyos"`
   - 推荐：HarmonyOS 与 Xiaoyi 统一映射到 `"xiaoyi"`
   - 或补 `platform_adapter/harmonyos_adapter.py`
2. `_determine_mode()` 改为：
   - 先 probe adapter
   - 只有至少一个核心能力 available 才算 `platform_enhanced`
   - 否则回退 `skill_default`
3. `_detect_database()` 改为拆分：
   - `has_local_sqlite`
   - `has_external_database`
   - `has_redis`
   然后：
   - `platform_enhanced` 看 adapter probe
   - `self_hosted_enhanced` 至少要真实外部数据库配置 + Redis
   - 否则 `skill_default`

#### D2. 修改 `platform_adapter/xiaoyi_adapter.py`
必须改：
1. 去掉 TODO + 永远 False 的伪实现
2. `probe()` 增加：
   - `limitations`
   - `fallback_mode`
3. `invoke()` 不准再返回假成功 `"result": "invoked"`
   - 有真实 hook 才调
   - 没有真实 hook 则返回 `CAPABILITY_NOT_AVAILABLE` + `fallback_available=True`

### E. 把运行时自检改硬，不要再只查“文件存在”

#### E1. 修改 `diagnostics/runtime_self_check.py`
必须增加：
- 检查表：
  - `tasks`
  - `task_runs`
  - `task_steps`
  - `task_events`
  - `workflow_checkpoints`
- 先 bootstrap 再检查 registry
- 若注册数为 0 -> fail
- 若核心能力缺项 -> fail
- 核心能力：
  - `send_message`
  - `schedule_task`
  - `retry_task`
  - `pause_task`
  - `resume_task`
  - `cancel_task`
  - `diagnostics`
  - `export_history`
  - `replay_run`
- 平台检查不仅看 `detect_environment()`，还要校验推荐 adapter 是否真实存在、能 probe、能 fallback
- 默认链路检查：
  - 创建 1 个测试任务
  - 查询任务
  - 验证写入 `tasks`

### F. 调整测试，卡死“假实现”

#### F1. 修改 `tests/test_capability_registry.py`
新增断言：
- bootstrap 后核心能力数量 >= 10
- `schedule_task` 执行后 `tasks` 表新增真实记录
- `pause/resume/cancel/retry` 命中真实 `TaskManager`

#### F2. 修改 `tests/test_diagnostics_export.py`
新增：
- `export_history` 针对真实 task_id 返回非空 `task`
- 至少有 `events` 或 `runs`
- `replay_run` 针对真实 run_id 返回非空 `steps / timeline`

#### F3. 修改 `tests/test_platform_probe.py`
新增：
- 推荐 adapter 不得指向不存在的实现
- 若返回 `"xiaoyi"`，则 `xiaoyi_adapter` 必须可 import
- 若平台能力不可用，`runtime_mode` 必须回落到 `skill_default`

#### F4. 新增 `tests/test_router_bootstrap.py`
必须验证：
- `route_request({"type":"diagnostics","data":{}})` 能直接跑通
- 不需要手工 `register_handler`
- 路由 -> registry -> capability 执行链路成立

#### F5. 新增 `tests/test_real_capability_integration.py`
至少覆盖：
- `schedule_task` -> `tasks`
- `retry_task` -> 状态变化
- `export_history` -> 返回真实数据
- `replay_run` -> 返回真实 run/step 链路

### G. 文档口径必须同步

同步更新：
- `SKILL_PRODUCT_ARCHITECTURE.md`
- `CAPABILITY_MATRIX.md`
- `DEFAULT_SKILL_CONFIG.md`
- `DEGRADATION_STRATEGY.md`
- `RELEASE_NOTES_SKILL_REFACTOR.md`

必须写清：
- 哪些能力已真实接入任务内核
- 哪些能力已真实接入落库链路
- 哪些平台能力仍是适配器骨架
- 哪些 workflow/batch 能力还未默认启用

---

## 四、执行顺序（必须按这个顺序改）

1. 先改 `capabilities/`，把所有假实现接到 `TaskManager / repo`
2. 再加 `capabilities/bootstrap.py`
3. 再改 `skill_entry/input_router.py` 做自动 wiring
4. 再修 `runtime_probe.py / xiaoyi_adapter.py` 的自相矛盾
5. 再改 `runtime_self_check.py`
6. 再补测试
7. 最后再改文档和验收报告

---

## 五、最终交付要求（下一轮必须一起给）

1. 新完整压缩包
2. 一份 `EXACT_SKILL_REFACTOR_VERIFICATION.txt`
3. 真实输出：
   - 新增测试运行结果
   - `schedule_task` 创建真实任务后的数据库记录
   - `export_history` 返回样例
   - `replay_run` 返回样例
   - `route_request()` 直调能力样例
   - `RuntimeSelfCheck().run_all_checks()` 的真实输出

---

## 六、验收标准（这次只认这几个）

只有同时满足下面条件，这轮才算真正完成：

1. `capabilities/` 不再是硬编码假返回
2. `skill_entry` 已默认接通能力注册表
3. 平台探测和平台适配器不再自相矛盾
4. 默认技能路径统一走已验收的真实任务内核
5. `export_history / replay_run` 返回真实库数据
6. 新测试能卡住“空实现”和“假实现”

---

## 七、一句话给开发者

**这次不是继续加壳子，而是把 8.3.0 新增的技能层真正焊接到已经验收过的任务内核上。**
