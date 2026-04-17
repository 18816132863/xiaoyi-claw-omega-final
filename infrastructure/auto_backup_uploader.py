#!/usr/bin/env python3
"""
自动备份上传器 - V1.0.0

职责：
1. 自动打包工作空间
2. 自动上传到 Git 仓库
3. 支持定时备份

使用方式：
- 手动触发: python infrastructure/auto_backup_uploader.py
- 定时备份: 通过 HEARTBEAT.md 配置
"""

import os
import sys
import subprocess
import tarfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
import json


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


class AutoBackupUploader:
    """自动备份上传器"""
    
    def __init__(self, root: Path):
        self.root = root
        self.backup_dir = root / ".openclaw" / "backup"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 排除规则
        self.exclude_patterns = [
            ".openclaw/backup/",
            ".openclaw/browser/",
            ".openclaw/npm-cache/",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.jsonl",
            "*.log",
            "*.tmp",
            "*.tar.gz",
            "*.zip",
            "node_modules/",
            ".git/",
        ]
    
    def create_backup(self) -> Optional[Path]:
        """创建备份压缩包"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        print(f"📦 创建备份: {backup_name}")
        
        # 创建排除文件
        exclude_file = self.backup_dir / "exclude.txt"
        exclude_file.write_text("\n".join(self.exclude_patterns))
        
        try:
            # 使用 tar 打包
            cmd = [
                "tar", "-czvf", str(backup_path),
                "--exclude-from=" + str(exclude_file),
                "-C", str(self.root.parent),
                ".openclaw"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                size_mb = backup_path.stat().st_size / 1024 / 1024
                print(f"  ✅ 备份完成: {size_mb:.1f} MB")
                return backup_path
            else:
                print(f"  ❌ 备份失败: {result.stderr}")
                return None
        except Exception as e:
            print(f"  ❌ 备份异常: {e}")
            return None
    
    def get_backup_hash(self, backup_path: Path) -> str:
        """计算备份文件哈希"""
        sha256 = hashlib.sha256()
        with open(backup_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()[:16]
    
    def git_status(self) -> Dict[str, Any]:
        """获取 Git 状态"""
        try:
            # 检查是否有变更
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            
            changes = result.stdout.strip().split("\n") if result.stdout.strip() else []
            
            # 获取当前分支
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            branch = branch_result.stdout.strip()
            
            # 获取最新提交
            log_result = subprocess.run(
                ["git", "log", "-1", "--format=%h %s"],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            last_commit = log_result.stdout.strip()
            
            return {
                "has_changes": len(changes) > 0,
                "changes": changes[:20],  # 最多显示20个
                "branch": branch,
                "last_commit": last_commit
            }
        except Exception as e:
            return {"error": str(e)}
    
    def git_add_commit_push(self, message: str = None) -> bool:
        """Git 添加、提交、推送"""
        if message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"自动备份: {timestamp}"
        
        print(f"\n📤 上传到 Git...")
        
        try:
            # 1. git add
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print(f"  ❌ git add 失败: {result.stderr}")
                return False
            
            # 2. git commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=str(self.root),
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                if "nothing to commit" in result.stdout:
                    print("  ℹ️  没有变更需要提交")
                    return True
                print(f"  ❌ git commit 失败: {result.stderr}")
                return False
            
            print(f"  ✅ 提交: {message}")
            
            # 3. git push
            result = subprocess.run(
                ["git", "push", "--set-upstream", "origin", "master"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode != 0:
                print(f"  ❌ git push 失败: {result.stderr}")
                return False
            
            print("  ✅ 推送成功")
            return True
            
        except Exception as e:
            print(f"  ❌ Git 操作异常: {e}")
            return False
    
    def cleanup_old_backups(self, keep_count: int = 5):
        """清理旧备份"""
        backups = sorted(self.backup_dir.glob("backup_*.tar.gz"), reverse=True)
        
        if len(backups) > keep_count:
            for old_backup in backups[keep_count:]:
                try:
                    old_backup.unlink()
                    print(f"  🗑️  删除旧备份: {old_backup.name}")
                except Exception:
                    pass
    
    def run(self, create_tar: bool = False) -> Dict[str, Any]:
        """
        运行自动备份上传
        
        Args:
            create_tar: 是否创建 tar 备份文件
        
        Returns:
            执行结果
        """
        print("=" * 60)
        print("  自动备份上传器 V1.0.0")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "git_status": None,
            "backup_created": False,
            "backup_path": None,
            "git_pushed": False
        }
        
        # 1. 检查 Git 状态
        print("\n📊 检查 Git 状态...")
        git_status = self.git_status()
        results["git_status"] = git_status
        
        if "error" in git_status:
            print(f"  ❌ Git 状态检查失败: {git_status['error']}")
            return results
        
        print(f"  分支: {git_status['branch']}")
        print(f"  最新提交: {git_status['last_commit']}")
        print(f"  变更文件: {len(git_status['changes'])} 个")
        
        # 2. 创建备份（可选）
        if create_tar:
            print("\n📦 创建备份文件...")
            backup_path = self.create_backup()
            if backup_path:
                results["backup_created"] = True
                results["backup_path"] = str(backup_path)
                self.cleanup_old_backups()
        
        # 3. Git 提交推送
        if git_status["has_changes"]:
            success = self.git_add_commit_push()
            results["git_pushed"] = success
        else:
            print("\nℹ️  没有变更需要提交")
            results["git_pushed"] = True
        
        print("\n" + "=" * 60)
        if results["git_pushed"]:
            print("  ✅ 自动备份上传完成")
        else:
            print("  ⚠️  自动备份上传失败")
        print("=" * 60 + "\n")
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="自动备份上传器 V1.0.0")
    parser.add_argument("--create-tar", action="store_true", help="创建 tar 备份文件")
    parser.add_argument("--dry-run", action="store_true", help="仅检查状态，不执行上传")
    args = parser.parse_args()
    
    root = get_project_root()
    uploader = AutoBackupUploader(root)
    
    if args.dry_run:
        print("🔍 Dry run - 仅检查状态")
        git_status = uploader.git_status()
        print(f"分支: {git_status.get('branch')}")
        print(f"变更: {len(git_status.get('changes', []))} 个")
        return 0
    
    results = uploader.run(create_tar=args.create_tar)
    
    return 0 if results["git_pushed"] else 1


if __name__ == "__main__":
    sys.exit(main())
