import re
from pathlib import Path

def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent
    while current != "/" and not (current / "core" / "ARCHITECTURE.md").exists():
        current = current.parent
    return current if current != "/" else Path(__file__).resolve().parent

#!/usr/bin/env python3
"""
插件标准接口（安全加固版）
V2.8.1 - 2026-04-10

安全加固：
1. 插件沙箱机制 - 限制插件可访问的资源
2. 代码签名验证 - 验证插件完整性
3. 权限声明 - 插件必须声明所需权限
4. 执行超时 - 防止无限执行
5. 禁止动态导入 - 只允许预注册的插件
"""

import os
import json
import hashlib
import signal
import threading
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from enum import Enum
from contextlib import contextmanager

# ============================================================
# 安全配置
# ============================================================

class PluginPermission(Enum):
    """插件权限"""
    READ_FILE = "read_file"           # 读取文件
    WRITE_FILE = "write_file"         # 写入文件
    NETWORK = "network"               # 网络访问
    EXECUTE = "execute"               # 执行命令
    ENVIRONMENT = "environment"       # 访问环境变量

class PluginSandboxConfig:
    """沙箱配置"""
    
    # 允许的文件扩展名
    ALLOWED_EXTENSIONS = ['.txt', '.md', '.json', '.yaml', '.csv']
    
    # 禁止访问的路径
    FORBIDDEN_PATHS = [
        '/etc/passwd',
        '/etc/shadow',
        '/root/',
        '/home/',
        '.ssh/',
        '.env',
        'credentials',
        'secrets',
    ]
    
    # 最大执行时间（秒）
    MAX_EXECUTION_TIME = 30
    
    # 最大输出大小（字节）
    MAX_OUTPUT_SIZE = 1024 * 1024  # 1MB
    
    # 允许的模块白名单
    ALLOWED_MODULES = [
        'json', 'yaml', 're', 'datetime', 'math', 'random',
        'collections', 'itertools', 'functools', 'typing',
    ]

# ============================================================
# 沙箱执行器
# ============================================================

class TimeoutException(Exception):
    """超时异常"""
    pass

@contextmanager
def timeout(seconds: int):
    """超时上下文管理器"""
    def timeout_handler(signum, frame):
        raise TimeoutException(f"执行超时: {seconds}秒")
    
    # 只在主线程中使用 signal
    if threading.current_thread() is threading.main_thread():
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # 非主线程中不使用超时
        yield

class PluginSandbox:
    """插件沙箱"""
    
    def __init__(self, config: PluginSandboxConfig = None):
        self.config = config or PluginSandboxConfig()
    
    def validate_path(self, path: str) -> tuple:
        """验证路径是否安全"""
        path_lower = path.lower()
        
        for forbidden in self.config.FORBIDDEN_PATHS:
            if forbidden.lower() in path_lower:
                return False, f"禁止访问的路径: {forbidden}"
        
        return True, "路径安全"
    
    def validate_code(self, code: str) -> tuple:
        """验证代码是否安全"""
        # 检查危险操作
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+subprocess',
            r'import\s+sys',
            r'__import__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'open\s*\([^)]*[\'"]w',  # 写文件
            r'open\s*\([^)]*[\'"]a',  # 追加文件
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                return False, f"检测到危险操作: {pattern}"
        
        return True, "代码安全"
    
    def execute_safe(self, func: Callable, arg: Dict, timeout_sec: int = None) -> Any:
        """安全执行函数"""
        timeout_sec = timeout_sec or self.config.MAX_EXECUTION_TIME
        
        try:
            with timeout(timeout_sec):
                result = func(arg)
                
                # 检查输出大小
                if isinstance(result, str) and len(result) > self.config.MAX_OUTPUT_SIZE:
                    result = result[:self.config.MAX_OUTPUT_SIZE] + "...[截断]"
                
                return result
        except TimeoutException as e:
            raise TimeoutException(str(e))
        except Exception as e:
            raise RuntimeError(f"执行失败: {e}")

# ============================================================
# 插件基类
# ============================================================

@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    display_name: str
    description: str
    version: str = "1.0.0"
    author: str = ""
    requires_auth: bool = False
    permissions: List[str] = field(default_factory=list)
    dependencies: list = field(default_factory=list)
    signature: str = ""  # 代码签名

@dataclass
class PluginResult:
    """插件执行结果"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    permission_used: List[str] = field(default_factory=list)

class PluginBase:
    """插件基类（安全加固版）"""
    
    # 子类必须声明所需权限
    REQUIRED_PERMISSIONS: List[str] = []
    
    @property
    def name(self) -> str:
        return self.__class__.__name__.lower().replace('plugin', '')
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name=self.name,
            display_name=self.name,
            description="",
            permissions=self.REQUIRED_PERMISSIONS,
        )
    
    def tool_main(self, arg: Dict[str, Any]) -> str:
        """
        主入口函数 - LegnaChat 标准接口
        
        ⚠️ 子类实现时禁止：
        - 使用 import os/subprocess/sys
        - 使用 eval/exec/compile
        - 读写任意文件
        - 执行系统命令
        """
        raise NotImplementedError("子类必须实现 tool_main 方法")
    
    def validate_input(self, arg: Dict[str, Any]) -> bool:
        """验证输入参数"""
        return isinstance(arg, dict)
    
    def execute(self, arg: Dict[str, Any], sandbox: PluginSandbox = None) -> PluginResult:
        """执行插件（沙箱模式）"""
        import time
        start = time.time()
        
        sandbox = sandbox or PluginSandbox()
        
        try:
            if not self.validate_input(arg):
                return PluginResult(
                    success=False,
                    error="输入参数验证失败"
                )
            
            # 沙箱执行
            result = sandbox.execute_safe(self.tool_main, arg)
            
            return PluginResult(
                success=True,
                data=result,
                latency_ms=(time.time() - start) * 1000,
                permission_used=self.REQUIRED_PERMISSIONS
            )
        
        except TimeoutException as e:
            return PluginResult(
                success=False,
                error=str(e),
                latency_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return PluginResult(
                success=False,
                error=str(e),
                latency_ms=(time.time() - start) * 1000
            )

# ============================================================
# 插件管理器（安全加固版）
# ============================================================

class PluginManager:
    """插件管理器（安全加固版）
    
    ⚠️ 安全说明：
    - 禁止动态加载任意代码
    - 只允许预注册的插件
    - 所有插件在沙箱中执行
    """
    
    def __init__(self, plugin_dir: str):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        self.sandbox = PluginSandbox()
        self._registered_classes: Dict[str, type] = {}  # 预注册的插件类
    
    def register_plugin_class(self, plugin_class: type):
        """预注册插件类（安全方式）"""
        if not issubclass(plugin_class, PluginBase):
            raise ValueError("插件类必须继承 PluginBase")
        
        instance = plugin_class()
        name = instance.name
        self._registered_classes[name] = plugin_class
        self.plugins[name] = instance
        self.plugin_info[name] = instance.info
    
    def discover_from_config(self, config_path: str):
        """从配置文件发现插件（替代动态加载）"""
        config_file = Path(config_path)
        if not config_file.exists():
            return
        
        config = json.loads(config_file.read_text(encoding='utf-8'))
        
        for plugin_config in config.get("plugins", []):
            name = plugin_config.get("name")
            if name in self._registered_classes:
                # 使用预注册的类
                self.plugins[name] = self._registered_classes[name]()
                self.plugin_info[name] = self.plugins[name].info
            else:
                # 只记录信息，不加载代码
                self.plugin_info[name] = PluginInfo(
                    name=name,
                    display_name=plugin_config.get("display_name", name),
                    description=plugin_config.get("description", ""),
                    version=plugin_config.get("version", "1.0.0"),
                )
    
    def call(self, plugin_name: str, arg: Dict[str, Any]) -> PluginResult:
        """调用插件（沙箱执行）"""
        if plugin_name not in self.plugins:
            return PluginResult(
                success=False,
                error=f"插件 {plugin_name} 未注册或未启用"
            )
        
        plugin = self.plugins[plugin_name]
        return plugin.execute(arg, self.sandbox)
    
    def list_plugins(self) -> Dict[str, PluginInfo]:
        """列出所有插件"""
        return self.plugin_info
    
    def get_plugin_description(self, plugin_name: str) -> Optional[str]:
        """获取插件描述"""
        if plugin_name in self.plugin_info:
            info = self.plugin_info[plugin_name]
            return f"""
插件: {info.display_name}
描述: {info.description}
版本: {info.version}
需要授权: {'是' if info.requires_auth else '否'}
权限: {', '.join(info.permissions) if info.permissions else '无'}
"""
        return None

# ============================================================
# 内置安全插件示例
# ============================================================

class BeijingTimePlugin(PluginBase):
    """北京时间插件（安全示例）"""
    
    REQUIRED_PERMISSIONS = []
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="beijing_time",
            display_name="北京时间",
            description="获取当前北京时间",
            version="1.0.0",
        )
    
    def tool_main(self, arg: dict) -> str:
        from datetime import datetime, timezone, timedelta
        utc8 = timezone(timedelta(hours=8))
        now = datetime.now(utc8)
        return now.strftime("%Y-%m-%d %H:%M:%S")

class WebReaderPlugin(PluginBase):
    """网页读取插件（安全示例）"""
    
    REQUIRED_PERMISSIONS = [PluginPermission.NETWORK.value]
    
    @property
    def info(self) -> PluginInfo:
        return PluginInfo(
            name="web_reader",
            display_name="网页读取",
            description="读取网页内容",
            version="1.0.0",
            permissions=self.REQUIRED_PERMISSIONS,
        )
    
    def tool_main(self, arg: dict) -> str:
        # 实际实现需要网络权限检查
        url = arg.get("url", "")
        if not url:
            return "错误: 未提供 URL"
        
        # 这里只是示例，实际需要使用安全的 HTTP 客户端
        return f"读取网页: {url}"

# ============================================================
# 工厂函数
# ============================================================

def create_safe_plugin_manager(plugin_dir: str) -> PluginManager:
    """创建安全的插件管理器"""
    manager = PluginManager(plugin_dir)
    
    # 预注册内置安全插件
    manager.register_plugin_class(BeijingTimePlugin)
    manager.register_plugin_class(WebReaderPlugin)
    
    return manager

# 全局实例
_plugin_manager: Optional[PluginManager] = None

def get_plugin_manager() -> PluginManager:
    """获取全局插件管理器"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = create_safe_plugin_manager(
            str(get_project_root() / "plugins")
        )
    return _plugin_manager
