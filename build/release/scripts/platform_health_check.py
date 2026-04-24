#!/usr/bin/env python
"""
平台健康巡检脚本
输出平台调用的健康状况
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.invocation_ledger import (
    get_statistics,
    export_recent,
    export_failed_report,
    export_timeout_report,
    export_uncertain_report,
)
from platform_adapter.xiaoyi_adapter import XiaoyiAdapter


def get_24h_stats() -> dict:
    """获取 24 小时内的统计"""
    # 获取最近 24 小时的记录
    recent = export_recent(1000)
    
    # 过滤 24 小时内的记录
    now = datetime.now()
    cutoff = now - timedelta(hours=24)
    
    recent_24h = []
    for r in recent:
        created_at = r.get("created_at")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at)
                if dt > cutoff:
                    recent_24h.append(r)
            except:
                pass
    
    # 统计
    total = len(recent_24h)
    failed = sum(1 for r in recent_24h if r.get("normalized_status") == "failed")
    timeout = sum(1 for r in recent_24h if r.get("normalized_status") == "timeout")
    
    return {
        "total": total,
        "failed": failed,
        "timeout": timeout,
        "failed_rate": (failed / total * 100) if total > 0 else 0,
        "timeout_rate": (timeout / total * 100) if total > 0 else 0,
    }


def get_notification_auth_status() -> dict:
    """获取 NOTIFICATION 授权状态"""
    import asyncio
    
    adapter = XiaoyiAdapter()
    adapter._ensure_initialized_sync()
    
    cap = adapter._capabilities.get("NOTIFICATION")
    
    if cap and cap.available:
        return {
            "status": "configured",
            "message": "authCode 已配置",
        }
    else:
        return {
            "status": "not_configured",
            "message": "authCode 未配置或无效",
        }


def run_health_check() -> dict:
    """运行健康检查"""
    # 获取总体统计
    stats = get_statistics()
    
    # 获取 24 小时统计
    stats_24h = get_24h_stats()
    
    # 获取 NOTIFICATION 授权状态
    notification_auth = get_notification_auth_status()
    
    # 计算 unconfirmed uncertain
    uncertain_records = export_uncertain_report(1000)
    unconfirmed_uncertain = sum(1 for r in uncertain_records if not r.get("confirmed_status"))
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_invocations": stats["total"],
        "uncertain_count": stats["uncertain_count"],
        "unconfirmed_uncertain_count": unconfirmed_uncertain,
        "failed_rate_24h": stats_24h["failed_rate"],
        "timeout_rate_24h": stats_24h["timeout_rate"],
        "notification_auth_status": notification_auth["status"],
        "notification_auth_message": notification_auth["message"],
        "by_status": stats["by_status"],
    }


def format_health_report(report: dict) -> str:
    """格式化健康报告"""
    lines = [
        "=" * 60,
        "平台健康巡检报告",
        "=" * 60,
        f"时间: {report['timestamp']}",
        "",
        "📊 总体统计",
        "-" * 40,
        f"总调用数: {report['total_invocations']}",
        f"Uncertain 记录: {report['uncertain_count']}",
        f"未确认 Uncertain: {report['unconfirmed_uncertain_count']}",
        "",
        "📈 24 小时统计",
        "-" * 40,
        f"失败率: {report['failed_rate_24h']:.2f}%",
        f"超时率: {report['timeout_rate_24h']:.2f}%",
        "",
        "🔐 NOTIFICATION 授权状态",
        "-" * 40,
        f"状态: {report['notification_auth_status']}",
        f"说明: {report['notification_auth_message']}",
        "",
        "📋 状态分布",
        "-" * 40,
    ]
    
    for status, count in report["by_status"].items():
        pct = (count / report["total_invocations"] * 100) if report["total_invocations"] > 0 else 0
        lines.append(f"  {status}: {count} ({pct:.1f}%)")
    
    # 健康评估
    lines.extend([
        "",
        "🏥 健康评估",
        "-" * 40,
    ])
    
    issues = []
    
    if report["failed_rate_24h"] > 5:
        issues.append(f"⚠️ 24小时失败率过高: {report['failed_rate_24h']:.2f}%")
    
    if report["timeout_rate_24h"] > 5:
        issues.append(f"⚠️ 24小时超时率过高: {report['timeout_rate_24h']:.2f}%")
    
    if report["unconfirmed_uncertain_count"] > 10:
        issues.append(f"⚠️ 未确认 uncertain 记录过多: {report['unconfirmed_uncertain_count']}")
    
    if report["notification_auth_status"] != "configured":
        issues.append("⚠️ NOTIFICATION 未正确授权")
    
    if issues:
        lines.extend(issues)
    else:
        lines.append("✅ 所有指标正常")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    """主函数"""
    report = run_health_check()
    print(format_health_report(report))
    
    # 返回退出码
    # 如果有严重问题，返回 1
    if report["failed_rate_24h"] > 10 or report["timeout_rate_24h"] > 10:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
