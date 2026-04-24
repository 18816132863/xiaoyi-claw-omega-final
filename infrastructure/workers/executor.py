"""
任务执行器 V3.0.0

职责：
- 从队列拉取任务
- 执行任务步骤
- 记录执行结果
- 区分"执行成功"和"送达成功"

语义说明：
- succeeded: 任务执行成功且真实送达
- delivery_pending: 任务执行成功，等待真实送达确认
- waiting_retry: 任务失败，等待重试
- failed: 任务最终失败
"""

import asyncio
import json
import uuid
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
from pathlib import Path

from domain.tasks import (
    TaskSpec,
    TaskStatus,
    StepStatus,
    EventType,
)
from infrastructure.storage.repositories import (
    SQLiteTaskRepository,
    SQLiteTaskRunRepository,
    SQLiteTaskStepRepository,
    SQLiteTaskEventRepository,
    SQLiteCheckpointRepository,
)


def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class TaskExecutor:
    """任务执行器"""
    
    def __init__(
        self,
        task_repo: Optional[SQLiteTaskRepository] = None,
        run_repo: Optional[SQLiteTaskRunRepository] = None,
        step_repo: Optional[SQLiteTaskStepRepository] = None,
        event_repo: Optional[SQLiteTaskEventRepository] = None,
        checkpoint_repo: Optional[SQLiteCheckpointRepository] = None,
        tool_registry: Optional[Dict[str, Callable]] = None
    ):
        self.task_repo = task_repo or SQLiteTaskRepository()
        self.run_repo = run_repo or SQLiteTaskRunRepository()
        self.step_repo = step_repo or SQLiteTaskStepRepository()
        self.event_repo = event_repo or SQLiteTaskEventRepository()
        self.checkpoint_repo = checkpoint_repo or SQLiteCheckpointRepository()
        self.tool_registry = tool_registry or {}
        self.root = get_project_root()
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        执行任务
        
        流程：
        1. 加载任务
        2. 创建运行记录
        3. 逐步执行
        4. 记录结果
        
        Returns:
            success: 步骤执行是否成功
            delivery_status: delivered / queued_for_delivery / failed
        """
        # 1. 加载任务
        task = await self.task_repo.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在", "delivery_status": "failed"}
        
        # 2. 检查状态
        if task.status not in (TaskStatus.QUEUED, TaskStatus.RESUMED):
            return {"success": False, "error": f"任务状态 {task.status.value} 不可执行", "delivery_status": "failed"}
        
        # 3. 更新状态
        await self.task_repo.update(task_id, {"status": TaskStatus.RUNNING.value})
        
        # 4. 记录事件
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.STARTED.value,
            event_payload={}
        )
        
        # 5. 创建运行记录（真实落库）
        # 获取当前 run_no
        existing_runs = await self.run_repo.list_runs(task_id, limit=1)
        run_no = (existing_runs[0]["run_no"] + 1) if existing_runs else 1
        
        run_id = await self.run_repo.create_run(task_id, run_no)
        thread_id = f"thread_{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 6. 执行步骤
        result = await self._execute_steps(task, run_id, thread_id)
        
        # 7. 更新运行记录状态
        await self.run_repo.update_run(run_id, {
            "status": "succeeded" if result["success"] else "failed",
            "ended_at": datetime.now(),
            "error_text": result.get("error") if not result["success"] else None
        })
        
        # 7. 更新最终状态
        now_iso = datetime.now().isoformat()
        
        if result["success"]:
            delivery_status = result.get("delivery_status", "queued_for_delivery")
            
            if delivery_status == "delivered":
                # 真实送达成功
                if task.schedule and task.schedule.mode.value in ('cron', 'recurring'):
                    next_run = task.schedule.get_next_run_at(datetime.now())
                    await self.task_repo.update(task_id, {
                        "status": TaskStatus.PERSISTED.value,
                        "last_run_at": now_iso,
                        "next_run_at": next_run.isoformat() if next_run else None
                    })
                else:
                    await self.task_repo.update(task_id, {
                        "status": TaskStatus.SUCCEEDED.value,
                        "last_run_at": now_iso,
                        "next_run_at": None
                    })
                
                await self.event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.SUCCEEDED.value,
                    event_payload={"run_id": run_id, "delivery_status": "delivered"}
                )
            elif delivery_status == "queued_for_delivery":
                # 执行成功但未真实送达，进入 delivery_pending
                await self.task_repo.update(task_id, {
                    "status": TaskStatus.DELIVERY_PENDING.value,
                    "last_run_at": now_iso,
                    "last_error": None
                })
                
                await self.event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.DELIVERY_PENDING.value,
                    event_payload={"run_id": run_id, "note": "等待真实送达确认"}
                )
            else:
                # 其他情况视为失败
                await self.task_repo.update(task_id, {
                    "status": TaskStatus.FAILED.value,
                    "last_run_at": now_iso,
                    "last_error": f"未知交付状态: {delivery_status}"
                })
                
                await self.event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.FAILED.value,
                    event_payload={"run_id": run_id, "error": f"未知交付状态: {delivery_status}"}
                )
        else:
            # 执行失败，检查重试
            task = await self.task_repo.get(task_id)
            attempt_count = task.attempt_count + 1 if hasattr(task, 'attempt_count') else 1
            
            if attempt_count < task.retry_policy.max_attempts:
                retry_after = datetime.now() + timedelta(seconds=task.retry_policy.backoff_seconds * attempt_count)
                await self.task_repo.update(task_id, {
                    "status": TaskStatus.WAITING_RETRY.value,
                    "attempt_count": attempt_count,
                    "last_error": result.get("error", ""),
                    "next_run_at": retry_after.isoformat()
                })
                
                await self.event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.RETRYING.value,
                    event_payload={
                        "attempt": attempt_count,
                        "max_attempts": task.retry_policy.max_attempts,
                        "error": result.get("error", ""),
                        "retry_after": retry_after.isoformat()
                    }
                )
            else:
                await self.task_repo.update(task_id, {
                    "status": TaskStatus.FAILED.value,
                    "last_error": result.get("error", "")
                })
                
                await self.event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.FAILED.value,
                    event_payload={
                        "error": result.get("error", ""),
                        "attempts": attempt_count
                    }
                )
        
        return result
    
    async def _execute_steps(
        self,
        task: TaskSpec,
        run_id: str,
        thread_id: str
    ) -> Dict[str, Any]:
        """执行任务步骤"""
        context = {
            "task": task,
            "run_id": run_id,
            "thread_id": thread_id,
            "task_id": task.task_id,
            "inputs": task.inputs.copy(),
            "outputs": {},
            "current_step": 0,
            "delivery_status": "queued_for_delivery"
        }
        
        await self._save_checkpoint(context)
        
        for step in task.steps:
            context["current_step"] = step.step_index
            
            # 创建步骤记录（真实落库）
            step_id = await self.step_repo.create_step(
                task_run_id=run_id,
                step_index=step.step_index,
                step_name=step.step_name,
                tool_name=step.tool_name,
                input_json=step.input_mapping if hasattr(step, 'input_mapping') else {}
            )
            
            await self.event_repo.record_event(
                task_id=task.task_id,
                event_type=EventType.STEP_STARTED.value,
                event_payload={
                    "run_id": run_id,
                    "step_index": step.step_index,
                    "step_name": step.step_name
                },
                run_id=run_id
            )
            
            step_result = await self._execute_step(step, context)
            
            # 更新步骤记录
            await self.step_repo.update_step(step_id, {
                "status": "succeeded" if step_result["success"] else "failed",
                "output_json": step_result.get("output", {}),
                "ended_at": datetime.now(),
                "error_text": step_result.get("error") if not step_result["success"] else None
            })
            
            if not step_result["success"]:
                await self.event_repo.record_event(
                    task_id=task.task_id,
                    event_type=EventType.STEP_FAILED.value,
                    event_payload={
                        "run_id": run_id,
                        "step_index": step.step_index,
                        "error": step_result.get("error", "")
                    },
                    run_id=run_id
                )
                
                return {
                    "success": False,
                    "error": f"步骤 {step.step_name} 失败: {step_result.get('error', '')}",
                    "step_index": step.step_index,
                    "delivery_status": "failed"
                }
            
            await self.event_repo.record_event(
                task_id=task.task_id,
                event_type=EventType.STEP_COMPLETED.value,
                event_payload={
                    "run_id": run_id,
                    "step_index": step.step_index,
                    "output": step_result.get("output", {})
                },
                run_id=run_id
            )
            
            if step_result.get("delivery_status"):
                context["delivery_status"] = step_result["delivery_status"]
            
            await self._save_checkpoint(context)
        
        return {
            "success": True,
            "outputs": context["outputs"],
            "delivery_status": context["delivery_status"]
        }
    
    async def _execute_step(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤"""
        tool_name = step.tool_name
        
        if tool_name not in self.tool_registry:
            return {"success": False, "error": f"工具 {tool_name} 未注册"}
        
        tool = self.tool_registry[tool_name]
        
        inputs = {}
        for key, mapping in step.input_mapping.items():
            if isinstance(mapping, str) and mapping.startswith("$"):
                path = mapping[1:].split(".")
                value = context
                for p in path:
                    value = value.get(p, {})
                inputs[key] = value
            else:
                inputs[key] = mapping
        
        try:
            if asyncio.iscoroutinefunction(tool):
                output = await tool(inputs, context)
            else:
                output = tool(inputs, context)
            
            if step.output_key:
                context["outputs"][step.output_key] = output
            
            delivery_status = "queued_for_delivery"
            if isinstance(output, dict):
                status = output.get("status", "")
                if status == "success":
                    delivery_status = "delivered"
                elif status == "queued_for_delivery":
                    delivery_status = "queued_for_delivery"
            
            return {
                "success": output.get("success", True) if isinstance(output, dict) else True,
                "output": output,
                "delivery_status": delivery_status
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _save_checkpoint(self, context: Dict[str, Any]):
        """保存检查点"""
        await self.checkpoint_repo.save_checkpoint(
            task_id=context["task"].task_id,
            run_id=context["run_id"],
            thread_id=context["thread_id"],
            checkpoint_id=f"cp_{context['current_step']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            snapshot={
                "current_step": context["current_step"],
                "inputs": context["inputs"],
                "outputs": context["outputs"]
            }
        )


class SimpleExecutor:
    """简单执行器（用于测试）"""
    
    def __init__(self):
        self.root = get_project_root()
        self.task_repo = SQLiteTaskRepository()
        self.executor = TaskExecutor(task_repo=self.task_repo)
    
    async def process_queue(self) -> int:
        """处理队列中的任务"""
        queue_file = self.root / "data" / "task_queue.jsonl"
        
        if not queue_file.exists():
            return 0
        
        with open(queue_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return 0
        
        processed = 0
        remaining = []
        
        for line in lines:
            try:
                entry = json.loads(line.strip())
                
                if entry.get("status") == "pending":
                    result = await self.executor.execute_task(entry["task_id"])
                    
                    if result["success"]:
                        print(f"[Executor] 任务执行成功: {entry['task_id']}")
                    else:
                        print(f"[Executor] 任务执行失败: {entry['task_id']} - {result.get('error')}")
                    
                    processed += 1
                else:
                    remaining.append(line)
            
            except Exception as e:
                print(f"[Executor] 处理失败: {e}")
                remaining.append(line)
        
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining)
        
        return processed


if __name__ == "__main__":
    executor = SimpleExecutor()
    asyncio.run(executor.process_queue())
