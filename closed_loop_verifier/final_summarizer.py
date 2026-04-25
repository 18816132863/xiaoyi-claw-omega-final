"""最终总结器"""

from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExecutionSummary:
    """执行总结"""
    goal: str
    success: bool
    total_steps: int
    completed_steps: int
    failed_steps: int
    elapsed_seconds: int
    message: str
    recommendations: List[str]


class FinalSummarizer:
    """最终总结器"""
    
    def summarize(
        self,
        goal: str,
        steps: List[Dict[str, Any]],
        start_time: str,
        end_time: str,
    ) -> ExecutionSummary:
        """生成总结"""
        total = len(steps)
        completed = sum(1 for s in steps if s.get("status") == "completed")
        failed = sum(1 for s in steps if s.get("status") == "failed")
        
        # 计算耗时
        try:
            start = datetime.fromisoformat(start_time)
            end = datetime.fromisoformat(end_time)
            elapsed = int((end - start).total_seconds())
        except:
            elapsed = 0
        
        # 判断成功
        success = failed == 0 and completed == total
        
        # 生成消息
        if success:
            message = f"✅ 任务完成！共执行 {total} 个步骤，耗时 {elapsed} 秒。"
        elif failed > 0:
            message = f"⚠️ 任务部分完成。成功 {completed}/{total}，失败 {failed}。"
        else:
            message = f"❌ 任务失败。"
        
        # 生成建议
        recommendations = self._generate_recommendations(steps, success)
        
        return ExecutionSummary(
            goal=goal,
            success=success,
            total_steps=total,
            completed_steps=completed,
            failed_steps=failed,
            elapsed_seconds=elapsed,
            message=message,
            recommendations=recommendations,
        )
    
    def _generate_recommendations(self, steps: List[Dict[str, Any]], success: bool) -> List[str]:
        """生成建议"""
        recommendations = []
        
        if not success:
            failed_steps = [s for s in steps if s.get("status") == "failed"]
            for step in failed_steps:
                recommendations.append(f"步骤 {step.get('step_id')} 失败，可尝试手动执行")
        
        # 检查是否有高风险步骤
        high_risk = [s for s in steps if s.get("risk_level") in ["L3", "L4"]]
        if high_risk:
            recommendations.append("本次执行包含高风险操作，建议复核结果")
        
        return recommendations
    
    def format_for_user(self, summary: ExecutionSummary) -> str:
        """格式化为用户友好的文本"""
        lines = [
            summary.message,
            "",
            f"目标: {summary.goal}",
            f"步骤: {summary.completed_steps}/{summary.total_steps} 完成",
            f"耗时: {summary.elapsed_seconds} 秒",
        ]
        
        if summary.recommendations:
            lines.append("")
            lines.append("建议:")
            for rec in summary.recommendations:
                lines.append(f"  • {rec}")
        
        return "\n".join(lines)
