#!/usr/bin/env python3
"""
记忆管理器
V2.7.0 - 2026-04-10

智能记忆管理，优化 Token 消耗
"""

import os
import re
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque

@dataclass
class MemoryEntry:
    """记忆条目"""
    content: str
    timestamp: float
    memory_type: str  # short_term, working, long_term
    tags: List[str] = field(default_factory=list)
    importance: int = 0  # 0-10

class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.memory_dir = self.workspace / "memory"
        
        # 短期记忆 (会话级)
        self.short_term: deque = deque(maxlen=100)
        
        # 工作记忆 (任务级)
        self.working: Dict[str, List[MemoryEntry]] = {}
        
        # 配置
        self.config = {
            "short_term_ttl": 3600,      # 1小时
            "working_ttl": 86400,        # 24小时
            "max_tokens_per_recall": 2000,
            "compression_threshold": 7,  # 天
        }
    
    def store(self, content: str, memory_type: str = "long_term", 
              tags: List[str] = None, importance: int = 5) -> bool:
        """存储记忆"""
        entry = MemoryEntry(
            content=content,
            timestamp=time.time(),
            memory_type=memory_type,
            tags=tags or [],
            importance=importance
        )
        
        if memory_type == "short_term":
            self.short_term.append(entry)
            return True
        
        elif memory_type == "working":
            task_id = f"task_{int(time.time())}"
            if task_id not in self.working:
                self.working[task_id] = []
            self.working[task_id].append(entry)
            return True
        
        else:  # long_term
            return self._store_long_term(entry)
    
    def _store_long_term(self, entry: MemoryEntry) -> bool:
        """存储长期记忆"""
        try:
            # 确保目录存在
            self.memory_dir.mkdir(parents=True, exist_ok=True)
            
            # 按日期存储
            date_str = datetime.now().strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.md"
            
            # 格式化内容
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted = f"\n## [{timestamp}] {' '.join(entry.tags)}\n{entry.content}\n"
            
            # 追加到文件
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write(formatted)
            
            return True
        except Exception as e:
            print(f"存储长期记忆失败: {e}")
            return False
    
    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """检索记忆"""
        results = []
        
        # 1. 搜索短期记忆
        for entry in reversed(self.short_term):
            if self._matches(entry.content, query):
                results.append({
                    "content": entry.content,
                    "type": "short_term",
                    "timestamp": entry.timestamp,
                    "relevance": self._calculate_relevance(entry.content, query)
                })
        
        # 2. 搜索工作记忆
        for task_id, entries in self.working.items():
            for entry in reversed(entries):
                if self._matches(entry.content, query):
                    results.append({
                        "content": entry.content,
                        "type": "working",
                        "timestamp": entry.timestamp,
                        "relevance": self._calculate_relevance(entry.content, query)
                    })
        
        # 3. 搜索长期记忆
        long_term = self._search_files(query)
        results.extend(long_term)
        
        # 排序并限制数量
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:limit]
    
    def _matches(self, content: str, query: str) -> bool:
        """检查是否匹配"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 简单关键词匹配
        keywords = query_lower.split()
        return any(kw in content_lower for kw in keywords)
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """计算相关性"""
        score = 0.0
        query_lower = query.lower()
        content_lower = content.lower()
        
        # 关键词匹配
        for word in query_lower.split():
            if word in content_lower:
                score += 1.0
        
        # 完全匹配加分
        if query_lower in content_lower:
            score += 2.0
        
        return score
    
    def _search_files(self, query: str) -> List[Dict]:
        """搜索记忆文件"""
        results = []
        
        if not self.memory_dir.exists():
            return results
        
        # 搜索最近7天的文件
        for i in range(7):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            memory_file = self.memory_dir / f"{date_str}.md"
            
            if memory_file.exists():
                content = memory_file.read_text(encoding='utf-8')
                if self._matches(content, query):
                    # 提取相关段落
                    relevant = self._extract_relevant(content, query)
                    results.append({
                        "content": relevant,
                        "type": "long_term",
                        "date": date_str,
                        "relevance": self._calculate_relevance(content, query)
                    })
        
        return results
    
    def _extract_relevant(self, content: str, query: str) -> str:
        """提取相关内容"""
        lines = content.split('\n')
        relevant = []
        
        for i, line in enumerate(lines):
            if self._matches(line, query):
                # 提取上下文
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                relevant.extend(lines[start:end])
                relevant.append("---")
        
        return '\n'.join(relevant[:20])  # 限制长度
    
    def get_context_hint(self, query: str) -> Optional[str]:
        """获取上下文提示"""
        # 检测触发模式
        trigger_patterns = {
            "recall": ["记得", "上次", "之前", "以前", "recall", "last time"],
            "preference": ["我喜欢", "我想要", "我的", "I like", "my"],
            "context": ["继续", "接着", "刚才", "continue", "just now"],
        }
        
        for trigger_type, patterns in trigger_patterns.items():
            if any(p in query.lower() for p in patterns):
                memories = self.recall(query, limit=3)
                if memories:
                    return self._format_hint(memories)
        
        return None
    
    def _format_hint(self, memories: List[Dict]) -> str:
        """格式化提示"""
        lines = ["📚 记忆提示:"]
        
        for mem in memories:
            if mem["type"] == "short_term":
                lines.append(f"- 最近: {mem['content'][:100]}...")
            elif mem["type"] == "working":
                lines.append(f"- 任务: {mem['content'][:100]}...")
            else:
                lines.append(f"- {mem.get('date', '历史')}: {mem['content'][:100]}...")
        
        return '\n'.join(lines)
    
    def cleanup(self):
        """清理过期记忆"""
        now = time.time()
        
        # 清理短期记忆
        while self.short_term:
            if now - self.short_term[0].timestamp > self.config["short_term_ttl"]:
                self.short_term.popleft()
            else:
                break
        
        # 清理工作记忆
        expired_tasks = []
        for task_id, entries in self.working.items():
            if entries and now - entries[0].timestamp > self.config["working_ttl"]:
                expired_tasks.append(task_id)
        
        for task_id in expired_tasks:
            del self.working[task_id]
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "short_term_count": len(self.short_term),
            "working_tasks": len(self.working),
            "long_term_files": len(list(self.memory_dir.glob("*.md"))) if self.memory_dir.exists() else 0,
            "config": self.config
        }

# 全局实例
_manager: Optional[MemoryManager] = None

def get_memory_manager() -> MemoryManager:
    """获取全局记忆管理器"""
    global _manager
    if _manager is None:
        try:
            from infrastructure.path_resolver import get_project_root
            workspace = str(get_project_root())
        except ImportError:
            workspace = "."
        _manager = MemoryManager(workspace)
    return _manager

def store_memory(content: str, memory_type: str = "long_term", **kwargs) -> bool:
    """存储记忆（便捷函数）"""
    return get_memory_manager().store(content, memory_type, **kwargs)

def recall_memory(query: str, limit: int = 5) -> List[Dict]:
    """检索记忆（便捷函数）"""
    return get_memory_manager().recall(query, limit)

def get_context_hint(query: str) -> Optional[str]:
    """获取上下文提示（便捷函数）"""
    return get_memory_manager().get_context_hint(query)
