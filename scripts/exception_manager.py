#!/usr/bin/env python3
"""
例外管理器 V1.0.0

统一例外操作入口，支持：
- list: 列出所有例外
- create: 创建新例外
- renew: 续期例外
- revoke: 撤销例外
- expire-check: 自动过期检查
- history: 查看操作历史

所有例外操作必须通过此入口，禁止直接修改 RULE_EXCEPTIONS.json
"""

import json
import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


class ExceptionManager:
    """例外管理器 - 统一例外操作入口"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.exceptions_file = self.root / "core" / "RULE_EXCEPTIONS.json"
        self.history_file = self.root / "reports" / "ops" / "rule_exception_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_exceptions(self) -> Dict:
        """加载例外真源"""
        if self.exceptions_file.exists():
            with open(self.exceptions_file) as f:
                data = json.load(f)
            # 兼容两种格式：列表和字典
            if "exceptions" in data:
                if isinstance(data["exceptions"], list):
                    # 列表格式，转换为字典
                    exc_dict = {}
                    for exc in data["exceptions"]:
                        exc_id = exc.get("exception_id", f"auto_{uuid.uuid4().hex[:8]}")
                        exc_dict[exc_id] = exc
                    data["exceptions"] = exc_dict
            return data
        return {"exceptions": {}, "version": "1.0.0"}
    
    def _save_exceptions(self, data: Dict):
        """保存例外真源"""
        with open(self.exceptions_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_history(self) -> List[Dict]:
        """加载操作历史"""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return []
    
    def _save_history(self, history: List[Dict]):
        """保存操作历史"""
        with open(self.history_file, 'w') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def _generate_event_id(self) -> str:
        """生成事件 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_uuid = uuid.uuid4().hex[:8]
        return f"exc_evt_{timestamp}_{short_uuid}"
    
    def _generate_exception_id(self, rule_id: str) -> str:
        """生成例外 ID"""
        timestamp = datetime.now().strftime("%Y%m%d")
        short_uuid = uuid.uuid4().hex[:6]
        return f"EXC-{rule_id}-{timestamp}-{short_uuid}"
    
    def _add_history(self, action: str, exception_id: str, rule_id: str,
                     approved_by: str, owner: str, old_status: str, new_status: str,
                     old_expires_at: str, new_expires_at: str, reason: str):
        """添加历史记录"""
        history = self._load_history()
        
        record = {
            "event_id": self._generate_event_id(),
            "exception_id": exception_id,
            "action": action,
            "rule_id": rule_id,
            "approved_by": approved_by,
            "owner": owner,
            "old_status": old_status,
            "new_status": new_status,
            "old_expires_at": old_expires_at,
            "new_expires_at": new_expires_at,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        history.append(record)
        self._save_history(history)
        
        return record["event_id"]
    
    def list(self, status: str = None, rule_id: str = None) -> Dict:
        """列出所有例外"""
        data = self._load_exceptions()
        exceptions = data.get("exceptions", {})
        
        result = []
        for exc_id, exc in exceptions.items():
            if status and exc.get("status") != status:
                continue
            if rule_id and exc.get("rule_id") != rule_id:
                continue
            result.append({"exception_id": exc_id, **exc})
        
        return {
            "status": "success",
            "count": len(result),
            "exceptions": result
        }
    
    def create(self, rule_id: str, reason: str, owner: str,
               approved_by: str, duration_days: int = 30,
               ticket_ref: str = "", max_renewals: int = 2) -> Dict:
        """创建新例外"""
        data = self._load_exceptions()
        
        # 生成例外 ID
        exception_id = self._generate_exception_id(rule_id)
        
        # 计算过期时间
        now = datetime.now()
        expires_at = (now + timedelta(days=duration_days)).isoformat()
        
        # 创建例外
        exception = {
            "rule_id": rule_id,
            "reason": reason,
            "owner": owner,
            "approved_by": approved_by,
            "status": "active",
            "created_at": now.isoformat(),
            "expires_at": expires_at,
            "renewal_count": 0,
            "max_renewals": max_renewals,
            "ticket_ref": ticket_ref
        }
        
        data["exceptions"][exception_id] = exception
        self._save_exceptions(data)
        
        # 添加历史记录
        event_id = self._add_history(
            action="create",
            exception_id=exception_id,
            rule_id=rule_id,
            approved_by=approved_by,
            owner=owner,
            old_status="none",
            new_status="active",
            old_expires_at="none",
            new_expires_at=expires_at,
            reason=reason
        )
        
        return {
            "status": "success",
            "event_id": event_id,
            "exception_id": exception_id,
            "message": f"例外已创建: {exception_id}",
            "exception": exception
        }
    
    def renew(self, exception_id: str, approved_by: str,
              duration_days: int = 30, reason: str = "") -> Dict:
        """续期例外"""
        data = self._load_exceptions()
        exceptions = data.get("exceptions", {})
        
        if exception_id not in exceptions:
            return {
                "status": "error",
                "message": f"例外不存在: {exception_id}"
            }
        
        exception = exceptions[exception_id]
        
        # 检查状态
        if exception["status"] != "active":
            return {
                "status": "error",
                "message": f"例外状态不是 active，无法续期: {exception['status']}"
            }
        
        # 检查续期次数
        renewal_count = exception.get("renewal_count", 0)
        max_renewals = exception.get("max_renewals", 2)
        
        if renewal_count >= max_renewals:
            return {
                "status": "error",
                "message": f"已达到最大续期次数 ({max_renewals})，无法续期"
            }
        
        # 记录旧值
        old_expires_at = exception["expires_at"]
        
        # 更新例外
        now = datetime.now()
        new_expires_at = (now + timedelta(days=duration_days)).isoformat()
        
        exception["renewal_count"] = renewal_count + 1
        exception["expires_at"] = new_expires_at
        exception["last_renewed_at"] = now.isoformat()
        exception["last_renewed_by"] = approved_by
        
        if reason:
            exception["renewal_reason"] = reason
        
        data["exceptions"][exception_id] = exception
        self._save_exceptions(data)
        
        # 添加历史记录
        event_id = self._add_history(
            action="renew",
            exception_id=exception_id,
            rule_id=exception["rule_id"],
            approved_by=approved_by,
            owner=exception["owner"],
            old_status="active",
            new_status="active",
            old_expires_at=old_expires_at,
            new_expires_at=new_expires_at,
            reason=reason or f"续期 {duration_days} 天"
        )
        
        return {
            "status": "success",
            "event_id": event_id,
            "exception_id": exception_id,
            "message": f"例外已续期: {exception_id} (第 {renewal_count + 1}/{max_renewals} 次)",
            "old_expires_at": old_expires_at,
            "new_expires_at": new_expires_at
        }
    
    def revoke(self, exception_id: str, approved_by: str, reason: str) -> Dict:
        """撤销例外"""
        data = self._load_exceptions()
        exceptions = data.get("exceptions", {})
        
        if exception_id not in exceptions:
            return {
                "status": "error",
                "message": f"例外不存在: {exception_id}"
            }
        
        exception = exceptions[exception_id]
        
        # 检查状态
        if exception["status"] != "active":
            return {
                "status": "error",
                "message": f"例外状态不是 active，无法撤销: {exception['status']}"
            }
        
        # 记录旧值
        old_status = exception["status"]
        old_expires_at = exception["expires_at"]
        
        # 更新例外
        now = datetime.now()
        exception["status"] = "revoked"
        exception["revoked_at"] = now.isoformat()
        exception["revoked_by"] = approved_by
        exception["revoke_reason"] = reason
        
        data["exceptions"][exception_id] = exception
        self._save_exceptions(data)
        
        # 添加历史记录
        event_id = self._add_history(
            action="revoke",
            exception_id=exception_id,
            rule_id=exception["rule_id"],
            approved_by=approved_by,
            owner=exception["owner"],
            old_status=old_status,
            new_status="revoked",
            old_expires_at=old_expires_at,
            new_expires_at=old_expires_at,
            reason=reason
        )
        
        return {
            "status": "success",
            "event_id": event_id,
            "exception_id": exception_id,
            "message": f"例外已撤销: {exception_id}"
        }
    
    def expire_check(self) -> Dict:
        """自动过期检查"""
        data = self._load_exceptions()
        exceptions = data.get("exceptions", {})
        
        now = datetime.now()
        expired = []
        
        for exc_id, exc in exceptions.items():
            if exc.get("status") != "active":
                continue
            
            expires_at_str = exc.get("expires_at")
            if not expires_at_str:
                continue
            
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
            except:
                continue
            
            if expires_at < now:
                # 记录旧值
                old_expires_at = exc["expires_at"]
                
                # 更新状态
                exc["status"] = "expired"
                exc["expired_at"] = now.isoformat()
                
                exceptions[exc_id] = exc
                expired.append(exc_id)
                
                # 添加历史记录
                self._add_history(
                    action="expire",
                    exception_id=exc_id,
                    rule_id=exc["rule_id"],
                    approved_by="system",
                    owner=exc["owner"],
                    old_status="active",
                    new_status="expired",
                    old_expires_at=old_expires_at,
                    new_expires_at=old_expires_at,
                    reason="自动过期"
                )
        
        if expired:
            data["exceptions"] = exceptions
            self._save_exceptions(data)
        
        return {
            "status": "success",
            "expired_count": len(expired),
            "expired": expired,
            "message": f"已处理 {len(expired)} 个过期例外"
        }
    
    def history(self, exception_id: str = None, limit: int = 20) -> Dict:
        """查看操作历史"""
        history = self._load_history()
        
        if exception_id:
            history = [h for h in history if h.get("exception_id") == exception_id]
        
        # 按时间倒序
        history = sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "status": "success",
            "count": len(history[:limit]),
            "history": history[:limit]
        }
    
    def get_recent_actions(self, hours: int = 24) -> Dict:
        """获取最近的操作统计"""
        history = self._load_history()
        
        now = datetime.now()
        cutoff = now - timedelta(hours=hours)
        
        stats = {
            "create": 0,
            "renew": 0,
            "revoke": 0,
            "expire": 0
        }
        
        for h in history:
            try:
                ts = datetime.fromisoformat(h.get("timestamp", ""))
                if ts >= cutoff:
                    action = h.get("action", "")
                    if action in stats:
                        stats[action] += 1
            except:
                continue
        
        return {
            "status": "success",
            "window_hours": hours,
            "actions": stats
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="例外管理器 V1.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # list
    list_parser = subparsers.add_parser("list", help="列出所有例外")
    list_parser.add_argument("--status", help="按状态过滤")
    list_parser.add_argument("--rule-id", help="按规则ID过滤")
    
    # create
    create_parser = subparsers.add_parser("create", help="创建新例外")
    create_parser.add_argument("--rule-id", required=True, help="规则ID")
    create_parser.add_argument("--reason", required=True, help="例外原因")
    create_parser.add_argument("--owner", required=True, help="负责人")
    create_parser.add_argument("--approved-by", required=True, help="审批人")
    create_parser.add_argument("--duration-days", type=int, default=30, help="有效期(天)")
    create_parser.add_argument("--ticket-ref", default="", help="关联工单")
    create_parser.add_argument("--max-renewals", type=int, default=2, help="最大续期次数")
    
    # renew
    renew_parser = subparsers.add_parser("renew", help="续期例外")
    renew_parser.add_argument("--exception-id", required=True, help="例外ID")
    renew_parser.add_argument("--approved-by", required=True, help="审批人")
    renew_parser.add_argument("--duration-days", type=int, default=30, help="续期天数")
    renew_parser.add_argument("--reason", default="", help="续期原因")
    
    # revoke
    revoke_parser = subparsers.add_parser("revoke", help="撤销例外")
    revoke_parser.add_argument("--exception-id", required=True, help="例外ID")
    revoke_parser.add_argument("--approved-by", required=True, help="审批人")
    revoke_parser.add_argument("--reason", required=True, help="撤销原因")
    
    # expire-check
    subparsers.add_parser("expire-check", help="自动过期检查")
    
    # history
    history_parser = subparsers.add_parser("history", help="查看操作历史")
    history_parser.add_argument("--exception-id", help="例外ID")
    history_parser.add_argument("--limit", type=int, default=20, help="限制数量")
    
    # recent-actions
    recent_parser = subparsers.add_parser("recent-actions", help="获取最近操作统计")
    recent_parser.add_argument("--hours", type=int, default=24, help="时间窗口(小时)")
    
    args = parser.parse_args()
    
    manager = ExceptionManager()
    
    if args.command == "list":
        result = manager.list(args.status, args.rule_id)
    elif args.command == "create":
        result = manager.create(
            rule_id=args.rule_id,
            reason=args.reason,
            owner=args.owner,
            approved_by=args.approved_by,
            duration_days=args.duration_days,
            ticket_ref=args.ticket_ref,
            max_renewals=args.max_renewals
        )
    elif args.command == "renew":
        result = manager.renew(
            exception_id=args.exception_id,
            approved_by=args.approved_by,
            duration_days=args.duration_days,
            reason=args.reason
        )
    elif args.command == "revoke":
        result = manager.revoke(
            exception_id=args.exception_id,
            approved_by=args.approved_by,
            reason=args.reason
        )
    elif args.command == "expire-check":
        result = manager.expire_check()
    elif args.command == "history":
        result = manager.history(args.exception_id, args.limit)
    elif args.command == "recent-actions":
        result = manager.get_recent_actions(args.hours)
    else:
        parser.print_help()
        return
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
