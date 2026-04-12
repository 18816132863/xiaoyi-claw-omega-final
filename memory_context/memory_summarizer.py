#!/usr/bin/env python3
"""
记忆自动总结器
V2.7.0 - 2026-04-10

借鉴 LegnaChat 的记忆总结机制
"""

import os
import re
from typing import Optional
from pathlib import Path
from datetime import datetime

class MemorySummarizer:
    """记忆自动总结器"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        self.short_memory_file = self.memory_dir / "short.md"
        self.long_memory_file = self.memory_dir / "long.md"
        self.log_dir = self.workspace / "log"
        
        # 配置
        self.config = {
            "max_short_memory_lines": 50,
            "max_long_memory_lines": 200,
            "summary_trigger_lines": 100,
        }
    
    def summarize_session(self, session_log: str) -> str:
        """总结会话内容"""
        if not session_log.strip():
            return ""
        
        # 提取关键信息
        key_points = self._extract_key_points(session_log)
        
        # 生成总结
        summary = self._generate_summary(key_points)
        
        return summary
    
    def _extract_key_points(self, log: str) -> list:
        """提取关键点"""
        points = []
        
        # 提取用户偏好
        preference_patterns = [
            r"我喜欢(.+)",
            r"我想要(.+)",
            r"我的(.+)是",
            r"记住(.+)",
        ]
        
        for pattern in preference_patterns:
            matches = re.findall(pattern, log)
            points.extend([f"用户偏好: {m}" for m in matches])
        
        # 提取重要决定
        decision_patterns = [
            r"决定(.+)",
            r"选择(.+)",
            r"确定(.+)",
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, log)
            points.extend([f"重要决定: {m}" for m in matches])
        
        # 提取任务完成
        task_patterns = [
            r"完成了(.+)",
            r"成功(.+)",
            r"已(.+)",
        ]
        
        for pattern in task_patterns:
            matches = re.findall(pattern, log)
            points.extend([f"任务完成: {m}" for m in matches])
        
        return points[:20]  # 限制数量
    
    def _generate_summary(self, points: list) -> str:
        """生成总结"""
        if not points:
            return ""
        
        date = datetime.now().strftime("%Y-%m-%d")
        summary = f"\n## [{date}] 会话总结\n\n"
        
        for point in points:
            summary += f"- {point}\n"
        
        return summary
    
    def update_short_memory(self, new_content: str):
        """更新短期记忆"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 读取现有内容
        existing = ""
        if self.short_memory_file.exists():
            existing = self.short_memory_file.read_text(encoding='utf-8')
        
        # 合并并限制行数
        combined = existing + new_content
        lines = combined.split('\n')
        
        if len(lines) > self.config["max_short_memory_lines"]:
            # 保留最近的行
            lines = lines[-self.config["max_short_memory_lines"]:]
        
        # 写入
        self.short_memory_file.write_text('\n'.join(lines), encoding='utf-8')
    
    def update_long_memory(self, important_content: str):
        """更新长期记忆"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # 追加到长期记忆
        with open(self.long_memory_file, 'a', encoding='utf-8') as f:
            f.write(important_content + "\n")
        
        # 检查是否需要压缩
        if self.long_memory_file.exists():
            content = self.long_memory_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            if len(lines) > self.config["max_long_memory_lines"]:
                # 压缩旧内容
                self._compress_long_memory(lines)
    
    def _compress_long_memory(self, lines: list):
        """压缩长期记忆"""
        # 保留最近的内容
        recent = lines[-self.config["max_long_memory_lines"]:]
        
        # 归档旧内容
        archive_dir = self.memory_dir / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        archive_file = archive_dir / f"long_{datetime.now().strftime('%Y%m%d')}.md"
        archive_file.write_text('\n'.join(lines[:-self.config["max_long_memory_lines"]]), encoding='utf-8')
        
        # 更新主文件
        self.long_memory_file.write_text('\n'.join(recent), encoding='utf-8')
    
    def get_memory_for_context(self) -> str:
        """获取用于上下文的记忆"""
        memory = ""
        
        # 读取短期记忆
        if self.short_memory_file.exists():
            short = self.short_memory_file.read_text(encoding='utf-8')
            if short.strip():
                memory += f"## 短期记忆\n{short}\n\n"
        
        # 读取长期记忆
        if self.long_memory_file.exists():
            long = self.long_memory_file.read_text(encoding='utf-8')
            if long.strip():
                memory += f"## 长期记忆\n{long}\n\n"
        
        return memory

# 全局实例
_summarizer: Optional[MemorySummarizer] = None

def get_summarizer() -> MemorySummarizer:
    """获取全局总结器"""
    global _summarizer
    if _summarizer is None:
        try:
            from infrastructure.path_resolver import get_project_root
            workspace = str(get_project_root())
        except ImportError:
            workspace = "."
        _summarizer = MemorySummarizer(workspace)
    return _summarizer

def summarize_session(log: str) -> str:
    """总结会话（便捷函数）"""
    return get_summarizer().summarize_session(log)
