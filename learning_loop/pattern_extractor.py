"""模式提取器"""

from typing import Dict, Any, List
from .execution_memory import ExecutionRecord


class PatternExtractor:
    """模式提取器"""
    
    @staticmethod
    def extract_goal_pattern(goal: str) -> str:
        """提取目标模式"""
        # 简单的模式提取
        goal_lower = goal.lower()
        
        patterns = {
            "提醒": "reminder",
            "日程": "calendar",
            "备忘": "note",
            "通知": "notification",
            "短信": "message",
            "电话": "phone",
            "闹钟": "alarm",
            "照片": "photo",
            "文件": "file",
            "联系人": "contact",
        }
        
        for kw, pattern in patterns.items():
            if kw in goal_lower:
                return pattern
        
        return "general"
    
    @staticmethod
    def extract_success_patterns(records: List[ExecutionRecord]) -> List[Dict[str, Any]]:
        """提取成功模式"""
        patterns = []
        
        for record in records:
            if record.final_result != "success":
                continue
            
            pattern = {
                "goal_pattern": PatternExtractor.extract_goal_pattern(record.goal),
                "plan_template": record.plan,
                "capabilities": record.capabilities_used,
                "skills": record.skills_used,
                "avg_step_time": sum(record.step_timings.values()) / len(record.step_timings) if record.step_timings else 0,
                "confirmations": len(record.confirmations_needed),
            }
            patterns.append(pattern)
        
        return patterns
    
    @staticmethod
    def extract_failure_signatures(records: List[ExecutionRecord]) -> List[Dict[str, Any]]:
        """提取失败特征"""
        signatures = []
        
        for record in records:
            if not record.failed_steps:
                continue
            
            signature = {
                "goal_pattern": PatternExtractor.extract_goal_pattern(record.goal),
                "failed_steps": record.failed_steps,
                "fallback_occurred": record.fallback_occurred,
                "result_uncertain": record.result_uncertain,
            }
            signatures.append(signature)
        
        return signatures
