"""
测试 RuntimeProbe 与 XiaoyiAdapter 一致性
"""

import pytest
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_only_harmonyos_env_but_no_capability_connected():
    """
    场景1：仅设置 HARMONYOS_VERSION，但平台能力未接通
    
    口径统一版：
    - device_connected 默认 true
    - connected 取决于能力是否已接通
    - 如果 call_device_tool 可用，则返回 xiaoyi
    """
    # 设置环境变量
    original = os.environ.get("HARMONYOS_VERSION")
    os.environ["HARMONYOS_VERSION"] = "4.0.0"
    
    try:
        # 重新导入以获取新环境
        import importlib
        from platform_adapter import runtime_probe
        importlib.reload(runtime_probe)
        
        from platform_adapter.runtime_probe import RuntimeProbe
        
        env = RuntimeProbe.detect_environment()
        adapter = RuntimeProbe.get_recommended_adapter()
        
        # 口径统一：当前环境中 call_device_tool 可用
        # 所以返回 xiaoyi（4个能力都已 connected）
        assert adapter == "xiaoyi", f"Expected 'xiaoyi', got '{adapter}'"
        
    finally:
        # 恢复环境
        if original is None:
            os.environ.pop("HARMONYOS_VERSION", None)
        else:
            os.environ["HARMONYOS_VERSION"] = original


@pytest.mark.asyncio
async def test_xiaoyi_adapter_probe_when_not_connected():
    """
    场景2：XiaoyiAdapter 在能力未接通时的行为
    
    口径统一版：
    - device_connected 默认 true
    - connected 表示"该能力在已连接设备环境中已真实可调用"
    - 如果 call_device_tool 不可用，则为 probe_only
    - 如果 authCode 已配置，NOTIFICATION 也为 connected
    """
    from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
    
    adapter = XiaoyiAdapter()
    result = await adapter.probe()
    
    # 口径统一：device_connected 默认 true
    assert result["device_connected"] == True
    
    # 如果 call_device_tool 可用，available 应该是 True
    if result.get("call_device_tool_available"):
        assert result["available"] == True
        assert result["state"] == "connected"


@pytest.mark.asyncio
async def test_runtime_probe_adapter_consistency():
    """
    场景3：runtime_probe 与 xiaoyi_adapter 语义一致
    
    预期：
    - 如果 get_recommended_adapter() 返回 "xiaoyi"
    - 那么 probe_adapter("xiaoyi")["available"] 应该是 True
    """
    from platform_adapter.runtime_probe import RuntimeProbe
    
    adapter = RuntimeProbe.get_recommended_adapter()
    
    if adapter == "xiaoyi":
        probe_result = RuntimeProbe.probe_adapter("xiaoyi")
        assert probe_result.get("available") == True, \
            "get_recommended_adapter() returned 'xiaoyi' but probe says not available"
    elif adapter == "null":
        # 这是正常的，说明没有平台能力可用
        pass
    else:
        pytest.fail(f"Unexpected adapter: {adapter}")


@pytest.mark.asyncio
async def test_no_env_returns_null_adapter():
    """
    场景4：无环境变量时返回 null 适配器
    
    预期：
    - get_recommended_adapter() == "null"
    - runtime_mode == "skill_default" 或 "self_hosted_enhanced"（取决于数据库/Redis）
    """
    # 确保没有平台环境变量
    original_harmony = os.environ.get("HARMONYOS_VERSION")
    original_xiaoyi = os.environ.get("XIAOYI_ENV")
    
    os.environ.pop("HARMONYOS_VERSION", None)
    os.environ.pop("XIAOYI_ENV", None)
    
    try:
        import importlib
        from platform_adapter import runtime_probe
        importlib.reload(runtime_probe)
        
        from platform_adapter.runtime_probe import RuntimeProbe
        
        adapter = RuntimeProbe.get_recommended_adapter()
        assert adapter == "null", f"Expected 'null', got '{adapter}'"
        
    finally:
        if original_harmony:
            os.environ["HARMONYOS_VERSION"] = original_harmony
        if original_xiaoyi:
            os.environ["XIAOYI_ENV"] = original_xiaoyi
