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
        # 自动刷新状态快照
        self._refresh_status_snapshot()
    
    def _refresh_status_snapshot(self):
        """刷新例外状态快照"""
        data = self._load_exceptions()
        exceptions = data.get("exceptions", {})
        
        now = datetime.now()
        
        # 统计各状态
        active_count = 0
        soon_expiring_count = 0
        expired_count = 0
        revoked_count = 0
        stale_count = 0
        overused_count = 0
        high_debt_count = 0
        
        by_owner = {}
        
        for exc_id, exc in exceptions.items():
            status = exc.get("status", "")
            owner = exc.get("owner", "unknown")
            debt_level = exc.get("debt_level", "low")
            renewal_count = exc.get("renewal_count", 0)
            max_renewals = exc.get("max_renewals", 2)
            
            # 按状态统计
            if status == "active":
                active_count += 1
                
                # 检查即将过期
                expires_at_str = exc.get("expires_at")
                if expires_at_str:
                    try:
                        expires_at = datetime.fromisoformat(expires_at_str)
                        days_left = (expires_at - now).days
                        if days_left <= 7:
                            soon_expiring_count += 1
                    except:
                        pass
                
                # 检查 stale (超过 30 天未更新)
                created_at_str = exc.get("created_at")
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str)
                        if (now - created_at).days > 30:
                            stale_count += 1
                    except:
                        pass
                
                # 检查 overused
                if renewal_count >= max_renewals:
                    overused_count += 1
                
                # 检查 high debt
                if debt_level == "high":
                    high_debt_count += 1
            
            elif status == "expired":
                expired_count += 1
            elif status == "revoked":
                revoked_count += 1
            
            # 按负责人统计
            if owner not in by_owner:
                by_owner[owner] = {"active": 0, "expired": 0, "revoked": 0}
            if status in by_owner[owner]:
                by_owner[owner][status] += 1
        
        # 保存快照
        snapshot = {
            "active_count": active_count,
            "soon_expiring_count": soon_expiring_count,
            "stale_count": stale_count,
            "overused_count": overused_count,
            "expired_count": expired_count,
            "revoked_count": revoked_count,
            "high_debt_count": high_debt_count,
            "by_owner": by_owner,
            "generated_at": now.isoformat()
        }
        
        snapshot_path = self.root / "reports/ops/rule_exception_status.json"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        
        return snapshot
    
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
               ticket_ref: str = "", max_renewals: int = 2,
               debt_level: str = "low") -> Dict:
        """创建新例外"""
        # 检查策略
        policy_check = self._validate_exception_policy(
            rule_id=rule_id,
            duration_days=duration_days,
            approved_by=approved_by,
            ticket_ref=ticket_ref
        )
        if not policy_check["ok"]:
            return {
                "status": "error",
                "message": policy_check["reason"]
            }
        
        # 检查配额
        quota_check = self.check_quota_before_create(owner, rule_id, debt_level)
        if not quota_check["allowed"]:
            return {
                "status": "error",
                "message": quota_check["reason"]
            }
        
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
            "ticket_ref": ticket_ref,
            "debt_level": debt_level
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
        
        # 检查配额（续期后是否会导致超限）
        owner = exception.get("owner", "unknown")
        rule_id = exception.get("rule_id", "unknown")
        debt_level = exception.get("debt_level", "low")
        
        # 续期不增加新的例外，但需要检查是否已有配额违规
        quota_status = self.quota_check()
        
        # 如果 owner 已超限，拒绝续期
        if owner in quota_status.get("exceeded_owners", []):
            return {
                "status": "error",
                "message": f"Owner '{owner}' 配额已超限，无法续期"
            }
        
        # 如果 rule 已超限，拒绝续期
        if rule_id in quota_status.get("exceeded_rules", []):
            return {
                "status": "error",
                "message": f"Rule '{rule_id}' 配额已超限，无法续期"
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
    
    def quota_check(self) -> Dict:
        """检查配额使用情况"""
        data = self._load_exceptions()
        exceptions = data.get("exceptions", {})
        
        # Owner 级配额
        owner_quotas = {
            "architecture": {"max_active": 5, "max_high_debt": 2},
            "governance": {"max_active": 5, "max_high_debt": 2},
            "infrastructure": {"max_active": 3, "max_high_debt": 1},
            "_default": {"max_active": 2, "max_high_debt": 1}
        }
        
        # Rule 级配额
        rule_quotas = {
            "R004": 2,
            "R006": 2,
            "R007": 3,
            "_default": 2
        }
        
        # 统计使用情况
        owner_usage = {}
        owner_high_debt = {}
        rule_usage = {}
        
        for exc_id, exc in exceptions.items():
            if exc.get("status") != "active":
                continue
            
            owner = exc.get("owner", "unknown")
            rule_id = exc.get("rule_id", "unknown")
            debt_level = exc.get("debt_level", "low")
            
            # Owner 统计
            if owner not in owner_usage:
                owner_usage[owner] = 0
                owner_high_debt[owner] = 0
            owner_usage[owner] += 1
            
            if debt_level == "high":
                owner_high_debt[owner] += 1
            
            # Rule 统计
            if rule_id not in rule_usage:
                rule_usage[rule_id] = 0
            rule_usage[rule_id] += 1
        
        # 构建配额报告
        owner_report = {}
        for owner, used in owner_usage.items():
            config = owner_quotas.get(owner, owner_quotas["_default"])
            limit = config["max_active"]
            high_debt_limit = config["max_high_debt"]
            high_debt_used = owner_high_debt.get(owner, 0)
            
            owner_report[owner] = {
                "used": used,
                "limit": limit,
                "available": max(0, limit - used),
                "exceeded": used > limit,
                "high_debt_used": high_debt_used,
                "high_debt_limit": high_debt_limit,
                "high_debt_exceeded": high_debt_used > high_debt_limit
            }
        
        rule_report = {}
        for rule_id, used in rule_usage.items():
            limit = rule_quotas.get(rule_id, rule_quotas["_default"])
            rule_report[rule_id] = {
                "used": used,
                "limit": limit,
                "available": max(0, limit - used),
                "exceeded": used > limit
            }
        
        # 检查超限
        exceeded_owners = [o for o, r in owner_report.items() if r["exceeded"] or r["high_debt_exceeded"]]
        exceeded_rules = [r for r, rep in rule_report.items() if rep["exceeded"]]
        
        # 保存配额快照
        self._save_quota_snapshot(owner_report, rule_report, exceeded_owners, exceeded_rules)
        
        return {
            "status": "success",
            "owner_quotas": owner_report,
            "rule_quotas": rule_report,
            "exceeded_owners": exceeded_owners,
            "exceeded_rules": exceeded_rules,
            "has_violations": len(exceeded_owners) > 0 or len(exceeded_rules) > 0
        }
    
    def _save_quota_snapshot(self, owner_report: Dict, rule_report: Dict,
                             exceeded_owners: List, exceeded_rules: List):
        """保存配额快照"""
        snapshot = {
            "generated_at": datetime.now().isoformat(),
            "owners": {
                "architecture": {"max_active": 5, "max_high_debt": 2},
                "governance": {"max_active": 5, "max_high_debt": 2},
                "infrastructure": {"max_active": 3, "max_high_debt": 1},
                "_default": {"max_active": 2, "max_high_debt": 1}
            },
            "rules": {
                "R004": 2,
                "R006": 2,
                "R007": 3,
                "_default": 2
            },
            "owner_usage": owner_report,
            "rule_usage": rule_report,
            "violations": {
                "owner_violations": exceeded_owners,
                "rule_violations": exceeded_rules
            }
        }
        
        snapshot_path = self.root / "reports/ops/rule_exception_quota.json"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(snapshot_path, 'w') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
    
    def _load_policy(self) -> Dict:
        """加载例外策略"""
        data = self._load_exceptions()
        return data.get("policies", {})
    
    def _validate_exception_policy(self, rule_id: str, duration_days: int,
                                   approved_by: str, ticket_ref: str = "") -> Dict:
        """校验例外策略"""
        policies = self._load_policy()
        allowed = set(policies.get("allowed_for_rules", []))
        forbidden = set(policies.get("forbidden_for_rules", []))
        max_duration_days = policies.get("max_duration_days", 30)
        require_approval = policies.get("require_approval", True)
        
        if rule_id in forbidden:
            return {"ok": False, "reason": f"规则 {rule_id} 禁止创建例外"}
        
        if allowed and rule_id not in allowed:
            return {"ok": False, "reason": f"规则 {rule_id} 不在允许例外清单中"}
        
        if duration_days > max_duration_days:
            return {"ok": False, "reason": f"例外时长超限: {duration_days}/{max_duration_days} 天"}
        
        if require_approval and not approved_by:
            return {"ok": False, "reason": "缺少审批人"}
        
        return {"ok": True, "reason": "策略校验通过"}
    
    def check_quota_before_create(self, owner: str, rule_id: str, debt_level: str = "low") -> Dict:
        """创建前检查配额"""
        quota_status = self.quota_check()
        
        # Owner 配额定义
        owner_quotas = {
            "architecture": {"max_active": 5, "max_high_debt": 2},
            "governance": {"max_active": 5, "max_high_debt": 2},
            "infrastructure": {"max_active": 3, "max_high_debt": 1},
            "_default": {"max_active": 2, "max_high_debt": 1}
        }
        
        # Rule 配额定义
        rule_quotas = {
            "R004": 2,
            "R006": 2,
            "R007": 3,
            "_default": 2
        }
        
        # 检查 owner 活跃例外配额
        owner_config = owner_quotas.get(owner, owner_quotas["_default"])
        owner_limit = owner_config["max_active"]
        owner_used = quota_status["owner_quotas"].get(owner, {}).get("used", 0)
        
        if owner_used >= owner_limit:
            return {
                "allowed": False,
                "reason": f"Owner '{owner}' 活跃例外配额已满: {owner_used}/{owner_limit}"
            }
        
        # 检查 owner 高债务例外配额
        if debt_level == "high":
            high_debt_limit = owner_config["max_high_debt"]
            high_debt_used = quota_status["owner_quotas"].get(owner, {}).get("high_debt_used", 0)
            
            if high_debt_used >= high_debt_limit:
                return {
                    "allowed": False,
                    "reason": f"Owner '{owner}' 高债务例外配额已满: {high_debt_used}/{high_debt_limit}"
                }
        
        # 检查 rule 配额
        rule_limit = rule_quotas.get(rule_id, rule_quotas["_default"])
        rule_used = quota_status["rule_quotas"].get(rule_id, {}).get("used", 0)
        
        if rule_used >= rule_limit:
            return {
                "allowed": False,
                "reason": f"Rule '{rule_id}' 配额已满: {rule_used}/{rule_limit}"
            }
        
        return {
            "allowed": True,
            "reason": "配额检查通过"
        }
    
    def create_request(self, rule_id: str, reason: str, owner: str,
                       requested_by: str, duration_days: int = 30,
                       ticket_ref: str = "", max_renewals: int = 2) -> Dict:
        """创建例外申请（进入审批队列）"""
        # 检查配额
        quota_check = self.check_quota_before_create(owner, rule_id)
        if not quota_check["allowed"]:
            return {
                "status": "error",
                "message": quota_check["reason"]
            }
        
        # 生成申请 ID
        request_id = f"EXC_REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        # 加载审批队列
        queue_path = self.root / "reports/ops/exception_approval_queue.json"
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        
        if queue_path.exists():
            queue = json.load(open(queue_path))
        else:
            queue = {"pending": [], "approved": [], "denied": []}
        
        # 创建申请
        request = {
            "request_id": request_id,
            "rule_id": rule_id,
            "reason": reason,
            "owner": owner,
            "requested_by": requested_by,
            "duration_days": duration_days,
            "ticket_ref": ticket_ref,
            "max_renewals": max_renewals,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approved_at": None,
            "approved_by": None,
            "denied_at": None,
            "denied_by": None,
            "denied_reason": None,
            "exception_id": None
        }
        
        queue["pending"].append(request)
        
        with open(queue_path, 'w') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "request_id": request_id,
            "message": f"例外申请已提交，等待审批: {request_id}"
        }
    
    def approve_request(self, request_id: str, approved_by: str) -> Dict:
        """批准例外申请"""
        queue_path = self.root / "reports/ops/exception_approval_queue.json"
        if not queue_path.exists():
            return {"status": "error", "message": "审批队列不存在"}
        
        queue = json.load(open(queue_path))
        
        # 查找申请
        request = None
        for i, r in enumerate(queue["pending"]):
            if r["request_id"] == request_id:
                request = queue["pending"].pop(i)
                break
        
        if not request:
            return {"status": "error", "message": f"申请不存在: {request_id}"}
        
        # 更新申请状态
        request["status"] = "approved"
        request["approved_at"] = datetime.now().isoformat()
        request["approved_by"] = approved_by
        
        # 创建例外
        result = self.create(
            rule_id=request["rule_id"],
            reason=request["reason"],
            owner=request["owner"],
            approved_by=approved_by,
            duration_days=request["duration_days"],
            ticket_ref=request.get("ticket_ref", ""),
            max_renewals=request.get("max_renewals", 2)
        )
        
        request["exception_id"] = result.get("exception_id")
        
        # 移动到已批准列表
        queue["approved"].append(request)
        
        with open(queue_path, 'w') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "request_id": request_id,
            "exception_id": request["exception_id"],
            "message": f"申请已批准，例外已创建: {request['exception_id']}"
        }
    
    def deny_request(self, request_id: str, denied_by: str, reason: str) -> Dict:
        """拒绝例外申请"""
        queue_path = self.root / "reports/ops/exception_approval_queue.json"
        if not queue_path.exists():
            return {"status": "error", "message": "审批队列不存在"}
        
        queue = json.load(open(queue_path))
        
        # 查找申请
        request = None
        for i, r in enumerate(queue["pending"]):
            if r["request_id"] == request_id:
                request = queue["pending"].pop(i)
                break
        
        if not request:
            return {"status": "error", "message": f"申请不存在: {request_id}"}
        
        # 更新申请状态
        request["status"] = "denied"
        request["denied_at"] = datetime.now().isoformat()
        request["denied_by"] = denied_by
        request["denied_reason"] = reason
        
        # 移动到已拒绝列表
        queue["denied"].append(request)
        
        with open(queue_path, 'w') as f:
            json.dump(queue, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "request_id": request_id,
            "message": f"申请已拒绝: {reason}"
        }
    
    def list_approval_queue(self) -> Dict:
        """列出审批队列"""
        queue_path = self.root / "reports/ops/exception_approval_queue.json"
        if not queue_path.exists():
            return {"pending": [], "approved": [], "denied": []}
        
        return json.load(open(queue_path))


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
    create_parser.add_argument("--debt-level", default="low", choices=["low", "medium", "high"], help="债务级别")
    
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
    
    # quota-check
    subparsers.add_parser("quota-check", help="检查配额使用情况")
    
    # create-request
    cr_parser = subparsers.add_parser("create-request", help="创建例外申请")
    cr_parser.add_argument("--rule-id", required=True, help="规则ID")
    cr_parser.add_argument("--reason", required=True, help="申请原因")
    cr_parser.add_argument("--owner", required=True, help="负责人")
    cr_parser.add_argument("--requested-by", required=True, help="申请人")
    cr_parser.add_argument("--duration-days", type=int, default=30, help="有效期(天)")
    cr_parser.add_argument("--ticket-ref", default="", help="关联工单")
    
    # approve-request
    ar_parser = subparsers.add_parser("approve-request", help="批准例外申请")
    ar_parser.add_argument("--request-id", required=True, help="申请ID")
    ar_parser.add_argument("--approved-by", required=True, help="审批人")
    
    # deny-request
    dr_parser = subparsers.add_parser("deny-request", help="拒绝例外申请")
    dr_parser.add_argument("--request-id", required=True, help="申请ID")
    dr_parser.add_argument("--denied-by", required=True, help="拒绝人")
    dr_parser.add_argument("--reason", required=True, help="拒绝原因")
    
    # list-approval-queue
    subparsers.add_parser("list-approval-queue", help="列出审批队列")
    
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
            max_renewals=args.max_renewals,
            debt_level=args.debt_level
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
    elif args.command == "quota-check":
        result = manager.quota_check()
    elif args.command == "create-request":
        result = manager.create_request(
            rule_id=args.rule_id,
            reason=args.reason,
            owner=args.owner,
            requested_by=args.requested_by,
            duration_days=args.duration_days,
            ticket_ref=args.ticket_ref
        )
    elif args.command == "approve-request":
        result = manager.approve_request(
            request_id=args.request_id,
            approved_by=args.approved_by
        )
    elif args.command == "deny-request":
        result = manager.deny_request(
            request_id=args.request_id,
            denied_by=args.denied_by,
            reason=args.reason
        )
    elif args.command == "list-approval-queue":
        result = manager.list_approval_queue()
    else:
        parser.print_help()
        return
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
