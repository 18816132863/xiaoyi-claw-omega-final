from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
Token 优化器
V2.7.0 - 2026-04-10

动态优化 Token 消耗
"""

import re
import os
from typing import Dict, List, Tuple
from pathlib import Path

class TokenOptimizer:
    """Token 优化器"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.token_ratio = {
            'en': 4,  # 英文: 4字符/token
            'zh': 2,  # 中文: 2字符/token
        }
    
    def estimate_tokens(self, text: str) -> int:
        """估算 Token 数"""
        # 简单估算
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars
        
        tokens = chinese_chars / self.token_ratio['zh']
        tokens += other_chars / self.token_ratio['en']
        
        return int(tokens)
    
    def optimize_file(self, file_path: Path, max_tokens: int = 2000) -> Tuple[str, int]:
        """优化单个文件"""
        if not file_path.exists():
            return "", 0
        
        content = file_path.read_text()
        original_tokens = self.estimate_tokens(content)
        
        if original_tokens <= max_tokens:
            return content, original_tokens
        
        # 优化策略
        optimized = self._apply_optimizations(content, max_tokens)
        optimized_tokens = self.estimate_tokens(optimized)
        
        return optimized, optimized_tokens
    
    def _apply_optimizations(self, content: str, max_tokens: int) -> str:
        """应用优化策略"""
        lines = content.split('\n')
        result = []
        current_tokens = 0
        
        # 策略1: 保留标题和重要行
        for line in lines:
            line_tokens = self.estimate_tokens(line)
            
            # 保留标题
            if line.startswith('#'):
                result.append(line)
                current_tokens += line_tokens
                continue
            
            # 保留非空行（直到达到限制）
            if line.strip() and current_tokens + line_tokens < max_tokens:
                result.append(line)
                current_tokens += line_tokens
        
        # 添加截断提示
        if current_tokens >= max_tokens:
            result.append("\n... [内容已优化，完整版见原文件]")
        
        return '\n'.join(result)
    
    def get_loading_plan(self) -> Dict[str, Dict]:
        """获取加载计划"""
        return {
            # 立即加载（核心文件）
            "immediate": {
                "files": [
                    "AGENTS.md",
                    "SOUL.md", 
                    "TOOLS.md",
                    "USER.md",
                    "IDENTITY.md",
                    "HEARTBEAT.md"
                ],
                "max_tokens": 8000,
                "priority": 1
            },
            # 按需加载（记忆文件）
            "on_demand": {
                "files": [
                    "MEMORY.md",
                    "memory/*.md"
                ],
                "max_tokens": 3000,
                "priority": 2,
                "trigger": "recall"
            },
            # 延迟加载（技能）
            "lazy": {
                "files": [
                    "skills/*/SKILL.md"
                ],
                "max_tokens": 5000,
                "priority": 3,
                "trigger": "skill_call"
            }
        }
    
    def calculate_startup_tokens(self) -> Dict:
        """计算启动 Token"""
        plan = self.get_loading_plan()
        immediate = plan["immediate"]["files"]
        
        total = 0
        details = {}
        
        for file_name in immediate:
            file_path = self.workspace / file_name
            if file_path.exists():
                content = file_path.read_text()
                tokens = self.estimate_tokens(content)
                total += tokens
                details[file_name] = tokens
        
        return {
            "total": total,
            "target": 8000,
            "status": "ok" if total <= 8000 else "exceeded",
            "details": details
        }
    
    def generate_report(self) -> str:
        """生成优化报告"""
        startup = self.calculate_startup_tokens()
        
        report = []
        report.append("="*50)
        report.append("Token 优化报告")
        report.append("="*50)
        report.append("")
        report.append(f"启动 Token: {startup['total']} (目标: {startup['target']})")
        report.append(f"状态: {'✓ 达标' if startup['status'] == 'ok' else '✗ 超标'}")
        report.append("")
        report.append("文件详情:")
        for file, tokens in startup['details'].items():
            report.append(f"  {file}: {tokens} tokens")
        report.append("")
        report.append("="*50)
        
        return '\n'.join(report)

if __name__ == "__main__":
    optimizer = TokenOptimizer(str(get_project_root()))
    print(optimizer.generate_report())
