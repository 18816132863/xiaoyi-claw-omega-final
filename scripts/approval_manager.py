#!/usr/bin/env python3
"""
审批管理器 - V1.0.0

管理 semi_auto 动作的审批流程
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

def load_json(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None

def save_json(path: Path, data: Dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def normalize_approval_record(record: dict) -> dict:
    """统一归一审批记录状态"""
    # 1. pending
    if record.get("status") == "pending":
        record["status"] = "pending"
        record["final_status"] = None
        return record

    # 2. denied
    if record.get("denied_at"):
        record["status"] = "denied"
        record["final_status"] = "denied"
        return record

    # 3. executed
    if record.get("execute_success") is True:
        record["status"] = "executed"
        record["final_status"] = "executed"
        record["execute_success"] = True
        return record

    if record.get("final_status") == "executed":
        record["status"] = "executed"
        record["final_status"] = "executed"
        record["execute_success"] = True
        return record

    if record.get("execute_record_id") and record.get("executed_at"):
        record["status"] = "executed"
        record["final_status"] = "executed"
        record["execute_success"] = True
        return record

    # 4. execute_failed
    if record.get("execute_success") is False:
        record["status"] = "execute_failed"
        record["final_status"] = "execute_failed"
        record["execute_success"] = False
        return record

    if record.get("final_status") == "execute_failed":
        record["status"] = "execute_failed"
        record["final_status"] = "execute_failed"
        record["execute_success"] = False
        return record

    if record.get("execute_error"):
        record["status"] = "execute_failed"
        record["final_status"] = "execute_failed"
        record["execute_success"] = False
        return record

    # 5. approved_legacy
    if record.get("approved_at") and not record.get("executed_at") and not record.get("denied_at") and not record.get("execute_record_id"):
        record["status"] = "approved_legacy"
        # final_status 保持原样
        return record

    return record


class ApprovalManager:
    """审批管理器"""

    SEMI_AUTO_ACTIONS = [
        "rerun_nightly",
        "rerun_release_gate",
        "rerun_integration",
        "toggle_incident"
    ]

    def __init__(self, root: Path):
        self.root = root
        self.remediation_dir = root / "reports" / "remediation"
        self.queue_path = self.remediation_dir / "approval_queue.json"
        self.history_path = self.remediation_dir / "approval_history.json"

    def _load_queue(self) -> Dict:
        return load_json(self.queue_path) or {"pending": [], "generated_at": datetime.now().isoformat()}

    def _save_queue(self, queue: Dict):
        save_json(self.queue_path, queue)

    def _load_history(self) -> Dict:
        data = load_json(self.history_path) or {"approvals": [], "generated_at": datetime.now().isoformat()}
        # 归一化所有记录
        data["approvals"] = [normalize_approval_record(a) for a in data.get("approvals", [])]
        return data

    def _save_history(self, history: Dict):
        # 归一化后保存
        history["approvals"] = [normalize_approval_record(a) for a in history.get("approvals", [])]
        save_json(self.history_path, history)

    def add_to_queue(self, action_type: str, reason: str, source: str = "manual",
                     source_alert: str = None, source_incident: str = None,
                     action_params: dict = None) -> str:
        """添加到审批队列"""
        queue = self._load_queue()

        approval_id = f"apr_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid() % 1000:03d}"

        item = {
            "approval_id": approval_id,
            "action_type": action_type,
            "reason": reason,
            "source": source,
            "source_alert": source_alert,
            "source_incident": source_incident,
            "action_params": action_params or {},
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "approved_at": None,
            "approved_by": None,
            "denied_at": None,
            "denied_by": None,
            "deny_reason": None,
            "executed_at": None,
            "execute_record_id": None,
            "execute_success": None,
            "execute_error": None,
            "final_status": None
        }

        queue["pending"].append(item)
        queue["generated_at"] = datetime.now().isoformat()
        self._save_queue(queue)

        return approval_id

    def list_pending(self) -> List[Dict]:
        """列出待审批项"""
        queue = self._load_queue()
        return [item for item in queue.get("pending", []) if item.get("status") == "pending"]

    def grant(self, approval_id: str, owner: str) -> Dict:
        """批准并执行"""
        queue = self._load_queue()

        for item in queue.get("pending", []):
            if item.get("approval_id") == approval_id:
                item["status"] = "approved"
                item["approved_at"] = datetime.now().isoformat()
                item["approved_by"] = owner

                # 从队列移除
                queue["pending"] = [i for i in queue["pending"] if i.get("approval_id") != approval_id]
                self._save_queue(queue)

                # 执行动作
                action_type = item.get("action_type")
                action_params = item.get("action_params", {})
                execute_result = self._execute_approved_action(approval_id, action_type, action_params)

                # 更新执行结果
                item["executed_at"] = execute_result.get("executed_at")
                item["execute_record_id"] = execute_result.get("execute_record_id")
                item["execute_success"] = execute_result.get("success", False)
                item["execute_error"] = execute_result.get("error")

                # 状态统一
                if execute_result.get("success"):
                    item["status"] = "executed"
                    item["final_status"] = "executed"
                else:
                    item["status"] = "execute_failed"
                    item["final_status"] = "execute_failed"

                # 移到历史
                history = self._load_history()
                history["approvals"].append(item)
                self._save_history(history)

                return {
                    "success": True,
                    "approval_id": approval_id,
                    "status": "approved_and_executed",
                    "execute_success": execute_result.get("success", False),
                    "execute_record_id": execute_result.get("execute_record_id")
                }

        return {"success": False, "error": f"未找到审批项: {approval_id}"}

    def _execute_approved_action(self, approval_id: str, action_type: str, action_params: dict) -> Dict:
        """执行已批准的动作"""
        import subprocess
        import json

        # 调用 remediation_center 执行
        script = self.root / "scripts" / "remediation_center.py"
        if not script.exists():
            return {"success": False, "error": "remediation_center.py not found"}

        # 构建命令
        cmd = [sys.executable, str(script), "execute", action_type, "--approve", "--approval-id", approval_id]

        # 如果有参数，传递给脚本
        if action_params:
            cmd.extend(["--params", json.dumps(action_params)])

        result = subprocess.run(
            cmd,
            cwd=self.root,
            capture_output=True,
            text=True
        )

        # 从 latest_remediation.json 获取真实的 action_id
        latest_path = self.root / "reports" / "remediation" / "latest_remediation.json"
        execute_record_id = None
        if latest_path.exists():
            try:
                latest = json.load(open(latest_path))
                execute_record_id = latest.get("action_id")
            except:
                pass

        # 检查 history 文件是否存在
        if execute_record_id:
            history_file = self.root / "reports" / "remediation" / "history" / f"{execute_record_id}.json"
            if not history_file.exists():
                return {
                    "success": False,
                    "execute_record_id": execute_record_id,
                    "executed_at": datetime.now().isoformat(),
                    "error": "missing remediation history file"
                }

        return {
            "success": result.returncode == 0,
            "execute_record_id": execute_record_id,
            "executed_at": datetime.now().isoformat(),
            "output": result.stdout[:500] if result.stdout else "",
            "error": result.stderr[:200] if result.stderr else ""
        }

    def deny(self, approval_id: str, owner: str, reason: str) -> Dict:
        """拒绝"""
        queue = self._load_queue()

        for item in queue.get("pending", []):
            if item.get("approval_id") == approval_id:
                item["status"] = "denied"
                item["final_status"] = "denied"
                item["denied_at"] = datetime.now().isoformat()
                item["denied_by"] = owner
                item["deny_reason"] = reason

                # 移到历史
                history = self._load_history()
                history["approvals"].append(item)
                self._save_history(history)

                # 从队列移除
                queue["pending"] = [i for i in queue["pending"] if i.get("approval_id") != approval_id]
                self._save_queue(queue)

                return {"success": True, "approval_id": approval_id, "status": "denied"}

        return {"success": False, "error": f"未找到审批项: {approval_id}"}

    def record_execute(self, approval_id: str, execute_record_id: str):
        """记录执行结果"""
        history = self._load_history()

        for item in history.get("approvals", []):
            if item.get("approval_id") == approval_id:
                item["executed_at"] = datetime.now().isoformat()
                item["execute_record_id"] = execute_record_id
                self._save_history(history)
                return

    def is_semi_auto(self, action: str) -> bool:
        """检查是否是 semi_auto 动作"""
        return action in self.SEMI_AUTO_ACTIONS

def main():
    import argparse
    parser = argparse.ArgumentParser(description="审批管理")
    subparsers = parser.add_subparsers(dest="command")

    # list
    subparsers.add_parser("list", help="列出待审批项")

    # grant
    grant_parser = subparsers.add_parser("grant", help="批准")
    grant_parser.add_argument("approval_id", help="审批 ID")
    grant_parser.add_argument("owner", help="审批人")

    # deny
    deny_parser = subparsers.add_parser("deny", help="拒绝")
    deny_parser.add_argument("approval_id", help="审批 ID")
    deny_parser.add_argument("owner", help="审批人")
    deny_parser.add_argument("reason", help="拒绝原因")

    args = parser.parse_args()

    root = get_project_root()
    manager = ApprovalManager(root)

    if args.command == "list":
        pending = manager.list_pending()
        print("【待审批项】")
        if pending:
            for item in pending:
                print(f"  • {item['approval_id']}: {item['action_type']}")
                print(f"    原因: {item['reason']}")
                print(f"    时间: {item['created_at'][:19]}")
                print()
        else:
            print("  无")

    elif args.command == "grant":
        result = manager.grant(args.approval_id, args.owner)
        if result.get("success"):
            print(f"✅ 已批准: {args.approval_id}")
        else:
            print(f"❌ {result.get('error')}")

    elif args.command == "deny":
        result = manager.deny(args.approval_id, args.owner, args.reason)
        if result.get("success"):
            print(f"❌ 已拒绝: {args.approval_id}")
        else:
            print(f"❌ {result.get('error')}")

if __name__ == "__main__":
    main()
