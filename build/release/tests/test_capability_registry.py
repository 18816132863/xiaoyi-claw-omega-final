"""测试能力注册表"""
import pytest
from capabilities.registry import CapabilityRegistry, CapabilityStatus


def test_registry_creation():
    """测试注册表创建"""
    registry = CapabilityRegistry()
    assert registry is not None


def test_register_capability():
    """测试注册能力"""
    registry = CapabilityRegistry()
    
    async def dummy_handler(params):
        return {"success": True}
    
    registry.register(
        name="test_cap",
        description="Test capability",
        handler=dummy_handler
    )
    
    assert "test_cap" in registry.list_all()


@pytest.mark.asyncio
async def test_execute_capability():
    """测试执行能力"""
    registry = CapabilityRegistry()
    
    async def handler(params):
        return {"success": True, "data": params.get("value")}
    
    registry.register(
        name="test_exec",
        description="Test execution",
        handler=handler
    )
    
    result = await registry.execute("test_exec", {"value": 42})
    
    assert result["success"] == True
    assert result["data"] == 42


def test_get_capabilities_report():
    """测试能力报告"""
    registry = CapabilityRegistry()
    report = registry.get_capabilities_report()
    
    assert "total" in report
    assert "available" in report
    assert "degraded" in report
    assert "unavailable" in report
