"""记忆压缩器 - V1.0.0"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
from infrastructure.path_resolver import get_project_root

class MemoryCompressor:
    """记忆压缩器 - 长期记忆压缩存储"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.memory_dir = self.workspace / "memory"
        self.compressed_dir = self.memory_dir / "compressed"
        self.compressed_dir.mkdir(parents=True, exist_ok=True)
    
    def compress_old_memories(self, days: int = 7) -> Dict:
        """压缩旧记忆"""
        cutoff = datetime.now() - timedelta(days=days)
        compressed = {"files": 0, "entries": 0, "bytes_saved": 0}
        
        for memory_file in self.memory_dir.glob("*.md"):
            if memory_file.name == "compressed":
                continue
            
            # 检查日期
            try:
                file_date = datetime.strptime(memory_file.stem, "%Y-%m-%d")
                if file_date < cutoff:
                    # 压缩
                    content = memory_file.read_text()
                    compressed_content = self._compress_content(content)
                    
                    # 保存压缩版本
                    compressed_file = self.compressed_dir / f"{memory_file.stem}.json"
                    with open(compressed_file, "w") as f:
                        json.dump({
                            "original_size": len(content),
                            "compressed_size": len(json.dumps(compressed_content)),
                            "date": memory_file.stem,
                            "summary": compressed_content
                        }, f)
                    
                    compressed["files"] += 1
                    compressed["bytes_saved"] += len(content) - len(json.dumps(compressed_content))
            except:
                pass
        
        return compressed
    
    def _compress_content(self, content: str) -> Dict:
        """压缩内容"""
        lines = content.split("\n")
        
        # 提取标题和关键信息
        titles = [l for l in lines if l.startswith("##")]
        tasks = [l for l in lines if "完成" in l or "创建" in l or "更新" in l]
        
        return {
            "titles": titles[:10],
            "key_tasks": tasks[:20],
            "line_count": len(lines),
            "char_count": len(content)
        }
    
    def get_stats(self) -> Dict:
        """获取统计"""
        original_size = sum(
            f.stat().st_size 
            for f in self.memory_dir.glob("*.md")
        )
        compressed_size = sum(
            f.stat().st_size 
            for f in self.compressed_dir.glob("*.json")
        )
        
        return {
            "original_files": len(list(self.memory_dir.glob("*.md"))),
            "compressed_files": len(list(self.compressed_dir.glob("*.json"))),
            "original_size": original_size,
            "compressed_size": compressed_size,
            "compression_ratio": 1 - (compressed_size / max(1, original_size))
        }
