"""Prompt 结构化摘要装配器 - V4.3.1

不再截断代码片段，而是装配职责/边界/IO/约束摘要。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class SkillSummary:
    """技能摘要"""
    id: str
    name: str
    purpose: str          # 职责
    boundary: str         # 边界
    inputs: List[str]     # 输入
    outputs: List[str]    # 输出
    constraints: List[str]  # 约束

class PromptBuilder:
    """Prompt 构建器"""
    
    def __init__(self, token_budget: int = 2000):
        self.token_budget = token_budget
        self.used_tokens = 0
    
    def build_context(self, summaries: List[SkillSummary]) -> str:
        """构建上下文"""
        lines = ["# 可用技能摘要\n"]
        
        for summary in summaries:
            if self.used_tokens >= self.token_budget:
                break
            
            section = self._format_summary(summary)
            lines.append(section)
            self.used_tokens += len(section) // 4  # 估算 token
        
        return "\n".join(lines)
    
    def _format_summary(self, s: SkillSummary) -> str:
        """格式化摘要"""
        return f"""## {s.name} ({s.id})
- 职责: {s.purpose}
- 输入: {', '.join(s.inputs[:3])}
- 输出: {', '.join(s.outputs[:3])}
- 约束: {', '.join(s.constraints[:2])}
"""
    
    def build_skill_prompt(self, summary: SkillSummary, user_input: str) -> str:
        """构建技能调用 prompt"""
        return f"""你是 {summary.name}。

职责: {summary.purpose}

输入要求:
{chr(10).join(f'- {i}' for i in summary.inputs)}

输出格式:
{chr(10).join(f'- {o}' for o in summary.outputs)}

约束:
{chr(10).join(f'- {c}' for c in summary.constraints)}

用户输入: {user_input}
"""

# 全局访问
_builder = None

def get_prompt_builder() -> PromptBuilder:
    global _builder
    if _builder is None:
        _builder = PromptBuilder()
    return _builder
