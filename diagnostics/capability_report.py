"""
Capability Report - 能力报告
"""

from typing import Dict, Any, List
from datetime import datetime


class CapabilityReport:
    """能力报告生成器"""
    
    @staticmethod
    def generate() -> Dict[str, Any]:
        """生成能力报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "runtime_mode": "skill_default",
            "capabilities": {},
            "platform": {},
            "limitations": [],
            "recommendations": []
        }
        
        # 检测运行模式
        try:
            from platform_adapter.runtime_probe import RuntimeProbe
            env = RuntimeProbe.detect_environment()
            report["runtime_mode"] = env["runtime_mode"]
            report["platform"]["environment"] = env
        except Exception:
            report["platform"]["environment"] = {"error": "probe_failed"}
        
        # 获取能力状态
        try:
            from capabilities.registry import get_registry
            registry = get_registry()
            report["capabilities"] = registry.get_capabilities_report()
        except Exception:
            report["capabilities"] = {"error": "registry_not_available"}
        
        # 添加限制说明
        if report["runtime_mode"] == "skill_default":
            report["limitations"].extend([
                "No platform scheduling available",
                "Using SQLite for persistence",
                "Single-process execution"
            ])
            report["recommendations"].extend([
                "For enhanced features, deploy in Xiaoyi/HarmonyOS environment",
                "For production use, consider PostgreSQL + Redis setup"
            ])
        
        return report
    
    @staticmethod
    def format_markdown(report: Dict[str, Any]) -> str:
        """格式化为Markdown"""
        lines = [
            "# Capability Report",
            "",
            f"Generated: {report['generated_at']}",
            f"Runtime Mode: `{report['runtime_mode']}`",
            "",
            "## Capabilities",
            ""
        ]
        
        caps = report.get("capabilities", {})
        if "capabilities" in caps:
            for name, info in caps["capabilities"].items():
                status = info.get("status", "unknown")
                emoji = "✅" if status == "available" else "⚠️" if status == "degraded" else "❌"
                lines.append(f"- {emoji} **{name}**: {status}")
        
        if report.get("limitations"):
            lines.extend(["", "## Limitations", ""])
            for lim in report["limitations"]:
                lines.append(f"- {lim}")
        
        if report.get("recommendations"):
            lines.extend(["", "## Recommendations", ""])
            for rec in report["recommendations"]:
                lines.append(f"- {rec}")
        
        return "\n".join(lines)
