#!/usr/bin/env python3
"""自动 Git 提交模块 - V4.3.2

功能：
1. 检测工作区变更
2. 自动生成提交信息
3. 自动提交并推送
4. 记录提交历史
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
GIT_LOG_FILE = PROJECT_ROOT / "reports" / "git_commits.json"


class AutoGitCommit:
    """自动 Git 提交器"""
    
    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or PROJECT_ROOT
        self.git_log = self._load_log()
    
    def _load_log(self) -> Dict:
        """加载提交日志"""
        if GIT_LOG_FILE.exists():
            try:
                return json.loads(GIT_LOG_FILE.read_text())
            except:
                pass
        return {"commits": []}
    
    def _save_log(self):
        """保存提交日志"""
        GIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        GIT_LOG_FILE.write_text(json.dumps(self.git_log, ensure_ascii=False, indent=2))
    
    def _run_git(self, *args) -> Tuple[bool, str]:
        """执行 git 命令"""
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def has_changes(self) -> bool:
        """检查是否有变更"""
        ok, output = self._run_git("status", "--porcelain")
        return ok and output.strip() != ""
    
    def get_changes(self) -> Dict[str, List[str]]:
        """获取变更详情"""
        changes = {
            "modified": [],
            "added": [],
            "deleted": [],
            "renamed": []
        }
        
        ok, output = self._run_git("status", "--porcelain")
        if not ok:
            return changes
        
        for line in output.strip().split("\n"):
            if not line:
                continue
            
            status = line[:2].strip()
            file_path = line[3:]
            
            if status in ("M", "MM"):
                changes["modified"].append(file_path)
            elif status in ("A", "AM"):
                changes["added"].append(file_path)
            elif status == "D":
                changes["deleted"].append(file_path)
            elif status.startswith("R"):
                changes["renamed"].append(file_path)
        
        return changes
    
    def generate_commit_message(self, changes: Dict[str, List[str]]) -> str:
        """生成提交信息"""
        total = sum(len(v) for v in changes.values())
        
        parts = []
        if changes["added"]:
            parts.append(f"新增 {len(changes['added'])} 文件")
        if changes["modified"]:
            parts.append(f"修改 {len(changes['modified'])} 文件")
        if changes["deleted"]:
            parts.append(f"删除 {len(changes['deleted'])} 文件")
        if changes["renamed"]:
            parts.append(f"重命名 {len(changes['renamed'])} 文件")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"自动提交 [{timestamp}]: {', '.join(parts)}"
        
        return message
    
    def commit(self, message: str = None) -> Tuple[bool, str]:
        """提交变更"""
        if not self.has_changes():
            return True, "无变更需要提交"
        
        changes = self.get_changes()
        
        if message is None:
            message = self.generate_commit_message(changes)
        
        # 添加所有变更
        ok, output = self._run_git("add", "-A")
        if not ok:
            return False, f"git add 失败: {output}"
        
        # 提交
        ok, output = self._run_git("commit", "-m", message)
        if not ok:
            return False, f"git commit 失败: {output}"
        
        # 获取提交 hash
        ok, hash_output = self._run_git("rev-parse", "HEAD")
        commit_hash = hash_output.strip()[:8] if ok else "unknown"
        
        # 记录日志
        self.git_log["commits"].append({
            "hash": commit_hash,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "changes": changes
        })
        self._save_log()
        
        return True, f"提交成功: {commit_hash}"
    
    def push(self) -> Tuple[bool, str]:
        """推送到远程"""
        ok, output = self._run_git("push")
        if ok:
            return True, "推送成功"
        else:
            return False, f"推送失败: {output}"
    
    def commit_and_push(self, message: str = None) -> Tuple[bool, str]:
        """提交并推送"""
        # 提交
        ok, msg = self.commit(message)
        if not ok:
            return ok, msg
        
        # 推送
        ok, msg = self.push()
        return ok, msg
    
    def get_status(self) -> Dict:
        """获取状态"""
        changes = self.get_changes()
        return {
            "has_changes": self.has_changes(),
            "changes": changes,
            "total_changes": sum(len(v) for v in changes.values()),
            "last_commit": self.git_log["commits"][-1] if self.git_log["commits"] else None
        }


# 全局实例
_auto_git: Optional[AutoGitCommit] = None


def get_auto_git() -> AutoGitCommit:
    """获取自动 Git 提交器"""
    global _auto_git
    if _auto_git is None:
        _auto_git = AutoGitCommit()
    return _auto_git


def auto_commit_if_changed(message: str = None) -> Tuple[bool, str]:
    """如果有变更则自动提交"""
    git = get_auto_git()
    if git.has_changes():
        return git.commit_and_push(message)
    return True, "无变更"


# 命令行入口
if __name__ == "__main__":
    import sys
    
    git = get_auto_git()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "status":
            status = git.get_status()
            print(json.dumps(status, ensure_ascii=False, indent=2))
        
        elif cmd == "commit":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            ok, msg = git.commit(message)
            print(f"{'✅' if ok else '❌'} {msg}")
        
        elif cmd == "push":
            ok, msg = git.push()
            print(f"{'✅' if ok else '❌'} {msg}")
        
        elif cmd == "sync":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            ok, msg = git.commit_and_push(message)
            print(f"{'✅' if ok else '❌'} {msg}")
        
        else:
            print(f"用法: {sys.argv[0]} [status|commit|push|sync] [message]")
    
    else:
        # 默认：显示状态
        status = git.get_status()
        print(f"变更状态: {'有变更' if status['has_changes'] else '无变更'}")
        if status["has_changes"]:
            print(f"变更文件: {status['total_changes']} 个")
            for change_type, files in status["changes"].items():
                if files:
                    print(f"  {change_type}: {len(files)}")
