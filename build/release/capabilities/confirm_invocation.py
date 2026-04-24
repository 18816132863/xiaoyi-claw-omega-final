"""
手动确认能力
提供程序化接口确认 platform_invocations
"""

from typing import Optional
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from platform_adapter.invocation_ledger import (
    confirm_invocation,
    get_invocation_by_id,
    get_statistics,
)


class ConfirmInvocation:
    """手动确认能力"""
    
    # 确认状态
    CONFIRMED_SUCCESS = "confirmed_success"
    CONFIRMED_FAILED = "confirmed_failed"
    CONFIRMED_DUPLICATE = "confirmed_duplicate"
    
    @staticmethod
    def confirm_success(record_id: int, note: Optional[str] = None) -> bool:
        """
        确认成功
        
        Args:
            record_id: 记录 ID
            note: 确认备注
        
        Returns:
            bool: 是否成功
        """
        return confirm_invocation(
            record_id=record_id,
            confirmed_status=ConfirmInvocation.CONFIRMED_SUCCESS,
            confirm_note=note or "用户确认操作已成功",
        )
    
    @staticmethod
    def confirm_failed(record_id: int, note: Optional[str] = None) -> bool:
        """
        确认失败
        
        Args:
            record_id: 记录 ID
            note: 确认备注
        
        Returns:
            bool: 是否成功
        """
        return confirm_invocation(
            record_id=record_id,
            confirmed_status=ConfirmInvocation.CONFIRMED_FAILED,
            confirm_note=note or "用户确认操作失败",
        )
    
    @staticmethod
    def confirm_duplicate(record_id: int, note: Optional[str] = None) -> bool:
        """
        确认重复
        
        Args:
            record_id: 记录 ID
            note: 确认备注
        
        Returns:
            bool: 是否成功
        """
        return confirm_invocation(
            record_id=record_id,
            confirmed_status=ConfirmInvocation.CONFIRMED_DUPLICATE,
            confirm_note=note or "确认为重复操作",
        )
    
    @staticmethod
    def get_record(record_id: int) -> Optional[dict]:
        """获取记录详情"""
        return get_invocation_by_id(record_id)
    
    @staticmethod
    def get_confirmation_stats() -> dict:
        """获取确认统计"""
        stats = get_statistics()
        return {
            "total": stats["total"],
            "uncertain_count": stats["uncertain_count"],
            "confirmed_count": stats["confirmed_count"],
            "unconfirmed_count": stats["uncertain_count"] - stats["confirmed_count"],
            "confirmation_rate": (
                stats["confirmed_count"] / stats["uncertain_count"] * 100
                if stats["uncertain_count"] > 0 else 100
            ),
        }


# 便捷函数
def confirm_success(record_id: int, note: Optional[str] = None) -> bool:
    """确认成功"""
    return ConfirmInvocation.confirm_success(record_id, note)


def confirm_failed(record_id: int, note: Optional[str] = None) -> bool:
    """确认失败"""
    return ConfirmInvocation.confirm_failed(record_id, note)


def confirm_duplicate(record_id: int, note: Optional[str] = None) -> bool:
    """确认重复"""
    return ConfirmInvocation.confirm_duplicate(record_id, note)
