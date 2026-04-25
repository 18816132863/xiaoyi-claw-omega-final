"""导出能力性能报告"""

from typing import Dict, Any, Optional
from datetime import datetime
import json


def export_capability_performance_report(
    days: int = 7,
    output_format: str = "json",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    导出能力性能报告
    
    Args:
        days: 统计天数
        output_format: 输出格式 (json / markdown)
        output_path: 输出路径
        
    Returns:
        报告数据
    """
    from platform_adapter.invocation_ledger import InvocationLedger
    
    ledger = InvocationLedger()
    
    # 查询所有记录
    records = ledger.query_recent(limit=1000)
    
    # 按能力统计
    by_capability = {}
    error_codes = {}
    slow_invocations = []
    
    for r in records:
        capability = r.get("capability", "unknown")
        
        if capability not in by_capability:
            by_capability[capability] = {
                "total": 0,
                "success": 0,
                "failed": 0,
                "timeout": 0,
                "uncertain": 0,
                "latencies": []
            }
        
        by_capability[capability]["total"] += 1
        
        status = r.get("normalized_status", "unknown")
        if status == "completed":
            by_capability[capability]["success"] += 1
        elif status == "failed":
            by_capability[capability]["failed"] += 1
        elif status == "timeout":
            by_capability[capability]["timeout"] += 1
        elif status == "result_uncertain":
            by_capability[capability]["uncertain"] += 1
        
        # 统计错误码
        error_code = r.get("error_code")
        if error_code:
            error_codes[error_code] = error_codes.get(error_code, 0) + 1
        
        # 记录慢调用（假设有 duration_ms 字段）
        duration = r.get("duration_ms", 0)
        if duration > 1000:  # 超过 1 秒
            slow_invocations.append({
                "invocation_id": r.get("id"),
                "capability": capability,
                "duration_ms": duration,
                "status": status
            })
    
    # 计算成功率
    capability_stats = []
    for cap, stats in by_capability.items():
        success_rate = round(stats["success"] / stats["total"] * 100, 2) if stats["total"] > 0 else 0
        timeout_rate = round(stats["timeout"] / stats["total"] * 100, 2) if stats["total"] > 0 else 0
        
        capability_stats.append({
            "capability": cap,
            "total": stats["total"],
            "success": stats["success"],
            "failed": stats["failed"],
            "timeout": stats["timeout"],
            "uncertain": stats["uncertain"],
            "success_rate": success_rate,
            "timeout_rate": timeout_rate
        })
    
    # 排序
    capability_stats.sort(key=lambda x: x["total"], reverse=True)
    
    # Top 错误码
    top_errors = sorted(error_codes.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Top 慢调用
    slow_invocations.sort(key=lambda x: x.get("duration_ms", 0), reverse=True)
    top_slow = slow_invocations[:10]
    
    # 构建报告
    report = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "total_invocations": len(records),
        "by_capability": capability_stats,
        "top_error_codes": [{"code": code, "count": count} for code, count in top_errors],
        "top_slow_invocations": top_slow,
        "summary": {
            "total_capabilities": len(by_capability),
            "avg_success_rate": round(sum(s["success_rate"] for s in capability_stats) / len(capability_stats), 2) if capability_stats else 0,
            "avg_timeout_rate": round(sum(s["timeout_rate"] for s in capability_stats) / len(capability_stats), 2) if capability_stats else 0
        }
    }
    
    # 输出
    if output_path:
        with open(output_path, "w") as f:
            if output_format == "json":
                json.dump(report, f, indent=2, ensure_ascii=False)
            else:
                f.write(_format_markdown(report))
    
    return report


def _format_markdown(report: Dict[str, Any]) -> str:
    """格式化为 Markdown"""
    lines = [
        "# 能力性能报告",
        "",
        f"生成时间: {report['generated_at']}",
        f"统计周期: {report['period_days']} 天",
        f"总调用数: {report['total_invocations']}",
        "",
        "## 按能力统计",
        "",
        "| 能力 | 总数 | 成功 | 失败 | 超时 | 成功率 | 超时率 |",
        "|------|------|------|------|------|--------|--------|"
    ]
    
    for cap in report["by_capability"]:
        lines.append(
            f"| {cap['capability']} | {cap['total']} | {cap['success']} | {cap['failed']} | {cap['timeout']} | {cap['success_rate']}% | {cap['timeout_rate']}% |"
        )
    
    lines.extend([
        "",
        "## Top 错误码",
        "",
        "| 错误码 | 出现次数 |",
        "|--------|----------|"
    ])
    
    for err in report["top_error_codes"]:
        lines.append(f"| {err['code']} | {err['count']} |")
    
    lines.extend([
        "",
        "## Top 慢调用",
        "",
        "| 调用ID | 能力 | 耗时(ms) | 状态 |",
        "|--------|------|----------|------|"
    ])
    
    for slow in report["top_slow_invocations"]:
        lines.append(f"| {slow['invocation_id']} | {slow['capability']} | {slow['duration_ms']} | {slow['status']} |")
    
    return "\n".join(lines)


def run(**kwargs):
    """入口"""
    return export_capability_performance_report(**kwargs)


if __name__ == "__main__":
    import sys
    output_format = sys.argv[1] if len(sys.argv) > 1 else "json"
    report = export_capability_performance_report(output_format=output_format)
    print(json.dumps(report, indent=2, ensure_ascii=False))
