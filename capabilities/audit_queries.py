"""
审计查询能力
提供程序化接口查询 platform_invocations
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.invocation_ledger import (
    query_by_task_id,
    query_by_capability,
    query_by_status,
    export_recent,
    export_failed_report,
    export_timeout_report,
    export_uncertain_report,
    get_statistics,
    get_invocation_by_id,
    get_invocation_by_idempotency_key,
)


class AuditQueries:
    """审计查询能力"""
    
    @staticmethod
    def get_recent(n: int = 10) -> List[Dict[str, Any]]:
        """获取最近 N 条记录"""
        return export_recent(n)
    
    @staticmethod
    def get_by_task_id(task_id: str) -> List[Dict[str, Any]]:
        """按 task_id 查询"""
        return query_by_task_id(task_id)
    
    @staticmethod
    def get_by_capability(capability: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按 capability 查询"""
        return query_by_capability(capability, limit)
    
    @staticmethod
    def get_by_status(status: str, limit: int = 100) -> List[Dict[str, Any]]:
        """按状态查询"""
        return query_by_status(status, limit)
    
    @staticmethod
    def get_uncertain(limit: int = 100) -> List[Dict[str, Any]]:
        """获取 uncertain 记录"""
        return export_uncertain_report(limit)
    
    @staticmethod
    def get_failed(limit: int = 100) -> List[Dict[str, Any]]:
        """获取 failed 记录"""
        return export_failed_report(limit)
    
    @staticmethod
    def get_timeout(limit: int = 100) -> List[Dict[str, Any]]:
        """获取 timeout 记录"""
        return export_timeout_report(limit)
    
    @staticmethod
    def get_by_id(record_id: int) -> Optional[Dict[str, Any]]:
        """按 ID 查询"""
        return get_invocation_by_id(record_id)
    
    @staticmethod
    def get_by_idempotency_key(key: str) -> Optional[Dict[str, Any]]:
        """按幂等键查询"""
        return get_invocation_by_idempotency_key(key)
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """获取统计信息"""
        return get_statistics()
    
    @staticmethod
    def get_unconfirmed_uncertain(limit: int = 100) -> List[Dict[str, Any]]:
        """获取未确认的 uncertain 记录"""
        records = export_uncertain_report(limit)
        return [r for r in records if not r.get("confirmed_status")]
    
    @staticmethod
    def summarize_status(records: List[Dict[str, Any]]) -> Dict[str, int]:
        """汇总状态分布"""
        summary = {}
        for r in records:
            status = r.get("normalized_status", "unknown")
            summary[status] = summary.get(status, 0) + 1
        return summary


# 便捷函数
def query_recent(n: int = 10) -> List[Dict[str, Any]]:
    """查询最近 N 条记录"""
    return AuditQueries.get_recent(n)


def query_uncertain(limit: int = 100) -> List[Dict[str, Any]]:
    """查询 uncertain 记录"""
    return AuditQueries.get_uncertain(limit)


def query_failed(limit: int = 100) -> List[Dict[str, Any]]:
    """查询 failed 记录"""
    return AuditQueries.get_failed(limit)


def query_timeout(limit: int = 100) -> List[Dict[str, Any]]:
    """查询 timeout 记录"""
    return AuditQueries.get_timeout(limit)


def query_stats() -> Dict[str, Any]:
    """查询统计信息"""
    return AuditQueries.get_stats()
