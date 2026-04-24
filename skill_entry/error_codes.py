"""
Error Codes - 错误码定义
提供统一的错误码和异常处理
"""

from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass


class ErrorCategory(Enum):
    """错误类别"""
    INPUT = "INPUT"           # 输入错误
    BUSINESS = "BUSINESS"     # 业务错误
    SYSTEM = "SYSTEM"         # 系统错误
    PLATFORM = "PLATFORM"     # 平台错误
    NETWORK = "NETWORK"       # 网络错误
    TIMEOUT = "TIMEOUT"       # 超时错误
    PERMISSION = "PERMISSION" # 权限错误
    RESOURCE = "RESOURCE"     # 资源错误


@dataclass
class ErrorCode:
    """错误码定义"""
    code: str
    message: str
    category: ErrorCategory
    http_status: int = 400
    retryable: bool = False
    suggestions: list = None
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []


class ErrorCodes:
    """错误码集合"""
    
    # 输入错误 (1xxx)
    INVALID_INPUT = ErrorCode(
        code="E1001",
        message="Invalid input parameters",
        category=ErrorCategory.INPUT,
        http_status=400,
        suggestions=["Check input format", "Refer to API documentation"]
    )
    
    MISSING_REQUIRED_FIELD = ErrorCode(
        code="E1002",
        message="Missing required field",
        category=ErrorCategory.INPUT,
        http_status=400
    )
    
    INVALID_FORMAT = ErrorCode(
        code="E1003",
        message="Invalid format",
        category=ErrorCategory.INPUT,
        http_status=400
    )
    
    VALUE_OUT_OF_RANGE = ErrorCode(
        code="E1004",
        message="Value out of allowed range",
        category=ErrorCategory.INPUT,
        http_status=400
    )
    
    # 业务错误 (2xxx)
    TASK_NOT_FOUND = ErrorCode(
        code="E2001",
        message="Task not found",
        category=ErrorCategory.BUSINESS,
        http_status=404
    )
    
    TASK_ALREADY_COMPLETED = ErrorCode(
        code="E2002",
        message="Task already completed",
        category=ErrorCategory.BUSINESS,
        http_status=400
    )
    
    TASK_ALREADY_CANCELLED = ErrorCode(
        code="E2003",
        message="Task already cancelled",
        category=ErrorCategory.BUSINESS,
        http_status=400
    )
    
    INVALID_TASK_STATE = ErrorCode(
        code="E2004",
        message="Invalid task state for this operation",
        category=ErrorCategory.BUSINESS,
        http_status=400
    )
    
    DUPLICATE_TASK = ErrorCode(
        code="E2005",
        message="Duplicate task detected",
        category=ErrorCategory.BUSINESS,
        http_status=409
    )
    
    # 系统错误 (3xxx)
    INTERNAL_ERROR = ErrorCode(
        code="E3001",
        message="Internal system error",
        category=ErrorCategory.SYSTEM,
        http_status=500,
        retryable=True
    )
    
    CONFIGURATION_ERROR = ErrorCode(
        code="E3002",
        message="Configuration error",
        category=ErrorCategory.SYSTEM,
        http_status=500
    )
    
    STORAGE_ERROR = ErrorCode(
        code="E3003",
        message="Storage operation failed",
        category=ErrorCategory.SYSTEM,
        http_status=500,
        retryable=True
    )
    
    SERIALIZATION_ERROR = ErrorCode(
        code="E3004",
        message="Serialization/deserialization error",
        category=ErrorCategory.SYSTEM,
        http_status=500
    )
    
    # 平台错误 (4xxx)
    PLATFORM_UNAVAILABLE = ErrorCode(
        code="E4001",
        message="Platform service unavailable",
        category=ErrorCategory.PLATFORM,
        http_status=503,
        retryable=True,
        suggestions=["Try again later", "Check platform status"]
    )
    
    PLATFORM_ADAPTER_NOT_FOUND = ErrorCode(
        code="E4002",
        message="Platform adapter not found",
        category=ErrorCategory.PLATFORM,
        http_status=500
    )
    
    PLATFORM_CAPABILITY_NOT_SUPPORTED = ErrorCode(
        code="E4003",
        message="Platform capability not supported",
        category=ErrorCategory.PLATFORM,
        http_status=400,
        suggestions=["Use fallback method", "Check platform capabilities"]
    )
    
    PLATFORM_AUTH_FAILED = ErrorCode(
        code="E4004",
        message="Platform authentication failed",
        category=ErrorCategory.PLATFORM,
        http_status=401
    )
    
    # 网络错误 (5xxx)
    NETWORK_ERROR = ErrorCode(
        code="E5001",
        message="Network error",
        category=ErrorCategory.NETWORK,
        http_status=503,
        retryable=True
    )
    
    CONNECTION_REFUSED = ErrorCode(
        code="E5002",
        message="Connection refused",
        category=ErrorCategory.NETWORK,
        http_status=503,
        retryable=True
    )
    
    # 超时错误 (6xxx)
    OPERATION_TIMEOUT = ErrorCode(
        code="E6001",
        message="Operation timed out",
        category=ErrorCategory.TIMEOUT,
        http_status=504,
        retryable=True
    )
    
    TASK_TIMEOUT = ErrorCode(
        code="E6002",
        message="Task execution timed out",
        category=ErrorCategory.TIMEOUT,
        http_status=504,
        retryable=True
    )
    
    # 权限错误 (7xxx)
    PERMISSION_DENIED = ErrorCode(
        code="E7001",
        message="Permission denied",
        category=ErrorCategory.PERMISSION,
        http_status=403
    )
    
    AUTHENTICATION_REQUIRED = ErrorCode(
        code="E7002",
        message="Authentication required",
        category=ErrorCategory.PERMISSION,
        http_status=401
    )
    
    # 资源错误 (8xxx)
    RESOURCE_NOT_FOUND = ErrorCode(
        code="E8001",
        message="Resource not found",
        category=ErrorCategory.RESOURCE,
        http_status=404
    )
    
    RESOURCE_EXHAUSTED = ErrorCode(
        code="E8002",
        message="Resource exhausted",
        category=ErrorCategory.RESOURCE,
        http_status=429,
        retryable=True
    )
    
    QUOTA_EXCEEDED = ErrorCode(
        code="E8003",
        message="Quota exceeded",
        category=ErrorCategory.RESOURCE,
        http_status=429
    )
    
    # 错误码映射
    _CODE_MAP: Dict[str, ErrorCode] = {}
    
    @classmethod
    def get(cls, code: str) -> Optional[ErrorCode]:
        """根据错误码字符串获取ErrorCode对象"""
        if not cls._CODE_MAP:
            # 初始化映射
            for attr_name in dir(cls):
                attr = getattr(cls, attr_name)
                if isinstance(attr, ErrorCode):
                    cls._CODE_MAP[attr.code] = attr
        return cls._CODE_MAP.get(code)
    
    @classmethod
    def from_exception(cls, exc: Exception) -> ErrorCode:
        """根据异常类型推断错误码"""
        exc_type = type(exc).__name__
        
        mapping = {
            "ValueError": cls.INVALID_INPUT,
            "TypeError": cls.INVALID_INPUT,
            "KeyError": cls.MISSING_REQUIRED_FIELD,
            "TimeoutError": cls.OPERATION_TIMEOUT,
            "ConnectionError": cls.NETWORK_ERROR,
            "PermissionError": cls.PERMISSION_DENIED,
            "FileNotFoundError": cls.RESOURCE_NOT_FOUND,
        }
        
        return mapping.get(exc_type, cls.INTERNAL_ERROR)


class SkillError(Exception):
    """技能异常基类"""
    
    def __init__(
        self,
        error_code: ErrorCode,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None
    ):
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception
        super().__init__(error_code.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "code": self.error_code.code,
            "message": self.error_code.message,
            "category": self.error_code.category.value,
            "http_status": self.error_code.http_status,
            "retryable": self.error_code.retryable
        }
        
        if self.details:
            result["details"] = self.details
        
        if self.error_code.suggestions:
            result["suggestions"] = self.error_code.suggestions
        
        return result
    
    @classmethod
    def from_exception(cls, exc: Exception) -> "SkillError":
        """从普通异常创建SkillError"""
        error_code = ErrorCodes.from_exception(exc)
        return cls(error_code, original_exception=exc)
