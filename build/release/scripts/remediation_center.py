#!/usr/bin/env python3
"""
处置中心 - V1.1.0

统一处置入口，支持：
- plan: 输出建议处置动作
- dry-run: 模拟执行
- execute: 执行 safe_auto 动作
- auto-execute: 受控自动执行
- history: 查看处置历史
- guard: 查看熔断状态
- audit: 查看审计记录
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

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

class RemediationCenter:
    """处置中心"""

    SAFE_AUTO_ACTIONS = [
        "rebuild_dashboard",
        "rebuild_ops_state",
        "rebuild_bundle",
        "retry_notifications"
    ]

    SEMI_AUTO_ACTIONS = [
        "rerun_nightly",
        "rerun_release_gate",
        "rerun_integration",
        "toggle_incident"
    ]

    FORBIDDEN_ACTIONS = [
        "modify_core_arch",
        "modify_skill_registry",
        "modify_quality_rules",
        "delete_snapshots",
        "modify_release_decision",
        "clear_p2_backlog"
    ]

    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports"
        self.remediation_dir = self.reports_dir / "remediation"
        self.history_dir = self.remediation_dir / "history"
        self.policy_path = root / "infrastructure" / "remediation" / "remediation_policy.json"

        # 加载策略
        self.policy = load_json(self.policy_path) or {}

    def _generate_action_id(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"rem_{timestamp}_{os.getpid() % 1000:03d}"

    def _check_dashboard_status(self) -> Dict:
        """检查 dashboard 状态"""
        dashboard_path = self.reports_dir / "dashboard" / "ops_dashboard.json"
        if not dashboard_path.exists():
            return {"status": "missing", "action": "rebuild_dashboard", "reason": "dashboard 文件缺失"}

        # 检查是否过旧（超过 24 小时）
        import time
        mtime = dashboard_path.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours > 24:
            return {"status": "stale", "action": "rebuild_dashboard", "reason": f"dashboard 已过旧 ({age_hours:.1f} 小时)"}

        return {"status": "ok"}

    def _check_ops_state_status(self) -> Dict:
        """检查 ops_state 状态"""
        state_path = self.reports_dir / "ops" / "ops_state.json"
        if not state_path.exists():
            return {"status": "missing", "action": "rebuild_ops_state", "reason": "ops_state 文件缺失"}

        # 检查是否过旧（超过 1 小时）
        import time
        mtime = state_path.stat().st_mtime
        age_hours = (time.time() - mtime) / 3600
        if age_hours > 1:
            return {"status": "stale", "action": "rebuild_ops_state", "reason": f"ops_state 已过旧 ({age_hours:.1f} 小时)"}

        return {"status": "ok"}

    def _check_bundle_status(self) -> Dict:
        """检查 bundle 状态"""
        bundle_dir = self.reports_dir / "bundles"
        if not bundle_dir.exists() or not list(bundle_dir.glob("*.zip")):
            return {"status": "missing", "action": "rebuild_bundle", "reason": "无证据包"}

        # 检查最新 bundle 是否过旧
        bundles = sorted(bundle_dir.glob("*.zip"), reverse=True)
        if bundles:
            import time
            mtime = bundles[0].stat().st_mtime
            age_hours = (time.time() - mtime) / 3600
            if age_hours > 24:
                return {"status": "stale", "action": "rebuild_bundle", "reason": f"最新 bundle 已过旧 ({age_hours:.1f} 小时)"}

        return {"status": "ok"}

    def _check_notification_status(self) -> Dict:
        """检查通知状态"""
        result_path = self.reports_dir / "alerts" / "notification_result.json"
        if not result_path.exists():
            return {"status": "unknown", "action": None, "reason": "无通知结果"}

        result = load_json(result_path)
        if not result:
            return {"status": "unknown", "action": None, "reason": "无法读取通知结果"}

        failed = result.get("total_failed", 0)
        if failed > 0:
            return {"status": "failed", "action": "retry_notifications", "reason": f"{failed} 个通知发送失败"}

        return {"status": "ok"}

    def _get_suggest_only_issues(self) -> List[Dict]:
        """获取只能建议的问题"""
        issues = []

        # 检查 runtime gate
        runtime = load_json(self.reports_dir / "runtime_integrity.json")
        if runtime and not runtime.get("overall_passed", True):
            issues.append({
                "type": "runtime_gate_fail",
                "severity": "critical",
                "message": "Runtime gate 失败",
                "suggestion": "检查失败原因，修复代码问题",
                "auto_fix": False
            })

        # 检查 quality gate
        quality = load_json(self.reports_dir / "quality_gate.json")
        if quality and not quality.get("overall_passed", True):
            issues.append({
                "type": "quality_gate_fail",
                "severity": "critical",
                "message": "Quality gate 失败",
                "suggestion": "检查保护文件完整性",
                "auto_fix": False
            })

        # 检查 release gate
        release = load_json(self.reports_dir / "release_gate.json")
        if release and not release.get("can_release", True):
            issues.append({
                "type": "release_blocked",
                "severity": "critical",
                "message": "Release 被阻塞",
                "suggestion": "检查阻塞原因，人工决策",
                "auto_fix": False
            })

        # 检查 alerts
        alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json")
        if alerts:
            if alerts.get("blocking_count", 0) > 0:
                issues.append({
                    "type": "blocking_alerts",
                    "severity": "critical",
                    "message": f"存在 {alerts['blocking_count']} 个阻塞告警",
                    "suggestion": "处理阻塞告警",
                    "auto_fix": False
                })

            if alerts.get("strong_regressions"):
                issues.append({
                    "type": "strong_regression",
                    "severity": "high",
                    "message": "检测到强回归",
                    "suggestion": "分析回归原因",
                    "auto_fix": False
                })

        return issues

    def cmd_plan(self, save: bool = True) -> Dict:
        """输出建议处置动作"""
        print("╔══════════════════════════════════════════════════╗")
        print("║              处置建议                           ║")
        print("╚══════════════════════════════════════════════════╝")
        print()

        plan = {
            "generated_at": datetime.now().isoformat(),
            "safe_auto_actions": [],
            "suggest_only_issues": []
        }

        # 检查 safe_auto 触发条件
        checks = [
            self._check_dashboard_status(),
            self._check_ops_state_status(),
            self._check_bundle_status(),
            self._check_notification_status()
        ]

        print("【可自动修复的问题】")
        has_safe_auto = False
        for check in checks:
            if check.get("action"):
                has_safe_auto = True
                action = check["action"]
                reason = check["reason"]
                status = check["status"]
                print(f"  • {action}: {reason} ({status})")
                plan["safe_auto_actions"].append({
                    "action": action,
                    "reason": reason,
                    "status": status
                })

        if not has_safe_auto:
            print("  无")

        print()

        # 检查只能建议的问题
        print("【只能建议的问题（需人工处理）】")
        suggest_issues = self._get_suggest_only_issues()
        if suggest_issues:
            for issue in suggest_issues:
                print(f"  • [{issue['severity']}] {issue['message']}")
                print(f"    建议: {issue['suggestion']}")
                plan["suggest_only_issues"].append(issue)
        else:
            print("  无")

        print()

        # 输出建议命令
        if plan["safe_auto_actions"]:
            print("【建议执行的命令】")
            for item in plan["safe_auto_actions"]:
                print(f"  python scripts/remediation_center.py dry-run {item['action']}")
                print(f"  python scripts/remediation_center.py execute {item['action']}")
            print()

        # 保存 plan 结果
        if save:
            self.remediation_dir.mkdir(parents=True, exist_ok=True)
            plan_path = self.remediation_dir / "latest_remediation_plan.json"
            save_json(plan_path, plan)
            print(f"Plan 已保存: {plan_path}")
            print()

            # 更新 summary
            self._update_summary(plan)

        return plan

    def _record_action(self, action_id: str, action_type: str, mode: str,
                       triggered_by: str, source_alert: str = None,
                       source_incident: str = None):
        """记录动作开始"""
        return {
            "action_id": action_id,
            "action_type": action_type,
            "mode": mode,
            "triggered_by": triggered_by,
            "source_alert": source_alert,
            "source_incident": source_incident,
            "started_at": datetime.now().isoformat(),
            "finished_at": None,
            "success": False,
            "changed_files": [],
            "error": None,
            "requires_approval": action_type in self.SEMI_AUTO_ACTIONS
        }

    def _save_action_result(self, record: Dict):
        """保存动作结果"""
        # 保存到 latest
        latest_path = self.remediation_dir / "latest_remediation.json"
        save_json(latest_path, record)

        # 保存到 history
        self.history_dir.mkdir(parents=True, exist_ok=True)
        history_path = self.history_dir / f"{record['action_id']}.json"
        save_json(history_path, record)

        # 更新 summary
        self._update_summary_after_action(record)

    def _update_summary(self, plan: Dict = None):
        """更新 remediation_summary.json"""
        summary_path = self.remediation_dir / "remediation_summary.json"

        # 读取现有 summary
        summary = load_json(summary_path) or {}

        # 更新 plan 信息
        if plan:
            summary["latest_plan_generated_at"] = plan.get("generated_at")
            summary["pending_safe_actions"] = [a["action"] for a in plan.get("safe_auto_actions", [])]

        # 保存
        summary["updated_at"] = datetime.now().isoformat()
        summary["available_safe_actions"] = self.SAFE_AUTO_ACTIONS
        save_json(summary_path, summary)

    def _update_summary_after_action(self, record: Dict):
        """执行动作后更新 summary"""
        summary_path = self.remediation_dir / "remediation_summary.json"
        summary = load_json(summary_path) or {}

        summary["latest_execute_at"] = record.get("finished_at")
        summary["latest_action_type"] = record.get("action_type")
        summary["latest_action_success"] = record.get("success")
        summary["latest_action_id"] = record.get("action_id")

        # 统计最近失败
        if not record.get("success"):
            if "failed_recent_actions" not in summary:
                summary["failed_recent_actions"] = []
            summary["failed_recent_actions"].append(record.get("action_id"))
            summary["failed_recent_actions"] = summary["failed_recent_actions"][-10:]  # 保留最近10个

        summary["updated_at"] = datetime.now().isoformat()
        save_json(summary_path, summary)

    def _execute_command(self, command: str, timeout: int = 60) -> tuple:
        """执行命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)

    def cmd_dry_run(self, action: str) -> Dict:
        """模拟执行"""
        if action in self.FORBIDDEN_ACTIONS:
            print(f"❌ 动作 {action} 禁止自动执行")
            return {"error": "forbidden_action"}

        if action not in self.SAFE_AUTO_ACTIONS and action not in self.SEMI_AUTO_ACTIONS:
            print(f"❌ 未知动作: {action}")
            return {"error": "unknown_action"}

        print(f"╔══════════════════════════════════════════════════╗")
        print(f"║  Dry-Run: {action:<36} ║")
        print(f"╚══════════════════════════════════════════════════╝")
        print()

        action_id = self._generate_action_id()
        record = self._record_action(action_id, action, "dry-run", "manual")

        # 获取命令
        actions_config = self.policy.get("actions", {})
        action_config = actions_config.get(action, {})

        if action == "rebuild_dashboard":
            command = "python scripts/build_ops_dashboard.py"
            outputs = [
                "reports/dashboard/ops_dashboard.json",
                "reports/dashboard/ops_dashboard.md",
                "reports/dashboard/ops_dashboard.html"
            ]
        elif action == "rebuild_ops_state":
            command = "python scripts/ops_center.py status"
            outputs = ["reports/ops/ops_state.json"]
        elif action == "rebuild_bundle":
            command = "python scripts/ops_center.py bundle"
            outputs = ["reports/bundles/ops_bundle_*.zip"]
        elif action == "retry_notifications":
            command = "python scripts/remediation_center.py _retry_notifications"
            outputs = ["reports/alerts/notification_result.json"]
        else:
            command = action_config.get("command", "")
            outputs = action_config.get("outputs", [])

        print(f"【将要执行的命令】")
        print(f"  {command}")
        print()

        print(f"【将要修改的文件】")
        for f in outputs:
            print(f"  • {f}")
        print()

        print(f"【动作类型】")
        if action in self.SAFE_AUTO_ACTIONS:
            print(f"  ✅ safe_auto - 可自动执行")
        else:
            print(f"  ⚠️ semi_auto - 需要 --approve")
        print()

        print(f"【模拟结果】")
        print(f"  不会执行真实修改")
        print()

        record["finished_at"] = datetime.now().isoformat()
        record["success"] = True
        record["changed_files"] = outputs

        self._save_action_result(record)

        print(f"✅ Dry-run 完成: {action_id}")
        return record

    def _is_semi_auto(self, action: str) -> bool:
        """检查是否是 semi_auto 动作"""
        return action in self.SEMI_AUTO_ACTIONS

    def _add_to_approval_queue(self, action: str, reason: str,
                               source_alert: str = None, source_incident: str = None,
                               action_params: dict = None) -> Dict:
        """将 semi_auto 动作加入审批队列"""
        sys.path.insert(0, str(self.root))
        from scripts.approval_manager import ApprovalManager

        manager = ApprovalManager(self.root)
        approval_id = manager.add_to_queue(
            action, reason, "remediation_center",
            source_alert, source_incident, action_params
        )

        return {
            "status": "queued",
            "approval_id": approval_id,
            "action_type": action,
            "reason": reason,
            "source_alert": source_alert,
            "source_incident": source_incident,
            "action_params": action_params or {},
            "queued_at": datetime.now().isoformat()
        }

    def cmd_execute(self, action: str, approve: bool = False, approval_id: str = None, action_params: dict = None) -> Dict:
        """执行动作"""
        if action in self.FORBIDDEN_ACTIONS:
            print(f"❌ 动作 {action} 禁止自动执行")
            return {"error": "forbidden_action"}

        if action not in self.SAFE_AUTO_ACTIONS and action not in self.SEMI_AUTO_ACTIONS:
            print(f"❌ 未知动作: {action}")
            return {"error": "unknown_action"}

        # semi_auto 需要审批
        if action in self.SEMI_AUTO_ACTIONS and not approve:
            print(f"⚠️ 动作 {action} 需要审批")
            print(f"   正在加入审批队列...")

            # 检查 toggle_incident 是否有 incident_id
            if action == "toggle_incident":
                if not action_params or not action_params.get("incident_id"):
                    print(f"❌ toggle_incident 需要 incident_id 参数")
                    return {"error": "missing_incident_id"}

            # 自动入审批队列
            result = self._add_to_approval_queue(
                action, f"semi_auto action: {action}",
                action_params=action_params
            )
            print(f"   ✅ 已加入审批队列: {result['approval_id']}")
            print(f"   使用 ops_center.py approval grant {result['approval_id']} <owner> 批准执行")
            return result

        print(f"╔══════════════════════════════════════════════════╗")
        print(f"║  Execute: {action:<38} ║")
        print(f"╚══════════════════════════════════════════════════╝")
        print()

        action_id = self._generate_action_id()
        record = self._record_action(action_id, action, "execute", "manual" if not approval_id else "approval")

        # 执行命令
        if action == "rebuild_dashboard":
            command = "python scripts/build_ops_dashboard.py"
            timeout = 60
        elif action == "rebuild_ops_state":
            command = "python scripts/ops_center.py status"
            timeout = 30
        elif action == "rebuild_bundle":
            command = "python scripts/ops_center.py bundle"
            timeout = 60
        elif action == "retry_notifications":
            # 直接调用内部方法
            success, changed = self._retry_notifications_internal()
            record["finished_at"] = datetime.now().isoformat()
            record["success"] = success
            record["changed_files"] = changed
            self._save_action_result(record)
            if success:
                print(f"✅ 执行成功: {action_id}")
            else:
                print(f"❌ 执行失败: {action_id}")
            return record
        elif action == "rerun_nightly":
            command = "python scripts/run_release_gate.py nightly"
            timeout = 120
        elif action == "rerun_release_gate":
            command = "python scripts/run_release_gate.py release"
            timeout = 120
        elif action == "rerun_integration":
            command = "python infrastructure/verify_runtime_integrity.py --scope integration"
            timeout = 60
        elif action == "toggle_incident":
            if not action_params or not action_params.get("incident_id"):
                print(f"❌ toggle_incident 需要 incident_id 参数")
                record["finished_at"] = datetime.now().isoformat()
                record["success"] = False
                record["error"] = "missing incident_id"
                self._save_action_result(record)
                return record

            # 执行 incident 状态切换
            incident_id = action_params.get("incident_id")
            target_status = action_params.get("target_status", "resolved")

            # 调用 incident_cli
            incident_script = self.root / "scripts" / "incident_cli.py"
            if incident_script.exists():
                toggle_cmd = f"python scripts/incident_cli.py resolve {incident_id}"
                success, stdout, stderr = self._execute_command(toggle_cmd, 30)
                record["finished_at"] = datetime.now().isoformat()
                record["success"] = success
                record["changed_files"] = ["governance/ops/incident_tracker.json"]
                if success:
                    print(f"✅ Incident {incident_id} 已切换到 {target_status}")
                else:
                    record["error"] = stderr or stdout
                    print(f"❌ 切换失败: {stderr or stdout}")
            else:
                record["finished_at"] = datetime.now().isoformat()
                record["success"] = False
                record["error"] = "incident_cli.py not found"
                print(f"❌ incident_cli.py 不存在")
            self._save_action_result(record)
            return record
        elif action == "fix_config_drift":
            print(f"❌ fix_config_drift 暂不支持，请手动处理")
            record["finished_at"] = datetime.now().isoformat()
            record["success"] = False
            record["error"] = "not_implemented"
            self._save_action_result(record)
            return record
        else:
            print(f"❌ 未实现的动作: {action}")
            record["finished_at"] = datetime.now().isoformat()
            record["success"] = False
            record["error"] = "not_implemented"
            self._save_action_result(record)
            return record

        print(f"【执行命令】")
        print(f"  {command}")
        print()

        success, stdout, stderr = self._execute_command(command, timeout)

        record["finished_at"] = datetime.now().isoformat()
        record["success"] = success

        if success:
            # 根据动作类型确定 changed_files
            if action == "rebuild_dashboard":
                record["changed_files"] = [
                    "reports/dashboard/ops_dashboard.json",
                    "reports/dashboard/ops_dashboard.md",
                    "reports/dashboard/ops_dashboard.html"
                ]
            elif action == "rebuild_ops_state":
                record["changed_files"] = ["reports/ops/ops_state.json"]
            elif action == "rebuild_bundle":
                # 找到最新生成的 bundle
                bundle_dir = self.reports_dir / "bundles"
                if bundle_dir.exists():
                    bundles = sorted(bundle_dir.glob("ops_bundle_*.zip"), reverse=True)
                    if bundles:
                        record["changed_files"] = [f"reports/bundles/{bundles[0].name}"]
            elif action in ["rerun_nightly", "rerun_release_gate", "rerun_integration"]:
                record["changed_files"] = [
                    "reports/runtime_integrity.json",
                    "reports/quality_gate.json"
                ]

            print(f"【输出】")
            print(stdout[:500] if len(stdout) > 500 else stdout)
            print()
            print(f"【修改的文件】")
            for f in record["changed_files"]:
                print(f"  • {f}")
            print()
            print(f"✅ 执行成功: {action_id}")
        else:
            record["error"] = stderr or stdout or "Unknown error"
            print(f"【错误】")
            print(stderr or stdout)
            print()
            print(f"❌ 执行失败: {action_id}")

        self._save_action_result(record)

        # 如果是通过审批执行的，回填到 approval_history
        if approval_id and success:
            sys.path.insert(0, str(self.root))
            from scripts.approval_manager import ApprovalManager
            manager = ApprovalManager(self.root)
            manager.record_execute(approval_id, action_id)

        return record

    def _retry_notifications_internal(self) -> tuple:
        """内部方法：重试通知"""
        changed_files = []
        try:
            # 导入 NotificationManager
            sys.path.insert(0, str(self.root))
            from infrastructure.alerting.notification_manager import NotificationManager

            # 读取 latest_alerts
            alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json")
            if not alerts:
                print("无告警数据")
                return False, []

            # 重新发送通知
            nm = NotificationManager(self.root)
            result = nm.send_notifications(alerts)

            changed_files.append("reports/alerts/notification_result.json")

            # 检查是否有 history 更新
            history_path = self.reports_dir / "alerts" / "notification_history.json"
            if history_path.exists():
                changed_files.append("reports/alerts/notification_history.json")

            success = result.get("total_failed", 0) == 0
            print(f"通知结果: sent={result.get('total_sent', 0)}, failed={result.get('total_failed', 0)}")
            return success, changed_files
        except Exception as e:
            print(f"重试通知失败: {e}")
            import traceback
            traceback.print_exc()
            return False, changed_files

    def cmd_history(self, last: int = 10, action_type: str = None, failed: bool = False):
        """查看历史"""
        print("╔══════════════════════════════════════════════════╗")
        print("║              处置历史                           ║")
        print("╚══════════════════════════════════════════════════╝")
        print()

        if not self.history_dir.exists():
            print("无历史记录")
            return

        files = sorted(self.history_dir.glob("*.json"), reverse=True)[:last * 2]

        records = []
        for f in files:
            record = load_json(f)
            if record:
                # 过滤
                if action_type and record.get("action_type") != action_type:
                    continue
                if failed and record.get("success"):
                    continue
                records.append(record)

        records = records[:last]

        if not records:
            print("无匹配的历史记录")
            return

        for record in records:
            status = "✅" if record.get("success") else "❌"
            mode = record.get("mode", "?")
            action = record.get("action_type", "?")
            action_id = record.get("action_id", "?")
            started = record.get("started_at", "?")[:19]

            print(f"{status} [{mode}] {action}")
            print(f"   ID: {action_id}")
            print(f"   时间: {started}")
            if record.get("error"):
                print(f"   错误: {record['error']}")
            print()

    def cmd_internal_retry_notifications(self):
        """内部命令：重试通知"""
        success, changed = self._retry_notifications_internal()
        if success:
            print("✅ 通知重试成功")
        else:
            print("❌ 通知重试失败")
        return success

    # ==================== Auto Execute ====================

    def _load_guard_state(self) -> Dict:
        """加载熔断状态"""
        guard_path = self.remediation_dir / "remediation_guard.json"
        return load_json(guard_path) or {"guards": {}}

    def _save_guard_state(self, state: Dict):
        """保存熔断状态"""
        guard_path = self.remediation_dir / "remediation_guard.json"
        save_json(guard_path, state)

    def _load_auto_execute_policy(self) -> Dict:
        """加载自动执行策略"""
        policy_path = self.root / "infrastructure" / "remediation" / "auto_execute_policy.json"
        return load_json(policy_path) or {"profiles": {}, "default_profile": "manual_only"}

    def _generate_root_cause_key(self, action: str, plan_item: Dict = None) -> str:
        """生成根因标识"""
        if plan_item:
            # 基于 action + reason + status 生成稳定 key
            reason = plan_item.get("reason", "")
            status = plan_item.get("status", "")
            key_str = f"{action}:{reason}:{status}"
        else:
            key_str = action

        # 简单 hash
        import hashlib
        return hashlib.md5(key_str.encode()).hexdigest()[:12]

    def _check_cooldown(self, action: str, root_cause_key: str = None) -> tuple:
        """检查冷却期（支持 root_cause_key）"""
        policy = self._load_auto_execute_policy()
        cooldown_minutes = policy.get("cooldown", {}).get("action_specific", {}).get(action, 5)

        guard_state = self._load_guard_state()

        # 优先按 action + root_cause_key 查找
        guard_key = f"{action}:{root_cause_key}" if root_cause_key else action
        guard = guard_state.get("guards", {}).get(guard_key, {})

        # 如果没找到，尝试只按 action 查找
        if not guard and root_cause_key:
            guard = guard_state.get("guards", {}).get(action, {})

        last_attempt = guard.get("last_attempt_at")
        if last_attempt:
            last_time = datetime.fromisoformat(last_attempt)
            if datetime.now() - last_time < timedelta(minutes=cooldown_minutes):
                remaining = cooldown_minutes - (datetime.now() - last_time).seconds // 60
                return True, f"冷却中，剩余 {remaining} 分钟"

        return False, None

    def _check_circuit_breaker(self, action: str, root_cause_key: str = None) -> tuple:
        """检查熔断器（支持 root_cause_key）"""
        guard_state = self._load_guard_state()

        guard_key = f"{action}:{root_cause_key}" if root_cause_key else action
        guard = guard_state.get("guards", {}).get(guard_key, {})

        # 如果没找到，尝试只按 action 查找
        if not guard and root_cause_key:
            guard = guard_state.get("guards", {}).get(action, {})

        if guard.get("circuit_open"):
            opened_at = guard.get("circuit_opened_at")
            policy = self._load_auto_execute_policy()
            reset_minutes = policy.get("circuit_breaker", {}).get("actions", {}).get(action, {}).get("reset_minutes", 30)

            if opened_at:
                opened_time = datetime.fromisoformat(opened_at)
                if datetime.now() - opened_time < timedelta(minutes=reset_minutes):
                    return True, guard.get("circuit_reason", "熔断器开启")
                else:
                    # 重置熔断器
                    guard["circuit_open"] = False
                    guard["circuit_reason"] = None
                    guard_state["guards"][guard_key] = guard
                    self._save_guard_state(guard_state)

        return False, None

    def _check_retry_limit(self, action: str, root_cause_key: str = None) -> tuple:
        """检查重试上限（支持 root_cause_key）"""
        policy = self._load_auto_execute_policy()
        max_retry = policy.get("retry", {}).get("max_retry_count", 3)

        guard_state = self._load_guard_state()

        guard_key = f"{action}:{root_cause_key}" if root_cause_key else action
        guard = guard_state.get("guards", {}).get(guard_key, {})

        # 如果没找到，尝试只按 action 查找
        if not guard and root_cause_key:
            guard = guard_state.get("guards", {}).get(action, {})

        if guard.get("retry_count", 0) >= max_retry:
            return True, f"已达到重试上限 ({max_retry})"

        return False, None

    def _check_prerequisites(self, profile: str) -> Dict:
        """检查前置条件"""
        policy = self._load_auto_execute_policy()
        profile_config = policy.get("profiles", {}).get(profile, {})
        prereqs = profile_config.get("prerequisites", {})

        results = {"passed": True, "failures": []}

        if not prereqs:
            return results

        # 检查 blocking alerts
        if prereqs.get("no_blocking_alerts"):
            alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json")
            if alerts and alerts.get("blocking_count", 0) > 0:
                results["passed"] = False
                results["failures"].append(f"存在 {alerts['blocking_count']} 个阻塞告警")

        # 检查 strong regressions
        if prereqs.get("no_strong_regressions"):
            alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json")
            if alerts and alerts.get("strong_regressions"):
                results["passed"] = False
                results["failures"].append("存在强回归")

        # 检查 release blocked
        if prereqs.get("no_release_blocked"):
            release = load_json(self.reports_dir / "release_gate.json")
            if release and not release.get("can_release", True):
                results["passed"] = False
                results["failures"].append("Release 被阻塞")

        # 检查 release_gate_passed（显式检查）
        if prereqs.get("release_gate_passed"):
            release = load_json(self.reports_dir / "release_gate.json")
            if release:
                # 检查 runtime_gate 和 quality_gate
                runtime_passed = release.get("runtime_gate", {}).get("passed", False)
                quality_passed = release.get("quality_gate", {}).get("passed", False)
                can_release = release.get("can_release", False)

                if not (runtime_passed and quality_passed and can_release):
                    results["passed"] = False
                    if not runtime_passed:
                        results["failures"].append("Runtime gate 未通过")
                    if not quality_passed:
                        results["failures"].append("Quality gate 未通过")
                    if not can_release:
                        results["failures"].append("Release gate 未通过")

        # 检查 P0
        if prereqs.get("p0_must_be_zero"):
            runtime = load_json(self.reports_dir / "runtime_integrity.json")
            if runtime and runtime.get("p0_count", 0) > 0:
                results["passed"] = False
                results["failures"].append(f"P0 数量为 {runtime['p0_count']}")

        return results

    def _update_guard_after_execute(self, action: str, success: bool, error: str = None, root_cause_key: str = None):
        """执行后更新熔断状态（支持 root_cause_key）"""
        guard_state = self._load_guard_state()
        if "guards" not in guard_state:
            guard_state["guards"] = {}

        guard_key = f"{action}:{root_cause_key}" if root_cause_key else action

        guard = guard_state["guards"].get(guard_key, {
            "action_type": action,
            "root_cause_key": root_cause_key,
            "retry_count": 0,
            "circuit_open": False
        })

        guard["action_type"] = action
        guard["root_cause_key"] = root_cause_key
        guard["last_attempt_at"] = datetime.now().isoformat()

        if success:
            guard["last_success_at"] = datetime.now().isoformat()
            guard["retry_count"] = 0
        else:
            guard["retry_count"] = guard.get("retry_count", 0) + 1
            guard["last_error"] = error

            # 检查是否需要熔断
            policy = self._load_auto_execute_policy()
            threshold = policy.get("circuit_breaker", {}).get("actions", {}).get(action, {}).get("failure_threshold", 3)

            if guard["retry_count"] >= threshold:
                guard["circuit_open"] = True
                guard["circuit_reason"] = f"连续失败 {guard['retry_count']} 次"
                guard["circuit_opened_at"] = datetime.now().isoformat()

        guard_state["guards"][guard_key] = guard
        self._save_guard_state(guard_state)

    def _save_auto_execute_audit(self, audit: Dict):
        """保存自动执行审计"""
        # 保存到 latest
        audit_path = self.remediation_dir / "auto_execute_audit.json"
        save_json(audit_path, audit)

        # 保存到 history
        self.history_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_path = self.history_dir / f"{timestamp}_auto_execute.json"
        save_json(history_path, audit)

    def _save_auto_execute_summary(self, audit: Dict):
        """保存自动执行摘要"""
        summary_path = self.remediation_dir / "auto_execute_summary.json"

        summary = {
            "latest_profile": audit.get("profile"),
            "latest_workflow": audit.get("workflow"),
            "latest_executed_actions": audit.get("action_executed", []),
            "latest_denied_actions": audit.get("action_denied", []),
            "latest_deny_reasons": audit.get("deny_reasons", {}),
            "latest_remediation_record_ids": audit.get("remediation_record_ids", []),
            "cooldown_hits": audit.get("cooldown_hit", False),
            "circuit_open_hits": audit.get("circuit_open", False),
            "auto_execute_enabled": audit.get("auto_execute_enabled", False),
            "timestamp": audit.get("timestamp"),
            "updated_at": datetime.now().isoformat()
        }

        save_json(summary_path, summary)

    def cmd_auto_execute(self, profile: str, workflow: str = "manual") -> Dict:
        """受控自动执行"""
        print(f"╔══════════════════════════════════════════════════╗")
        print(f"║  Auto-Execute (profile: {profile:<22}) ║")
        print(f"╚══════════════════════════════════════════════════╝")
        print()

        # 检查是否开启
        policy = self._load_auto_execute_policy()
        profile_config = policy.get("profiles", {}).get(profile, {})

        if profile_config.get("require_explicit_enable"):
            env_var = profile_config.get("enable_env_var", "ENABLE_SAFE_REMEDIATION")
            enabled = os.environ.get(env_var, "false").lower() == "true"
            if not enabled:
                print(f"❌ 自动执行未开启 (需设置 {env_var}=true)")
                audit = {
                    "workflow": workflow,
                    "profile": profile,
                    "auto_execute_enabled": False,
                    "action_considered": [],
                    "action_executed": [],
                    "action_denied": [],
                    "deny_reasons": {"all": f"{env_var} 未设置"},
                    "preflight_result": "disabled",
                    "cooldown_hit": False,
                    "circuit_open": False,
                    "timestamp": datetime.now().isoformat()
                }
                self._save_auto_execute_audit(audit)
                return audit

        print(f"✅ 自动执行已开启")
        print()

        # 获取 plan（带详细信息用于生成 root_cause_key）
        plan = self._get_plan_internal()
        plan_actions = plan.get("safe_auto_actions", [])
        pending_actions = [a["action"] for a in plan_actions]

        if not pending_actions:
            print("无待处理的 safe_auto 动作")
            audit = {
                "workflow": workflow,
                "profile": profile,
                "auto_execute_enabled": True,
                "action_considered": [],
                "action_executed": [],
                "action_denied": [],
                "deny_reasons": {},
                "remediation_record_ids": [],
                "preflight_result": "no_actions",
                "cooldown_hit": False,
                "circuit_open": False,
                "timestamp": datetime.now().isoformat()
            }
            self._save_auto_execute_audit(audit)
            self._save_auto_execute_summary(audit)
            return audit

        print(f"【待处理动作】")
        for a in plan_actions:
            print(f"  • {a['action']}: {a.get('reason', '')}")
        print()

        # 检查前置条件
        prereq_result = self._check_prerequisites(profile)
        if not prereq_result["passed"]:
            print(f"❌ 前置条件不满足:")
            for f in prereq_result["failures"]:
                print(f"  • {f}")
            audit = {
                "workflow": workflow,
                "profile": profile,
                "auto_execute_enabled": True,
                "action_considered": pending_actions,
                "action_executed": [],
                "action_denied": pending_actions,
                "deny_reasons": {a: "; ".join(prereq_result["failures"]) for a in pending_actions},
                "remediation_record_ids": [],
                "preflight_result": "failed",
                "preflight_failures": prereq_result["failures"],
                "cooldown_hit": False,
                "circuit_open": False,
                "timestamp": datetime.now().isoformat()
            }
            self._save_auto_execute_audit(audit)
            self._save_auto_execute_summary(audit)
            return audit

        print(f"✅ 前置条件检查通过")
        print()

        # 逐个检查和执行
        executed = []
        denied = []
        deny_reasons = {}
        remediation_record_ids = []

        allowed_actions = profile_config.get("allowed_actions", [])

        for plan_item in plan_actions:
            action = plan_item["action"]

            # 生成 root_cause_key
            root_cause_key = self._generate_root_cause_key(action, plan_item)

            # 检查是否允许
            if action not in allowed_actions:
                denied.append(action)
                deny_reasons[action] = "不在允许列表中"
                continue

            # 检查冷却（带 root_cause_key）
            in_cooldown, cooldown_reason = self._check_cooldown(action, root_cause_key)
            if in_cooldown:
                denied.append(action)
                deny_reasons[action] = cooldown_reason
                continue

            # 检查熔断（带 root_cause_key）
            circuit_open, circuit_reason = self._check_circuit_breaker(action, root_cause_key)
            if circuit_open:
                denied.append(action)
                deny_reasons[action] = circuit_reason
                continue

            # 检查重试上限（带 root_cause_key）
            over_limit, limit_reason = self._check_retry_limit(action, root_cause_key)
            if over_limit:
                denied.append(action)
                deny_reasons[action] = limit_reason
                continue

            # 执行
            print(f"【执行】{action} (root_cause: {root_cause_key})")
            result = self.cmd_execute(action)
            record_id = result.get("action_id")

            if result.get("success"):
                executed.append(action)
                if record_id:
                    remediation_record_ids.append(record_id)
                self._update_guard_after_execute(action, True, None, root_cause_key)
            else:
                denied.append(action)
                deny_reasons[action] = result.get("error", "执行失败")
                self._update_guard_after_execute(action, False, result.get("error"), root_cause_key)

        # 保存审计
        audit = {
            "workflow": workflow,
            "profile": profile,
            "auto_execute_enabled": True,
            "action_considered": pending_actions,
            "action_executed": executed,
            "action_denied": denied,
            "deny_reasons": deny_reasons,
            "remediation_record_ids": remediation_record_ids,
            "preflight_result": "passed",
            "cooldown_hit": len([r for r in deny_reasons.values() if "冷却" in r]) > 0,
            "circuit_open": len([r for r in deny_reasons.values() if "熔断" in r]) > 0,
            "timestamp": datetime.now().isoformat()
        }
        self._save_auto_execute_audit(audit)
        self._save_auto_execute_summary(audit)

        print()
        print(f"【执行结果】")
        print(f"  执行: {executed if executed else '无'}")
        print(f"  拒绝: {denied if denied else '无'}")
        if remediation_record_ids:
            print(f"  记录ID: {remediation_record_ids}")
        if deny_reasons:
            print(f"  拒绝原因:")
            for a, r in deny_reasons.items():
                print(f"    • {a}: {r}")

        return audit

    def _get_plan_internal(self) -> Dict:
        """内部方法：获取 plan"""
        plan = {
            "generated_at": datetime.now().isoformat(),
            "safe_auto_actions": [],
            "suggest_only_issues": []
        }

        checks = [
            self._check_dashboard_status(),
            self._check_ops_state_status(),
            self._check_bundle_status(),
            self._check_notification_status()
        ]

        for check in checks:
            if check.get("action"):
                plan["safe_auto_actions"].append({
                    "action": check["action"],
                    "reason": check["reason"],
                    "status": check["status"]
                })

        return plan

    def cmd_guard(self, reset: str = None):
        """查看熔断状态"""
        print("╔══════════════════════════════════════════════════╗")
        print("║              熔断状态                           ║")
        print("╚══════════════════════════════════════════════════╝")
        print()

        guard_state = self._load_guard_state()

        if reset:
            # 重置熔断器
            if reset in guard_state.get("guards", {}):
                guard_state["guards"][reset]["circuit_open"] = False
                guard_state["guards"][reset]["circuit_reason"] = None
                guard_state["guards"][reset]["retry_count"] = 0
                self._save_guard_state(guard_state)
                print(f"✅ 已重置 {reset} 的熔断器")
                print()
            else:
                print(f"❌ 未找到 {reset} 的熔断记录")
                print()

        guards = guard_state.get("guards", {})
        if not guards:
            print("无熔断记录")
            return

        for action, guard in guards.items():
            status = "🔴 熔断" if guard.get("circuit_open") else "🟢 正常"
            print(f"{status} {action}")
            print(f"   重试次数: {guard.get('retry_count', 0)}")
            print(f"   最后尝试: {guard.get('last_attempt_at', 'N/A')[:19]}")
            if guard.get("root_cause_key"):
                print(f"   根因标识: {guard.get('root_cause_key')}")
            if guard.get("circuit_open"):
                print(f"   熔断原因: {guard.get('circuit_reason', 'N/A')}")
                print(f"   熔断时间: {guard.get('circuit_opened_at', 'N/A')[:19]}")
            print()

    def cmd_audit(self, last: int = 10, denied: bool = False, workflow: str = None):
        """查看审计记录"""
        print("╔══════════════════════════════════════════════════╗")
        print("║              自动执行审计                       ║")
        print("╚══════════════════════════════════════════════════╝")
        print()

        # 查找 auto_execute 审计文件
        audit_files = sorted(self.history_dir.glob("*_auto_execute.json"), reverse=True)[:last * 2]

        records = []
        for f in audit_files:
            record = load_json(f)
            if record:
                if workflow and record.get("workflow") != workflow:
                    continue
                if denied and not record.get("action_denied"):
                    continue
                records.append(record)

        records = records[:last]

        if not records:
            print("无审计记录")
            return

        for record in records:
            enabled = "✅" if record.get("auto_execute_enabled") else "❌"
            profile = record.get("profile", "?")
            wf = record.get("workflow", "?")
            executed = record.get("action_executed", [])
            denied_actions = record.get("action_denied", [])
            record_ids = record.get("remediation_record_ids", [])

            print(f"{enabled} [{profile}] {wf}")
            print(f"   执行: {executed if executed else '无'}")
            if record_ids:
                print(f"   记录ID: {record_ids}")
            if denied_actions:
                print(f"   拒绝: {denied_actions}")
                for a, r in record.get("deny_reasons", {}).items():
                    if a in denied_actions:
                        print(f"     • {a}: {r}")
            print(f"   时间: {record.get('timestamp', '?')[:19]}")
            print()

def main():
    parser = argparse.ArgumentParser(description="处置中心")
    subparsers = parser.add_subparsers(dest="command", help="命令")

    # plan
    subparsers.add_parser("plan", help="输出建议处置动作")

    # dry-run
    dry_run_parser = subparsers.add_parser("dry-run", help="模拟执行")
    dry_run_parser.add_argument("action", help="动作名称")

    # execute
    execute_parser = subparsers.add_parser("execute", help="执行动作")
    execute_parser.add_argument("action", help="动作名称")
    execute_parser.add_argument("--approve", action="store_true", help="批准执行 semi_auto 动作")
    execute_parser.add_argument("--approval-id", help="审批 ID（用于回填执行记录）")
    execute_parser.add_argument("--params", help="动作参数（JSON 格式）")

    # auto-execute
    auto_exec_parser = subparsers.add_parser("auto-execute", help="受控自动执行")
    auto_exec_parser.add_argument("--profile", default="nightly_auto", help="执行策略 (nightly_auto/release_auto/manual_only)")
    auto_exec_parser.add_argument("--workflow", default="manual", help="来源 workflow")

    # history
    history_parser = subparsers.add_parser("history", help="查看历史")
    history_parser.add_argument("--last", type=int, default=10, help="最近 N 条")
    history_parser.add_argument("--type", help="过滤动作类型")
    history_parser.add_argument("--failed", action="store_true", help="只显示失败的")

    # guard
    guard_parser = subparsers.add_parser("guard", help="查看熔断状态")
    guard_parser.add_argument("--reset", help="重置指定动作的熔断器")

    # audit
    audit_parser = subparsers.add_parser("audit", help="查看自动执行审计")
    audit_parser.add_argument("--last", type=int, default=10, help="最近 N 条")
    audit_parser.add_argument("--denied", action="store_true", help="只显示被拒绝的")
    audit_parser.add_argument("--workflow", help="过滤 workflow")

    # internal
    subparsers.add_parser("_retry_notifications", help="内部命令：重试通知")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    root = get_project_root()
    rc = RemediationCenter(root)

    if args.command == "plan":
        rc.cmd_plan()
    elif args.command == "dry-run":
        rc.cmd_dry_run(args.action)
    elif args.command == "execute":
        params = json.loads(args.params) if hasattr(args, 'params') and args.params else None
        rc.cmd_execute(args.action, args.approve, getattr(args, 'approval_id', None), params)
    elif args.command == "auto-execute":
        rc.cmd_auto_execute(args.profile, args.workflow)
    elif args.command == "history":
        rc.cmd_history(args.last, args.type, args.failed)
    elif args.command == "guard":
        rc.cmd_guard(args.reset)
    elif args.command == "audit":
        rc.cmd_audit(args.last, args.denied, args.workflow)
    elif args.command == "_retry_notifications":
        rc.cmd_internal_retry_notifications()

    return 0

if __name__ == "__main__":
    sys.exit(main())
