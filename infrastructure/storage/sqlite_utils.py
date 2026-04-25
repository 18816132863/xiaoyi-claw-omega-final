"""
SQLite 工具函数

统一处理时间字段序列化，避免 Python 3.12 datetime adapter 弃用警告。

硬规范：
- SQLite 层禁止裸 datetime 直接入库
- 所有时间字段必须经过 serialize_datetime()
- 只接受 None、ISO 8601 字符串、datetime 对象
- 其他类型直接报错，不偷偷放行
"""

from datetime import datetime
from typing import Optional, Union


def serialize_datetime(value: Optional[Union[datetime, str]]) -> Optional[str]:
    """
    统一时间字段序列化方法（硬限制版）
    
    SQLite 层只接受：
    - None
    - ISO 8601 字符串
    - datetime 对象（会被转为 ISO 字符串）
    
    不接受其他任何类型，发现直接报错。
    
    Args:
        value: datetime 对象、ISO 字符串或 None
        
    Returns:
        ISO 8601 字符串或 None
        
    Raises:
        TypeError: 传入不支持类型时抛出
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    # 硬限制：其他类型直接报错，不偷偷放行
    raise TypeError(
        f"serialize_datetime() 只接受 None、str、datetime，"
        f"收到: {type(value).__name__} ({value!r})"
    )


def deserialize_datetime(value: Optional[str]) -> Optional[datetime]:
    """
    从 SQLite 读取时间字段
    
    Args:
        value: ISO 8601 字符串或 None
        
    Returns:
        datetime 对象或 None
    """
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            # 解析失败返回 None，但不报错
            return None
    return None


# 别名，方便使用
_serialize_dt = serialize_datetime
_deserialize_dt = deserialize_datetime
