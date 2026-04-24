#!/usr/bin/env python3
"""
删除确认模块 V1.0.0

功能：
- 所有删除操作必须经过用户确认
- 记录所有删除操作
- 支持撤销（移动到回收站而非直接删除）
- 删除审计日志

使用方式：
- 任何删除操作都应通过此模块
- 禁止直接使用 rm 或 os.remove
"""

import os
import sys
import json
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


class DeleteManager:
    """删除管理器 - 所有删除操作必须经过此类"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.trash_dir = self.root / "archive" / "trash"
        self.log_file = self.root / "reports" / "ops" / "delete_log.json"
        self.pending_file = self.root / "reports" / "ops" / "pending_deletes.json"
        
        # 确保目录存在
        self.trash_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def request_delete(self, target: str, reason: str = "", 
                       requester: str = "system") -> Dict:
        """
        请求删除 - 返回待确认信息
        
        Args:
            target: 要删除的目标路径
            reason: 删除原因
            requester: 请求者
        
        Returns:
            包含确认信息的字典
        """
        target_path = Path(target)
        
        # 检查目标是否存在
        if not target_path.exists():
            return {
                "status": "error",
                "message": f"目标不存在: {target}",
                "target": str(target_path)
            }
        
        # 检查是否是受保护文件
        protected = self._check_protected(target_path)
        if protected:
            return {
                "status": "protected",
                "message": f"受保护文件，禁止删除: {target}",
                "target": str(target_path),
                "protection_reason": protected
            }
        
        # 获取目标信息
        info = self._get_target_info(target_path)
        
        # 生成删除请求 ID
        request_id = self._generate_request_id(target_path)
        
        # 保存待确认请求
        pending = self._load_pending()
        pending[request_id] = {
            "target": str(target_path),
            "reason": reason,
            "requester": requester,
            "requested_at": datetime.now().isoformat(),
            "info": info,
            "status": "pending"
        }
        self._save_pending(pending)
        
        return {
            "status": "pending",
            "request_id": request_id,
            "target": str(target_path),
            "info": info,
            "reason": reason,
            "message": f"删除请求已创建，等待确认。请求ID: {request_id}"
        }
    
    def confirm_delete(self, request_id: str, confirmed: bool = True,
                       confirmer: str = "user") -> Dict:
        """
        确认删除
        
        Args:
            request_id: 请求 ID
            confirmed: 是否确认删除
            confirmer: 确认者
        
        Returns:
            操作结果
        """
        pending = self._load_pending()
        
        if request_id not in pending:
            return {
                "status": "error",
                "message": f"请求不存在: {request_id}"
            }
        
        request = pending[request_id]
        
        if confirmed:
            # 执行删除（移动到回收站）
            result = self._execute_delete(request["target"])
            
            # 记录日志
            self._log_delete({
                **request,
                "confirmed": True,
                "confirmer": confirmer,
                "confirmed_at": datetime.now().isoformat(),
                "result": result
            })
            
            # 从待确认列表移除
            del pending[request_id]
            self._save_pending(pending)
            
            return {
                "status": "deleted",
                "request_id": request_id,
                "target": request["target"],
                "message": f"已删除并移至回收站: {request['target']}"
            }
        else:
            # 拒绝删除
            request["status"] = "rejected"
            request["rejected_at"] = datetime.now().isoformat()
            request["rejecter"] = confirmer
            
            # 记录日志
            self._log_delete(request)
            
            # 从待确认列表移除
            del pending[request_id]
            self._save_pending(pending)
            
            return {
                "status": "rejected",
                "request_id": request_id,
                "target": request["target"],
                "message": "删除请求已拒绝"
            }
    
    def list_pending(self) -> List[Dict]:
        """列出所有待确认的删除请求"""
        pending = self._load_pending()
        return [
            {"request_id": rid, **req}
            for rid, req in pending.items()
        ]
    
    def restore_from_trash(self, target: str) -> Dict:
        """从回收站恢复"""
        target_path = Path(target)
        trash_path = self.trash_dir / target_path.name
        
        if not trash_path.exists():
            return {
                "status": "error",
                "message": f"回收站中不存在: {target}"
            }
        
        # 恢复文件
        shutil.move(str(trash_path), str(target_path))
        
        return {
            "status": "restored",
            "target": str(target_path),
            "message": f"已恢复: {target}"
        }
    
    def empty_trash(self, older_than_days: int = 7) -> Dict:
        """清空回收站（超过指定天数的文件）"""
        deleted = []
        now = datetime.now()
        
        for item in self.trash_dir.iterdir():
            mtime = datetime.fromtimestamp(item.stat().st_mtime)
            age_days = (now - mtime).days
            
            if age_days > older_than_days:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                deleted.append(str(item))
        
        return {
            "status": "emptied",
            "deleted_count": len(deleted),
            "deleted": deleted
        }
    
    def _check_protected(self, target: Path) -> Optional[str]:
        """检查是否是受保护文件"""
        protected_patterns = [
            "core/ARCHITECTURE.md",
            "core/RULE_REGISTRY.json",
            "core/SOUL.md",
            "core/USER.md",
            "core/AGENTS.md",
            "core/TOOLS.md",
            "core/IDENTITY.md",
            "MEMORY.md",
        ]
        
        target_str = str(target)
        for pattern in protected_patterns:
            if pattern in target_str:
                return f"匹配保护模式: {pattern}"
        
        return None
    
    def _get_target_info(self, target: Path) -> Dict:
        """获取目标信息"""
        stat = target.stat()
        return {
            "type": "directory" if target.is_dir() else "file",
            "size": stat.st_size if target.is_file() else self._get_dir_size(target),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }
    
    def _get_dir_size(self, path: Path) -> int:
        """获取目录大小"""
        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                total += item.stat().st_size
        return total
    
    def _generate_request_id(self, target: Path) -> str:
        """生成请求 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_part = hashlib.md5(str(target).encode()).hexdigest()[:8]
        return f"del_{timestamp}_{hash_part}"
    
    def _execute_delete(self, target: str) -> Dict:
        """执行删除（移动到回收站）"""
        target_path = Path(target)
        trash_path = self.trash_dir / f"{target_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        shutil.move(str(target_path), str(trash_path))
        
        return {
            "original_path": str(target_path),
            "trash_path": str(trash_path),
            "deleted_at": datetime.now().isoformat()
        }
    
    def _load_pending(self) -> Dict:
        """加载待确认请求"""
        if self.pending_file.exists():
            with open(self.pending_file) as f:
                return json.load(f)
        return {}
    
    def _save_pending(self, pending: Dict):
        """保存待确认请求"""
        with open(self.pending_file, 'w') as f:
            json.dump(pending, f, ensure_ascii=False, indent=2)
    
    def _log_delete(self, record: Dict):
        """记录删除日志"""
        logs = []
        if self.log_file.exists():
            with open(self.log_file) as f:
                logs = json.load(f)
        
        logs.append(record)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="删除确认模块 V1.0.0")
    parser.add_argument("--request", help="请求删除目标")
    parser.add_argument("--reason", default="", help="删除原因")
    parser.add_argument("--confirm", help="确认删除请求ID")
    parser.add_argument("--reject", help="拒绝删除请求ID")
    parser.add_argument("--list", action="store_true", help="列出待确认请求")
    parser.add_argument("--restore", help="从回收站恢复")
    parser.add_argument("--empty-trash", type=int, help="清空回收站(超过N天)")
    args = parser.parse_args()
    
    manager = DeleteManager()
    
    if args.request:
        result = manager.request_delete(args.request, args.reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.confirm:
        result = manager.confirm_delete(args.confirm, True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.reject:
        result = manager.confirm_delete(args.reject, False)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.list:
        pending = manager.list_pending()
        print(json.dumps(pending, ensure_ascii=False, indent=2))
    elif args.restore:
        result = manager.restore_from_trash(args.restore)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.empty_trash is not None:
        result = manager.empty_trash(args.empty_trash)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
