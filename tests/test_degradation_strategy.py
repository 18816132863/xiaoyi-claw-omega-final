"""测试降级策略"""
import pytest
from platform_adapter.null_adapter import NullAdapter
from platform_adapter.base import PlatformCapability


@pytest.mark.asyncio
async def test_null_adapter_probe():
    """测试空适配器探测"""
    adapter = NullAdapter()
    result = await adapter.probe()
    
    assert result["adapter"] == "null"
    assert result["available"] == False


@pytest.mark.asyncio
async def test_null_adapter_invoke():
    """测试空适配器调用"""
    adapter = NullAdapter()
    result = await adapter.invoke(PlatformCapability.TASK_SCHEDULING, {})
    
    assert result["success"] == False
    assert result["fallback_available"] == True


@pytest.mark.asyncio
async def test_null_adapter_is_available():
    """测试空适配器可用性"""
    adapter = NullAdapter()
    available = await adapter.is_available()
    
    assert available == False
