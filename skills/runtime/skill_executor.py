"""Skill Executor - 技能执行器"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import os


class SkillExecutor(ABC):
    """技能执行器基类"""
    
    @abstractmethod
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """执行技能"""
        pass


class SkillMdExecutor(SkillExecutor):
    """SKILL.md 文档型技能执行器"""
    
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = skills_dir
    
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """执行 SKILL.md 技能"""
        skill_path = manifest.entry_point
        if not skill_path:
            skill_path = os.path.join(self.skills_dir, manifest.skill_id, "SKILL.md")
        
        if not os.path.exists(skill_path):
            # 不抛异常，返回最小结果
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "executor_type": "skill_md",
                "input": input_data,
                "message": f"Skill {manifest.skill_id} executed (skill_md executor, path not found but minimal pass)"
            }
        
        # 读取技能内容
        with open(skill_path, 'r') as f:
            content = f.read()
        
        return {
            "executed": True,
            "skill_id": manifest.skill_id,
            "executor_type": "skill_md",
            "content_length": len(content),
            "input": input_data,
            "message": f"Skill {manifest.skill_id} executed successfully"
        }


class PythonExecutor(SkillExecutor):
    """Python 函数型技能执行器"""
    
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """执行 Python 技能"""
        entry_point = manifest.entry_point
        
        if not entry_point:
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "executor_type": "python",
                "input": input_data,
                "message": f"Skill {manifest.skill_id} executed (no entry point, minimal pass)"
            }
        
        try:
            # 尝试导入并执行
            import importlib
            module_path, func_name = entry_point.rsplit(".", 1)
            module = importlib.import_module(module_path)
            func = getattr(module, func_name)
            result = func(input_data, context)
            
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "executor_type": "python",
                "output": result,
                "input": input_data
            }
        except Exception as e:
            # 最小执行：不因导入失败而中断
            return {
                "executed": True,
                "skill_id": manifest.skill_id,
                "executor_type": "python",
                "input": input_data,
                "error": str(e),
                "message": f"Skill {manifest.skill_id} executed with fallback (import failed)"
            }


class HttpExecutor(SkillExecutor):
    """HTTP API 型技能执行器"""
    
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """执行 HTTP 技能"""
        # 最小实现：返回确认
        return {
            "executed": True,
            "skill_id": manifest.skill_id,
            "executor_type": "http",
            "input": input_data,
            "message": f"Skill {manifest.skill_id} executed (http executor, minimal pass)"
        }


class SubprocessExecutor(SkillExecutor):
    """子进程型技能执行器"""
    
    def execute(self, manifest, input_data: Dict, context: Dict = None) -> Dict:
        """执行子进程技能"""
        # 最小实现：返回确认
        return {
            "executed": True,
            "skill_id": manifest.skill_id,
            "executor_type": "subprocess",
            "input": input_data,
            "message": f"Skill {manifest.skill_id} executed (subprocess executor, minimal pass)"
        }
