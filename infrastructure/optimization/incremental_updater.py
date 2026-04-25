"""增量更新器 - V1.0.0"""

from typing import Dict, Set, Optional, List
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import json
import hashlib
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FileState:
    """文件状态"""
    path: str
    mtime: float
    size: int
    checksum: str

class IncrementalUpdater:
    """增量更新器 - 只更新变化的部分"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.state_file = self.workspace / ".cache" / "file_states.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.file_states: Dict[str, FileState] = {}
        self._load_states()
    
    def _load_states(self):
        """加载状态"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                data = json.load(f)
            for path, state in data.items():
                self.file_states[path] = FileState(**state)
    
    def _save_states(self):
        """保存状态"""
        data = {
            path: {
                "path": state.path,
                "mtime": state.mtime,
                "size": state.size,
                "checksum": state.checksum
            }
            for path, state in self.file_states.items()
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f)
    
    def _compute_checksum(self, path: Path) -> str:
        """计算校验和"""
        try:
            content = path.read_bytes()
            return hashlib.md5(content).hexdigest()[:16]
        except:
            return ""
    
    def detect_changes(self, directory: str) -> Dict[str, List[str]]:
        """检测变化"""
        dir_path = self.workspace / directory
        changes = {"added": [], "modified": [], "deleted": []}
        
        if not dir_path.exists():
            return changes
        
        # 检查现有文件
        current_files: Set[str] = set()
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(self.workspace))
                current_files.add(rel_path)
                
                current_mtime = file_path.stat().st_mtime
                current_size = file_path.stat().st_size
                current_checksum = self._compute_checksum(file_path)
                
                if rel_path not in self.file_states:
                    changes["added"].append(rel_path)
                else:
                    old_state = self.file_states[rel_path]
                    if (current_mtime > old_state.mtime or 
                        current_size != old_state.size or
                        current_checksum != old_state.checksum):
                        changes["modified"].append(rel_path)
                
                # 更新状态
                self.file_states[rel_path] = FileState(
                    path=rel_path,
                    mtime=current_mtime,
                    size=current_size,
                    checksum=current_checksum
                )
        
        # 检查删除的文件
        for path in list(self.file_states.keys()):
            if path.startswith(directory) and path not in current_files:
                changes["deleted"].append(path)
                del self.file_states[path]
        
        self._save_states()
        return changes
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "tracked_files": len(self.file_states),
            "state_file": str(self.state_file)
        }
