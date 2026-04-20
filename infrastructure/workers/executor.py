"""
任务执行器 V1.0.0

职责：
- 从队列拉取任务
- 执行任务步骤
- 记录执行结果
- 处理失败重试
"""

import asyncio
import json
import uuid
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from pathlib import Path

from domain.tasks import (
    TaskSpec,
    TaskStatus,
    StepStatus,
    EventType,
)
from infrastructure.storage.repositories import (
    SQLiteTaskRepository,
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
        event_repo: Optional[SQLiteTaskEventRepository] = None,
        checkpoint_repo: Optional[SQLiteCheckpointRepository] = None,
        tool_registry: Optional[Dict[str, Callable]] = None
    ):
        self.task_repo = task_repo or SQLiteTaskRepository()
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
        """
        # 1. 加载任务
        task = await self.task_repo.get(task_id)
        if not task:
            return {"success": False, "error": "任务不存在"}
        
        # 2. 检查状态
        if task.status not in (TaskStatus.QUEUED, TaskStatus.RESUMED):
            return {"success": False, "error": f"任务状态 {task.status.value} 不可执行"}
        
        # 3. 更新状态
        await self.task_repo.update(task_id, {"status": TaskStatus.RUNNING.value})
        
        # 4. 记录事件
        await self.event_repo.record_event(
            task_id=task_id,
            event_type=EventType.STARTED.value,
            event_payload={}
        )
        
        # 5. 创建运行记录
        run_id = str(uuid.uuid4())
        thread_id = f"thread_{task_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 6. 执行步骤
        result = await self._execute_steps(task, run_id, thread_id)
        
        # 7. 更新最终状态
        if result["success"]:
            await self.task_repo.update(task_id, {
                "status": TaskStatus.SUCCEEDED.value,
                "last_run_at": datetime.now().isoformat()
            })
            
            await self.event_repo.record_event(
                task_id=task_id,
                event_type=EventType.SUCCEEDED.value,
                event_payload={"run_id": run_id}
            )
        else:
            # 检查是否需要重试
            task = await self.task_repo.get(task_id)
            attempt_count = task.attempt_count + 1 if hasattr(task, 'attempt_count') else 1
            
            if attempt_count < task.retry_policy.max_attempts:
                await self.task_repo.update(task_id, {
                    "status": TaskStatus.WAITING_RETRY.value,
                    "attempt_count": attempt_count,
                    "last_error": result.get("error", "")
                })
                
                await self.event_repo.record_event(
                    task_id=task_id,
                    event_type=EventType.RETRYING.value,
                    event_payload={
                        "attempt": attempt_count,
                        "max_attempts": task.retry_policy.max_attempts,
                        "error": result.get("error", "")
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
            "inputs": task.inputs.copy(),
            "outputs": {},
            "current_step": 0
        }
        
        # 保存检查点
        await self._save_checkpoint(context)
        
        for step in task.steps:
            context["current_step"] = step.step_index
            
            # 记录步骤开始
            await self.event_repo.record_event(
                task_id=task.task_id,
                event_type=EventType.STEP_STARTED.value,
                event_payload={
                    "run_id": run_id,
                    "step_index": step.step_index,
                    "step_name": step.step_name
                }
            )
            
            # 执行步骤
            step_result = await self._execute_step(step, context)
            
            if not step_result["success"]:
                # 记录步骤失败
                await self.event_repo.record_event(
                    task_id=task.task_id,
                    event_type=EventType.STEP_FAILED.value,
                    event_payload={
                        "run_id": run_id,
                        "step_index": step.step_index,
                        "error": step_result.get("error", "")
                    }
                )
                
                return {
                    "success": False,
                    "error": f"步骤 {step.step_name} 失败: {step_result.get('error', '')}",
                    "step_index": step.step_index
                }
            
            # 记录步骤完成
            await self.event_repo.record_event(
                task_id=task.task_id,
                event_type=EventType.STEP_COMPLETED.value,
                event_payload={
                    "run_id": run_id,
                    "step_index": step.step_index,
                    "output": step_result.get("output", {})
                }
            )
            
            # 保存检查点
            await self._save_checkpoint(context)
        
        return {"success": True, "outputs": context["outputs"]}
    
    async def _execute_step(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个步骤"""
        tool_name = step.tool_name
        
        # 检查工具是否注册
        if tool_name not in self.tool_registry:
            return {
                "success": False,
                "error": f"工具 {tool_name} 未注册"
            }
        
        tool = self.tool_registry[tool_name]
        
        # 准备输入
        inputs = {}
        for key, mapping in step.input_mapping.items():
            if isinstance(mapping, str) and mapping.startswith("$"):
                # 从上下文获取
                path = mapping[1:].split(".")
                value = context
                for p in path:
                    value = value.get(p, {})
                inputs[key] = value
            else:
                inputs[key] = mapping
        
        try:
            # 执行工具
            if asyncio.iscoroutinefunction(tool):
                output = await tool(inputs, context)
            else:
                output = tool(inputs, context)
            
            # 保存输出
            if step.output_key:
                context["outputs"][step.output_key] = output
            
            return {"success": True, "output": output}
        
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
        
        # 读取队列
        with open(queue_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return 0
        
        # 处理任务
        processed = 0
        remaining = []
        
        for line in lines:
            try:
                entry = json.loads(line.strip())
                
                if entry.get("status") == "pending":
                    # 执行任务
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
        
        # 更新队列文件
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.writelines(remaining)
        
        return processed


if __name__ == "__main__":
    executor = SimpleExecutor()
    asyncio.run(executor.process_queue())
