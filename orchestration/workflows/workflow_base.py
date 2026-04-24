#!/usr/bin/env python3
"""
工作流基类 - V2.8.0

每个工作流包必须包含：
- 工作流名称
- 适用场景
- 输入参数模板
- 前置条件检查
- 调用技能清单
- 默认执行顺序
- 失败回退逻辑
- 输出格式模板
- 结果校验规则
- 完成判定标准
"""

import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class WorkflowStepStatus(Enum):
    """工作流步骤状态（与 domain.tasks.specs.StepStatus 不同）"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    """工作流步骤"""
    name: str
    description: str
    skill: Optional[str]
    status: str
    start_time: Optional[str]
    end_time: Optional[str]
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error: Optional[str]
    fallback_used: bool

@dataclass
class WorkflowResult:
    """工作流结果"""
    workflow_name: str
    status: str
    start_time: str
    end_time: Optional[str]
    steps: List[Dict]
    output: Dict[str, Any]
    quality_score: float
    error: Optional[str]

class WorkflowBase(ABC):
    """工作流基类"""
    
    # 子类必须定义
    name: str = "base_workflow"
    description: str = "基础工作流"
    version: str = "1.0.0"
    applicable_scenarios: List[str] = []
    required_skills: List[str] = []
    
    def __init__(self):
        self.status = WorkflowStatus.PENDING
        self.steps: List[WorkflowStep] = []
        self.start_time: Optional[str] = None
        self.end_time: Optional[str] = None
        self.output: Dict[str, Any] = {}
        self.error: Optional[str] = None
        self.logs: List[str] = []
    
    @abstractmethod
    def get_input_template(self) -> Dict[str, Any]:
        """获取输入参数模板"""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict) -> tuple:
        """验证输入参数"""
        pass
    
    @abstractmethod
    def get_execution_order(self) -> List[str]:
        """获取执行顺序"""
        pass
    
    @abstractmethod
    def get_output_template(self) -> Dict[str, Any]:
        """获取输出格式模板"""
        pass
    
    @abstractmethod
    def get_validation_rules(self) -> Dict[str, Any]:
        """获取结果校验规则"""
        pass
    
    @abstractmethod
    def get_completion_criteria(self) -> List[str]:
        """获取完成判定标准"""
        pass
    
    def check_prerequisites(self) -> tuple:
        """检查前置条件"""
        missing_skills = []
        for skill in self.required_skills:
            # 简化检查：只检查技能目录是否存在
            skill_dir = Path(f"skills/{skill}")
            if not skill_dir.exists():
                missing_skills.append(skill)
        
        if missing_skills:
            return False, f"缺少技能: {missing_skills}"
        return True, "前置条件满足"
    
    def get_fallback_logic(self, step_name: str, error: str) -> Optional[str]:
        """获取失败回退逻辑"""
        return None
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    def add_step(self, name: str, description: str, skill: str = None):
        """添加步骤"""
        step = WorkflowStep(
            name=name,
            description=description,
            skill=skill,
            status=WorkflowStepStatus.PENDING.value,
            start_time=None,
            end_time=None,
            input_data={},
            output_data={},
            error=None,
            fallback_used=False
        )
        self.steps.append(step)
    
    def start_step(self, step_name: str):
        """开始步骤"""
        for step in self.steps:
            if step.name == step_name:
                step.status = WorkflowStepStatus.RUNNING.value
                step.start_time = datetime.now().isoformat()
                self.log(f"开始步骤: {step_name}")
                break
    
    def complete_step(self, step_name: str, output: Dict = None):
        """完成步骤"""
        for step in self.steps:
            if step.name == step_name:
                step.status = WorkflowStepStatus.SUCCESS.value
                step.end_time = datetime.now().isoformat()
                if output:
                    step.output_data = output
                self.log(f"完成步骤: {step_name}")
                break
    
    def fail_step(self, step_name: str, error: str, use_fallback: bool = False):
        """失败步骤"""
        for step in self.steps:
            if step.name == step_name:
                step.status = WorkflowStepStatus.FAILED.value
                step.end_time = datetime.now().isoformat()
                step.error = error
                step.fallback_used = use_fallback
                self.log(f"步骤失败: {step_name} - {error}")
                break
    
    def execute(self, input_data: Dict) -> WorkflowResult:
        """执行工作流"""
        self.start_time = datetime.now().isoformat()
        self.status = WorkflowStatus.RUNNING
        self.log(f"开始工作流: {self.name}")
        
        # 验证输入
        valid, msg = self.validate_input(input_data)
        if not valid:
            self.status = WorkflowStatus.FAILED
            self.error = f"输入验证失败: {msg}"
            return self._create_result()
        
        # 检查前置条件
        ready, msg = self.check_prerequisites()
        if not ready:
            self.status = WorkflowStatus.FAILED
            self.error = f"前置条件不满足: {msg}"
            return self._create_result()
        
        # 执行步骤
        execution_order = self.get_execution_order()
        for step_name in execution_order:
            try:
                self.start_step(step_name)
                # 子类实现具体执行逻辑
                success = self.execute_step(step_name, input_data)
                if success:
                    self.complete_step(step_name)
                else:
                    # 尝试回退
                    fallback = self.get_fallback_logic(step_name, "执行失败")
                    if fallback:
                        self.log(f"使用回退: {fallback}")
                        self.fail_step(step_name, "执行失败", use_fallback=True)
                    else:
                        self.fail_step(step_name, "执行失败")
                        self.status = WorkflowStatus.FAILED
                        break
            except Exception as e:
                self.fail_step(step_name, str(e))
                self.status = WorkflowStatus.FAILED
                break
        
        if self.status == WorkflowStatus.RUNNING:
            self.status = WorkflowStatus.COMPLETED
        
        self.end_time = datetime.now().isoformat()
        self.log(f"工作流结束: {self.name} - {self.status.value}")
        
        return self._create_result()
    
    @abstractmethod
    def execute_step(self, step_name: str, input_data: Dict) -> bool:
        """执行具体步骤 - 子类实现"""
        pass
    
    def _create_result(self) -> WorkflowResult:
        """创建结果"""
        return WorkflowResult(
            workflow_name=self.name,
            status=self.status.value,
            start_time=self.start_time,
            end_time=self.end_time,
            steps=[asdict(s) for s in self.steps],
            output=self.output,
            quality_score=self._calculate_quality(),
            error=self.error
        )
    
    def _calculate_quality(self) -> float:
        """计算质量分数"""
        if not self.steps:
            return 0.0
        
        success_count = sum(1 for s in self.steps if s.status == WorkflowStepStatus.SUCCESS.value)
        fallback_count = sum(1 for s in self.steps if s.fallback_used)
        
        base_score = success_count / len(self.steps)
        fallback_penalty = fallback_count * 0.1
        
        return max(0, base_score - fallback_penalty)
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            f"# 工作流报告: {self.name}",
            "",
            f"**状态**: {self.status.value}",
            f"**开始时间**: {self.start_time}",
            f"**结束时间**: {self.end_time}",
            f"**质量分数**: {self._calculate_quality():.2f}",
            "",
            "## 步骤详情",
            ""
        ]
        
        for step in self.steps:
            status_emoji = {
                WorkflowStepStatus.SUCCESS.value: "✅",
                WorkflowStepStatus.FAILED.value: "❌",
                WorkflowStepStatus.RUNNING.value: "🔄",
                WorkflowStepStatus.PENDING.value: "⏳",
                WorkflowStepStatus.SKIPPED.value: "⏭️"
            }.get(step.status, "❓")
            
            lines.append(f"### {status_emoji} {step.name}")
            lines.append(f"- 描述: {step.description}")
            lines.append(f"- 状态: {step.status}")
            if step.error:
                lines.append(f"- 错误: {step.error}")
            if step.fallback_used:
                lines.append(f"- 使用了回退")
            lines.append("")
        
        return "\n".join(lines)
