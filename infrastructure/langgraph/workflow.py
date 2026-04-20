"""
LangGraph 工作流 V1.0.0

职责：
- 工作流编排
- 状态管理
- 检查点持久化
- 中断/恢复
"""

import json
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.constants import START
    HAS_LANGGRAPH = True
except ImportError:
    HAS_LANGGRAPH = False
    print("[LangGraph] 未安装，使用简化实现")


# 工作流状态
class WorkflowState(TypedDict):
    """工作流状态"""
    task_id: str
    task_type: str
    current_step: int
    total_steps: int
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    status: str
    error: Optional[str]
    retry_count: int
    max_retries: int


class TaskWorkflow:
    """任务工作流"""
    
    def __init__(self):
        self.checkpointer = MemorySaver() if HAS_LANGGRAPH else None
        self.graph = self._build_graph() if HAS_LANGGRAPH else None
        self.root = project_root
    
    def _build_graph(self):
        """构建工作流图"""
        if not HAS_LANGGRAPH:
            return None
        
        # 定义节点
        def validate_node(state: WorkflowState) -> WorkflowState:
            """校验节点"""
            state["status"] = "validating"
            self._save_checkpoint(state)
            return state
        
        def execute_node(state: WorkflowState) -> WorkflowState:
            """执行节点"""
            state["status"] = "executing"
            self._save_checkpoint(state)
            
            # 执行步骤
            import asyncio
            from infrastructure.task_manager import get_task_manager
            
            tm = get_task_manager()
            result = asyncio.run(tm.execute_task(state["task_id"]))
            
            if result.get("success"):
                state["status"] = "succeeded"
                state["outputs"] = result.get("outputs", {})
            else:
                state["status"] = "failed"
                state["error"] = result.get("error")
            
            return state
        
        def retry_node(state: WorkflowState) -> WorkflowState:
            """重试节点"""
            state["retry_count"] += 1
            state["status"] = "retrying"
            self._save_checkpoint(state)
            return state
        
        def success_node(state: WorkflowState) -> WorkflowState:
            """成功节点"""
            state["status"] = "succeeded"
            self._save_checkpoint(state)
            return state
        
        def fail_node(state: WorkflowState) -> WorkflowState:
            """失败节点"""
            state["status"] = "failed"
            self._save_checkpoint(state)
            return state
        
        # 构建图
        builder = StateGraph(WorkflowState)
        
        builder.add_node("validate", validate_node)
        builder.add_node("execute", execute_node)
        builder.add_node("retry", retry_node)
        builder.add_node("success", success_node)
        builder.add_node("fail", fail_node)
        
        # 添加边
        builder.add_edge(START, "validate")
        builder.add_edge("validate", "execute")
        
        # 条件边
        def should_retry(state: WorkflowState) -> str:
            if state["status"] == "failed" and state["retry_count"] < state["max_retries"]:
                return "retry"
            elif state["status"] == "succeeded":
                return "success"
            else:
                return "fail"
        
        builder.add_conditional_edges("execute", should_retry, {
            "retry": "retry",
            "success": "success",
            "fail": "fail"
        })
        
        builder.add_edge("retry", "execute")
        builder.add_edge("success", END)
        builder.add_edge("fail", END)
        
        return builder.compile(checkpointer=self.checkpointer)
    
    def _save_checkpoint(self, state: WorkflowState):
        """保存检查点"""
        checkpoint_file = self.root / "data" / "checkpoints" / f"{state['task_id']}.json"
        checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, default=str, indent=2)
    
    def run(self, task_id: str, task_type: str, inputs: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """运行工作流"""
        initial_state: WorkflowState = {
            "task_id": task_id,
            "task_type": task_type,
            "current_step": 0,
            "total_steps": 0,
            "inputs": inputs,
            "outputs": {},
            "status": "pending",
            "error": None,
            "retry_count": 0,
            "max_retries": max_retries
        }
        
        if self.graph:
            # 使用 LangGraph
            config = {"configurable": {"thread_id": task_id}}
            result = self.graph.invoke(initial_state, config)
            return result
        else:
            # 简化实现
            return self._simple_run(initial_state)
    
    def _simple_run(self, state: WorkflowState) -> WorkflowState:
        """简化执行"""
        import asyncio
        from infrastructure.task_manager import get_task_manager
        
        tm = get_task_manager()
        
        # 执行任务
        result = asyncio.run(tm.execute_task(state["task_id"]))
        
        if result.get("success"):
            state["status"] = "succeeded"
            state["outputs"] = result.get("outputs", {})
        else:
            state["status"] = "failed"
            state["error"] = result.get("error")
        
        self._save_checkpoint(state)
        
        return state
    
    def interrupt(self, task_id: str):
        """中断工作流"""
        # 更新状态为 paused
        checkpoint_file = self.root / "data" / "checkpoints" / f"{task_id}.json"
        
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            state["status"] = "paused"
            
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, default=str, indent=2)
    
    def resume(self, task_id: str) -> Dict[str, Any]:
        """恢复工作流"""
        checkpoint_file = self.root / "data" / "checkpoints" / f"{task_id}.json"
        
        if not checkpoint_file.exists():
            return {"success": False, "error": "检查点不存在"}
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        state["status"] = "resumed"
        
        # 继续执行
        return self._simple_run(state)


# 全局实例
_workflow: Optional[TaskWorkflow] = None


def get_workflow() -> TaskWorkflow:
    """获取工作流实例"""
    global _workflow
    if _workflow is None:
        _workflow = TaskWorkflow()
    return _workflow
