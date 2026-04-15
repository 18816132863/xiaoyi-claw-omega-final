#!/usr/bin/env python3
"""
运维中心 - V1.1.0

统一运维入口，支持：
- status: 查看总状态
- verify: 运行门禁
- incidents: 管理 incidents
- alerts: 查看告警
- dashboard: 构建看板
- bundle: 打包证据
- remediation: 处置管理
"""

import os
import sys
import json
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime
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

class OpsCenter:
    """运维中心"""
    
    def __init__(self, root: Path):
        self.root = root
        self.reports_dir = root / "reports"
        self.state_path = self.reports_dir / "ops" / "ops_state.json"
    
    # ==================== Status ====================
    
    def rules_status(self) -> Dict:
        """规则状态"""
        rule_report = load_json(self.reports_dir / "ops/rule_engine_report.json") or {}
        return {
            "status": "success",
            "rules": rule_report
        }
    
    def exceptions_status(self) -> Dict:
        """例外状态"""
        status = load_json(self.reports_dir / "ops/rule_exception_status.json") or {}
        return {
            "status": "success",
            "exceptions": status
        }
    
    def exceptions_debt(self) -> Dict:
        """例外债务"""
        debt = load_json(self.reports_dir / "ops/rule_exception_debt.json") or {}
        return {
            "status": "success",
            "debt": debt
        }
    
    def exceptions_approvals(self) -> Dict:
        """例外审批"""
        queue = load_json(self.reports_dir / "ops/exception_approval_queue.json") or {}
        return {
            "status": "success",
            "queue": queue
        }
    
    def get_state(self) -> Dict:
        """获取统一状态"""
        # 加载各报告
        runtime = load_json(self.reports_dir / "runtime_integrity.json")
        quality = load_json(self.reports_dir / "quality_gate.json")
        release = load_json(self.reports_dir / "release_gate.json")
        alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json")
        incident_summary = load_json(self.reports_dir / "alerts" / "incident_summary.json")
        dashboard = load_json(self.reports_dir / "dashboard" / "ops_dashboard.json")
        
        # 构建状态
        state = {
            "generated_at": datetime.now().isoformat(),
            "overall_status": "unknown",
            "runtime_status": runtime.get("overall_passed", False) if runtime else None,
            "quality_status": quality.get("overall_passed", False) if quality else None,
            "release_status": release.get("can_release", False) if release else None,
            "blocking_alerts": alerts.get("blocking_count", 0) if alerts else 0,
            "warning_alerts": alerts.get("warning_count", 0) if alerts else 0,
            "open_incidents": incident_summary.get("open_incidents", 0) if incident_summary else 0,
            "resolved_incidents": incident_summary.get("resolved_incidents", 0) if incident_summary else 0,
            "can_release": release.get("can_release", False) if release else None,
            "latest_blocked_reason": None,
            "latest_incident_id": None,
            "latest_dashboard_path": str(self.reports_dir / "dashboard" / "ops_dashboard.json"),
            "latest_bundle_path": None,
            "details": {
                "runtime": runtime,
                "quality": quality,
                "release": release,
                "alerts": alerts,
                "incident_summary": incident_summary
            }
        }
        
        # 计算总体状态
        if state["blocking_alerts"] > 0 or state["open_incidents"] > 0:
            state["overall_status"] = "blocking"
        elif state["warning_alerts"] > 0:
            state["overall_status"] = "warning"
        elif state["runtime_status"] and state["quality_status"] and state["can_release"]:
            state["overall_status"] = "healthy"
        else:
            state["overall_status"] = "degraded"
        
        # 提取阻塞原因
        if alerts and alerts.get("blocked_reasons"):
            state["latest_blocked_reason"] = alerts["blocked_reasons"][0] if alerts["blocked_reasons"] else None
        
        # 提取最新 incident
        if incident_summary and incident_summary.get("latest_opened_at"):
            # 找到对应的 incident_id
            incidents = load_json(self.root / "governance/ops" / "incident_tracker.json") or []
            for inc in incidents:
                if inc.get("status") == "open":
                    state["latest_incident_id"] = inc.get("incident_id")
                    break
        
        # 查找最新 bundle
        bundle_dir = self.reports_dir / "bundles"
        if bundle_dir.exists():
            bundles = sorted(bundle_dir.glob("ops_bundle_*.zip"), reverse=True)
            if bundles:
                state["latest_bundle_path"] = str(bundles[0])
        
        return state
    
    def save_state(self, state: Dict):
        """保存状态"""
        save_json(self.state_path, state)
    
    def cmd_status(self):
        """显示状态"""
        state = self.get_state()
        self.save_state(state)
        
        print("╔══════════════════════════════════════════════════╗")
        print("║              运维状态总览                       ║")
        print("╚══════════════════════════════════════════════════╝")
        print()
        
        # 总体状态
        status_map = {
            "healthy": ("✅ 健康", "green"),
            "warning": ("⚠️ 警告", "yellow"),
            "blocking": ("🚨 阻塞", "red"),
            "degraded": ("📉 降级", "orange"),
            "unknown": ("❓ 未知", "gray")
        }
        status_text, _ = status_map.get(state["overall_status"], ("❓ 未知", "gray"))
        print(f"总体状态: {status_text}")
        print()
        
        # 各模块状态
        print("【模块状态】")
        print(f"  Runtime: {'✅' if state['runtime_status'] else '❌'}")
        print(f"  Quality: {'✅' if state['quality_status'] else '❌'}")
        print(f"  Release: {'✅' if state['can_release'] else '❌'}")
        print()
        
        # 告警
        print("【告警】")
        print(f"  阻塞级: {state['blocking_alerts']}")
        print(f"  警告级: {state['warning_alerts']}")
        print()
        
        # Incidents
        print("【Incidents】")
        print(f"  Open: {state['open_incidents']}")
        print(f"  Resolved: {state['resolved_incidents']}")
        if state['latest_incident_id']:
            print(f"  最新: {state['latest_incident_id']}")
        print()
        
        # 阻塞原因
        if state['latest_blocked_reason']:
            print(f"【阻塞原因】")
            print(f"  {state['latest_blocked_reason']}")
            print()
        
        # 路径
        print("【文件路径】")
        print(f"  Dashboard: {state['latest_dashboard_path']}")
        if state['latest_bundle_path']:
            print(f"  Bundle: {state['latest_bundle_path']}")
        print(f"  State: {self.state_path}")
        
        return state
    
    # ==================== Verify ====================
    
    def cmd_verify(self, profile: str = "premerge"):
        """运行门禁"""
        print(f"运行 {profile} 门禁...")
        
        script = self.root / "scripts" / "run_release_gate.py"
        result = subprocess.run([sys.executable, str(script), profile], cwd=self.root)
        
        return result.returncode
    
    # ==================== Incidents ====================
    
    def cmd_incidents(self, action: str, args: List[str] = None):
        """管理 incidents"""
        args = args or []
        
        if action == "list":
            self._list_incidents(args[0] if args else None)
        elif action == "acknowledge":
            self._acknowledge_incident(args[0] if args else None, args[1] if len(args) > 1 else None)
        elif action == "resolve":
            self._resolve_incident(args[0] if args else None, " ".join(args[1:]) if len(args) > 1 else "手动关闭")
        elif action == "annotate":
            self._annotate_incident(args[0] if args else None, " ".join(args[1:]) if len(args) > 1 else "")
        else:
            print(f"未知操作: {action}")
            print("用法: ops_center.py incidents [list|acknowledge|resolve|annotate] [args]")
    
    def _list_incidents(self, status_filter: str = None):
        """列出 incidents"""
        incidents = load_json(self.root / "governance/ops" / "incident_tracker.json") or []
        
        if status_filter:
            incidents = [i for i in incidents if i.get("status") == status_filter]
        
        if not incidents:
            print("无 incident")
            return
        
        print(f"共 {len(incidents)} 个 incident:")
        print()
        
        for inc in incidents:
            status_icon = "🔴" if inc.get("status") == "open" else "🟢"
            print(f"{status_icon} {inc.get('incident_id', '?')}")
            print(f"   类型: {inc.get('alert_type', '?')}")
            print(f"   状态: {inc.get('status', '?')}")
            print(f"   打开: {inc.get('opened_at', '?')[:19] if inc.get('opened_at') else '?'}")
            if inc.get("resolved_at"):
                print(f"   关闭: {inc.get('resolved_at')[:19]}")
            print()
    
    def _acknowledge_incident(self, incident_id: str, owner: str):
        """确认 incident"""
        if not incident_id:
            print("用法: ops_center.py incidents acknowledge <id> [owner]")
            return
        
        incidents = load_json(self.root / "governance/ops" / "incident_tracker.json") or []
        
        for inc in incidents:
            if inc.get("incident_id") == incident_id:
                inc["status"] = "acknowledged"
                if owner:
                    inc["owner"] = owner
                inc["acknowledged_at"] = datetime.now().isoformat()
                save_json(self.root / "governance/ops" / "incident_tracker.json", incidents)
                print(f"✅ 已确认 {incident_id}")
                return
        
        print(f"❌ 未找到 {incident_id}")
    
    def _resolve_incident(self, incident_id: str, note: str):
        """关闭 incident"""
        if not incident_id:
            print("用法: ops_center.py incidents resolve <id> [note]")
            return
        
        incidents = load_json(self.root / "governance/ops" / "incident_tracker.json") or []
        
        for inc in incidents:
            if inc.get("incident_id") == incident_id:
                inc["status"] = "resolved"
                inc["resolved_at"] = datetime.now().isoformat()
                inc["resolution_note"] = note
                save_json(self.root / "governance/ops" / "incident_tracker.json", incidents)
                print(f"✅ 已关闭 {incident_id}")
                return
        
        print(f"❌ 未找到 {incident_id}")
    
    def _annotate_incident(self, incident_id: str, note: str):
        """添加备注"""
        if not incident_id or not note:
            print("用法: ops_center.py incidents annotate <id> <note>")
            return
        
        incidents = load_json(self.root / "governance/ops" / "incident_tracker.json") or []
        
        for inc in incidents:
            if inc.get("incident_id") == incident_id:
                if "annotations" not in inc:
                    inc["annotations"] = []
                inc["annotations"].append({
                    "timestamp": datetime.now().isoformat(),
                    "note": note
                })
                save_json(self.root / "governance/ops" / "incident_tracker.json", incidents)
                print(f"✅ 已添加备注到 {incident_id}")
                return
        
        print(f"❌ 未找到 {incident_id}")
    
    # ==================== Alerts ====================
    
    def cmd_alerts(self, action: str = "latest"):
        """查看告警"""
        if action == "latest":
            alerts = load_json(self.reports_dir / "alerts" / "latest_alerts.json")
            if not alerts:
                print("无告警报告")
                return
            
            print("【最新告警】")
            print(f"生成时间: {alerts.get('generated_at', '?')}")
            print(f"来源: {alerts.get('source_workflow', '?')}")
            print(f"阻塞级: {alerts.get('blocking_count', 0)}")
            print(f"警告级: {alerts.get('warning_count', 0)}")
            print()
            
            if alerts.get("alerts"):
                print("【告警详情】")
                for alert in alerts["alerts"]:
                    icon = "🚨" if alert.get("severity") == "blocking" else "⚠️"
                    print(f"  {icon} {alert.get('alert_type')}: {alert.get('message')}")
        
        elif action == "history":
            history_dir = self.reports_dir / "alerts" / "history"
            if not history_dir.exists():
                print("无历史记录")
                return
            
            files = sorted(history_dir.glob("*.json"), reverse=True)[:10]
            print(f"最近 {len(files)} 条历史:")
            for f in files:
                data = load_json(f)
                if data:
                    print(f"  {f.name}: {data.get('blocking_count', 0)} 阻塞, {data.get('warning_count', 0)} 警告")
        
        elif action == "notifications":
            result = load_json(self.reports_dir / "alerts" / "notification_result.json")
            if result:
                print("【最新通知结果】")
                print(f"发送时间: {result.get('sent_at', '?')}")
                print(f"成功: {result.get('total_sent', 0)}")
                print(f"失败: {result.get('total_failed', 0)}")
                for ch in result.get("channels", []):
                    status = "✅" if ch.get("sent") else "❌"
                    print(f"  {status} {ch.get('channel')}: {ch.get('error') or 'OK'}")
    
    # ==================== Dashboard ====================
    
    def cmd_dashboard(self, action: str = "build"):
        """构建看板"""
        if action == "build":
            print("构建看板...")
            script = self.root / "scripts" / "build_ops_dashboard.py"
            result = subprocess.run([sys.executable, str(script)], cwd=self.root)
            
            if result.returncode == 0:
                print()
                print("✅ 看板已生成:")
                print(f"  JSON: {self.reports_dir / 'dashboard' / 'ops_dashboard.json'}")
                print(f"  MD: {self.reports_dir / 'dashboard' / 'ops_dashboard.md'}")
                print(f"  HTML: {self.reports_dir / 'dashboard' / 'ops_dashboard.html'}")
            
            return result.returncode
    
    # ==================== Bundle ====================
    
    def cmd_bundle(self):
        """打包证据"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bundle_dir = self.reports_dir / "bundles"
        bundle_dir.mkdir(parents=True, exist_ok=True)
        
        bundle_path = bundle_dir / f"ops_bundle_{timestamp}.zip"
        
        # 要打包的文件
        files_to_bundle = [
            "runtime_integrity.json",
            "quality_gate.json",
            "release_gate.json",
            "nightly_audit.json",
            "alerts/latest_alerts.json",
            "alerts/incident_summary.json",
            "alerts/notification_result.json",
            "dashboard/ops_dashboard.json",
            "dashboard/ops_dashboard.md",
            "trends/gate_trend.json",
        ]
        
        # 添加 incident_tracker
        incident_path = self.root / "governance/ops" / "incident_tracker.json"
        
        print(f"打包证据包: {bundle_path}")
        
        with zipfile.ZipFile(bundle_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in files_to_bundle:
                src = self.reports_dir / f
                if src.exists():
                    zf.write(src, f"reports/{f}")
                    print(f"  + {f}")
            
            if incident_path.exists():
                zf.write(incident_path, "governance/ops/incident_tracker.json")
                print(f"  + governance/ops/incident_tracker.json")
            
            # 添加 ops_state
            state = self.get_state()
            state["latest_bundle_path"] = str(bundle_path)
            self.save_state(state)
            zf.writestr("ops_state.json", json.dumps(state, ensure_ascii=False, indent=2))
            print(f"  + ops_state.json")
        
        print()
        print(f"✅ 证据包已生成: {bundle_path}")
        print(f"   大小: {bundle_path.stat().st_size / 1024:.1f} KB")

        return str(bundle_path)

    def cmd_control_plane(self, args: list) -> int:
        """控制平面命令"""
        subcommand = args[0] if args else "status"

        if subcommand == "status":
            # 生成并显示控制平面状态
            script = self.root / "scripts" / "control_plane.py"
            if script.exists():
                result = subprocess.run([sys.executable, str(script)], cwd=self.root)
                return result.returncode
            else:
                print("❌ control_plane.py 不存在")
                return 1

        elif subcommand == "summary":
            # 显示摘要
            state = load_json(self.reports_dir / "ops" / "control_plane_state.json")
            if state:
                print("【控制平面摘要】")
                print(f"  Runtime: {'✅' if state.get('overview', {}).get('runtime_passed') else '❌'}")
                print(f"  Quality: {'✅' if state.get('overview', {}).get('quality_passed') else '❌'}")
                print(f"  Release: {'✅' if state.get('overview', {}).get('can_release') else '❌'}")
                print(f"  Blocking alerts: {state.get('alerts', {}).get('blocking_count', 0)}")
                print(f"  Open incidents: {state.get('incidents', {}).get('open', 0)}")
            else:
                print("❌ 控制平面状态不存在，请先运行 control-plane status")
            return 0

        elif subcommand == "audit":
            # 生成并显示审计
            script = self.root / "scripts" / "control_plane_audit.py"
            if script.exists():
                result = subprocess.run([sys.executable, str(script)], cwd=self.root)
                return result.returncode
            else:
                print("❌ control_plane_audit.py 不存在")
                return 1

        elif subcommand == "export":
            # 导出
            return self._export_control_plane()

        else:
            print(f"未知子命令: {subcommand}")
            return 1

    def _export_control_plane(self) -> int:
        """导出控制平面"""
        import zipfile

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = self.reports_dir / "ops" / f"control_plane_export_{timestamp}.zip"

        files_to_export = [
            "ops/control_plane_state.json",
            "ops/control_plane_audit.json",
            "ops/ops_state.json",
            "remediation/approval_queue.json",
            "remediation/approval_history.json",
            "remediation/auto_execute_audit.json",
            "remediation/auto_execute_summary.json",
        ]

        print(f"导出控制平面: {export_path}")

        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in files_to_export:
                src = self.reports_dir / f
                if src.exists():
                    zf.write(src, f)
                    print(f"  + {f}")

        print()
        print(f"✅ 导出完成: {export_path}")
        print(f"   大小: {export_path.stat().st_size / 1024:.1f} KB")
        return 0

    def cmd_approval(self, args: list) -> int:
        """审批命令"""
        script = self.root / "scripts" / "approval_manager.py"
        if not script.exists():
            print("❌ approval_manager.py 不存在")
            return 1

        result = subprocess.run([sys.executable, str(script)] + args, cwd=self.root)
        return result.returncode

def main():
    if len(sys.argv) < 2:
        print("用法: ops_center.py <command> [args]")
        print()
        print("命令:")
        print("  status                    - 查看总状态")
        print("  verify [profile]          - 运行门禁 (premerge/nightly/release)")
        print("  incidents list [status]   - 列出 incidents")
        print("  incidents ack <id> [owner] - 确认 incident")
        print("  incidents resolve <id> [note] - 关闭 incident")
        print("  incidents annotate <id> <note> - 添加备注")
        print("  alerts [latest|history|notifications] - 查看告警")
        print("  dashboard build           - 构建看板")
        print("  bundle                    - 打包证据")
        print("  remediation plan          - 查看处置建议")
        print("  remediation dry-run <action> - 模拟执行处置")
        print("  remediation execute <action> - 执行处置")
        print("  remediation auto-execute --profile <profile> - 受控自动执行")
        print("  remediation history       - 查看处置历史")
        print("  guard [--reset <action>]  - 查看熔断状态")
        print("  audit [--denied]          - 查看自动执行审计")
        print("  control-plane status      - 生成控制平面状态")
        print("  control-plane summary     - 显示控制平面摘要")
        print("  control-plane audit       - 生成控制平面审计")
        print("  control-plane export      - 导出控制平面")
        print("  approval list             - 列出待审批项")
        print("  approval grant <id> <owner> - 批准")
        print("  approval deny <id> <owner> <reason> - 拒绝")
        print("  rules status              - 规则状态")
        print("  exceptions status         - 例外状态")
        print("  exceptions debt           - 例外债务")
        print("  exceptions approvals      - 例外审批")
        return 0

    root = get_project_root()
    ops = OpsCenter(root)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "status":
        ops.cmd_status()
    elif command == "verify":
        profile = args[0] if args else "premerge"
        return ops.cmd_verify(profile)
    elif command == "incidents":
        action = args[0] if args else "list"
        ops.cmd_incidents(action, args[1:])
    elif command == "alerts":
        action = args[0] if args else "latest"
        ops.cmd_alerts(action)
    elif command == "dashboard":
        action = args[0] if args else "build"
        return ops.cmd_dashboard(action)
    elif command == "bundle":
        ops.cmd_bundle()
    elif command == "remediation":
        # 调用 remediation_center
        remediation_script = root / "scripts" / "remediation_center.py"
        if not remediation_script.exists():
            print("❌ remediation_center.py 不存在")
            return 1
        result = subprocess.run([sys.executable, str(remediation_script)] + args, cwd=root)
        return result.returncode
    elif command == "guard":
        # 查看熔断状态
        remediation_script = root / "scripts" / "remediation_center.py"
        if remediation_script.exists():
            result = subprocess.run([sys.executable, str(remediation_script), "guard"] + args, cwd=root)
            return result.returncode
    elif command == "audit":
        # 查看审计记录
        remediation_script = root / "scripts" / "remediation_center.py"
        if remediation_script.exists():
            result = subprocess.run([sys.executable, str(remediation_script), "audit"] + args, cwd=root)
            return result.returncode
    elif command == "control-plane":
        # 控制平面命令
        return ops.cmd_control_plane(args)
    elif command == "approval":
        # 审批命令
        return ops.cmd_approval(args)
    elif command == "rules":
        # 规则状态
        result = ops.rules_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "exceptions":
        # 例外状态
        subcmd = args[0] if args else "status"
        if subcmd == "status":
            result = ops.exceptions_status()
        elif subcmd == "debt":
            result = ops.exceptions_debt()
        elif subcmd == "approvals":
            result = ops.exceptions_approvals()
        else:
            result = ops.exceptions_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"未知命令: {command}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
