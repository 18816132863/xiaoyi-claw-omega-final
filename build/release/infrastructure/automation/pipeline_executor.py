#!/usr/bin/env python3
"""
流水线执行器 - V1.0.0

执行多阶段流水线任务。
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor


class StageStatus(Enum):
    """阶段状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStatus(Enum):
    """流水线状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class Stage:
    """流水线阶段"""
    id: str
    name: str
    action: Callable
    params: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: StageStatus = StageStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 0


@dataclass
class Pipeline:
    """流水线"""
    id: str
    name: str
    stages: List[Stage]
    status: PipelineStatus = PipelineStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parallel_stages: bool = False


@dataclass
class PipelineResult:
    """流水线结果"""
    pipeline_id: str
    status: PipelineStatus
    stage_results: Dict[str, Any]
    context: Dict[str, Any]
    duration_seconds: float
    error: Optional[str] = None


class PipelineExecutor:
    """流水线执行器"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.pipelines: Dict[str, Pipeline] = {}
        self.results: Dict[str, PipelineResult] = {}
        self.pipeline_counter = 0
        self.stage_counter = 0
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def create_pipeline(self,
                        name: str,
                        stages: List[Dict],
                        parallel_stages: bool = False) -> str:
        """
        创建流水线
        
        Args:
            name: 流水线名称
            stages: 阶段列表
            parallel_stages: 是否并行执行独立阶段
        
        Returns:
            流水线ID
        """
        pipeline_id = f"pipeline_{self.pipeline_counter}"
        self.pipeline_counter += 1
        
        stage_objects = []
        for s in stages:
            stage_id = f"stage_{self.stage_counter}"
            self.stage_counter += 1
            
            stage = Stage(
                id=stage_id,
                name=s.get("name", stage_id),
                action=s.get("action", lambda ctx: None),
                params=s.get("params", {}),
                dependencies=s.get("dependencies", []),
                max_retries=s.get("max_retries", 0)
            )
            stage_objects.append(stage)
        
        pipeline = Pipeline(
            id=pipeline_id,
            name=name,
            stages=stage_objects,
            parallel_stages=parallel_stages
        )
        
        self.pipelines[pipeline_id] = pipeline
        return pipeline_id
    
    def execute(self, pipeline_id: str, context: Dict = None) -> PipelineResult:
        """
        执行流水线
        
        Args:
            pipeline_id: 流水线ID
            context: 执行上下文
        
        Returns:
            执行结果
        """
        pipeline = self.pipelines.get(pipeline_id)
        if not pipeline:
            return PipelineResult(
                pipeline_id=pipeline_id,
                status=PipelineStatus.FAILED,
                stage_results={},
                context={},
                duration_seconds=0,
                error="流水线不存在"
            )
        
        pipeline.status = PipelineStatus.RUNNING
        pipeline.started_at = datetime.now()
        pipeline.context = context or {}
        
        start_time = datetime.now()
        stage_results = {}
        error = None
        
        try:
            if pipeline.parallel_stages:
                self._execute_parallel(pipeline, stage_results)
            else:
                self._execute_sequential(pipeline, stage_results)
            
            # 检查是否所有阶段都完成
            all_completed = all(
                s.status == StageStatus.COMPLETED or s.status == StageStatus.SKIPPED
                for s in pipeline.stages
            )
            
            if all_completed:
                pipeline.status = PipelineStatus.COMPLETED
            else:
                pipeline.status = PipelineStatus.FAILED
                error = "部分阶段执行失败"
                
        except Exception as e:
            pipeline.status = PipelineStatus.FAILED
            error = str(e)
        
        pipeline.completed_at = datetime.now()
        duration = (pipeline.completed_at - start_time).total_seconds()
        
        result = PipelineResult(
            pipeline_id=pipeline_id,
            status=pipeline.status,
            stage_results=stage_results,
            context=pipeline.context,
            duration_seconds=duration,
            error=error
        )
        
        self.results[pipeline_id] = result
        return result
    
    def _execute_sequential(self, pipeline: Pipeline, stage_results: Dict):
        """顺序执行"""
        while True:
            # 找到可执行的阶段
            ready_stages = self._get_ready_stages(pipeline)
            
            if not ready_stages:
                # 检查是否还有未完成的阶段
                pending = [s for s in pipeline.stages if s.status == StageStatus.PENDING]
                if pending:
                    # 有依赖无法满足的阶段
                    for s in pending:
                        s.status = StageStatus.SKIPPED
                        stage_results[s.id] = {"status": "skipped", "reason": "依赖无法满足"}
                break
            
            # 执行阶段
            for stage in ready_stages:
                self._execute_stage(stage, pipeline.context)
                stage_results[stage.id] = {
                    "status": stage.status.value,
                    "result": stage.result,
                    "error": stage.error
                }
                
                if stage.status == StageStatus.FAILED:
                    # 阶段失败，停止执行
                    return
    
    def _execute_parallel(self, pipeline: Pipeline, stage_results: Dict):
        """并行执行"""
        while True:
            ready_stages = self._get_ready_stages(pipeline)
            
            if not ready_stages:
                pending = [s for s in pipeline.stages if s.status == StageStatus.PENDING]
                if pending:
                    for s in pending:
                        s.status = StageStatus.SKIPPED
                        stage_results[s.id] = {"status": "skipped", "reason": "依赖无法满足"}
                break
            
            # 并行执行
            futures = []
            for stage in ready_stages:
                future = self._executor.submit(
                    self._execute_stage, stage, pipeline.context
                )
                futures.append((stage, future))
            
            # 等待完成
            for stage, future in futures:
                future.result()
                stage_results[stage.id] = {
                    "status": stage.status.value,
                    "result": stage.result,
                    "error": stage.error
                }
    
    def _get_ready_stages(self, pipeline: Pipeline) -> List[Stage]:
        """获取可执行的阶段"""
        ready = []
        completed_ids = {
            s.id for s in pipeline.stages 
            if s.status in [StageStatus.COMPLETED, StageStatus.SKIPPED]
        }
        
        for stage in pipeline.stages:
            if stage.status != StageStatus.PENDING:
                continue
            
            # 检查依赖
            if set(stage.dependencies).issubset(completed_ids):
                ready.append(stage)
        
        return ready
    
    def _execute_stage(self, stage: Stage, context: Dict):
        """执行阶段"""
        stage.status = StageStatus.RUNNING
        stage.started_at = datetime.now()
        
        for attempt in range(stage.max_retries + 1):
            try:
                # 合并参数和上下文
                params = {**stage.params, "context": context}
                result = stage.action(**params)
                
                stage.result = result
                stage.status = StageStatus.COMPLETED
                stage.completed_at = datetime.now()
                
                # 更新上下文
                context[stage.id] = result
                
                return
                
            except Exception as e:
                stage.error = str(e)
                stage.retry_count = attempt + 1
                
                if attempt >= stage.max_retries:
                    stage.status = StageStatus.FAILED
                    stage.completed_at = datetime.now()
                    return
    
    def cancel(self, pipeline_id: str) -> bool:
        """取消流水线"""
        pipeline = self.pipelines.get(pipeline_id)
        if pipeline and pipeline.status == PipelineStatus.RUNNING:
            pipeline.status = PipelineStatus.CANCELLED
            return True
        return False
    
    def get_status(self, pipeline_id: str) -> Optional[PipelineStatus]:
        """获取流水线状态"""
        pipeline = self.pipelines.get(pipeline_id)
        return pipeline.status if pipeline else None
    
    def get_result(self, pipeline_id: str) -> Optional[PipelineResult]:
        """获取执行结果"""
        return self.results.get(pipeline_id)
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        status_counts = {}
        for status in PipelineStatus:
            status_counts[status.value] = sum(
                1 for p in self.pipelines.values() if p.status == status
            )
        
        return {
            "total_pipelines": len(self.pipelines),
            "completed": status_counts.get("completed", 0),
            "failed": status_counts.get("failed", 0),
            "running": status_counts.get("running", 0),
            "success_rate": (
                status_counts.get("completed", 0) / len(self.pipelines)
                if self.pipelines else 0
            ),
            "avg_duration": (
                sum(r.duration_seconds for r in self.results.values()) / len(self.results)
                if self.results else 0
            )
        }


# 全局流水线执行器
_pipeline_executor: Optional[PipelineExecutor] = None


def get_pipeline_executor() -> PipelineExecutor:
    """获取全局流水线执行器"""
    global _pipeline_executor
    if _pipeline_executor is None:
        _pipeline_executor = PipelineExecutor()
    return _pipeline_executor
