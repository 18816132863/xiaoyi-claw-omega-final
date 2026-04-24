"""
测试路由 Bootstrap
验证 route_request 能直接跑通
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_route_diagnostics_without_manual_register():
    """测试路由 diagnostics 不需要手工注册"""
    from skill_entry.input_router import route_request
    
    result = await route_request({
        "type": "diagnostics",
        "data": {}
    })
    
    assert result["success"] == True
    assert "overall_status" in result
    assert "checks" in result


@pytest.mark.asyncio
async def test_route_schedule_task():
    """测试路由 schedule_task"""
    from skill_entry.input_router import route_request
    
    result = await route_request({
        "type": "schedule_task",
        "data": {
            "message": "Test task",
            "user_id": "router_test"
        }
    })
    
    assert result["success"] == True
    assert "task_id" in result


@pytest.mark.asyncio
async def test_route_unknown_type():
    """测试路由未知类型"""
    from skill_entry.input_router import route_request
    
    result = await route_request({
        "type": "unknown_type",
        "data": {}
    })
    
    assert result["success"] == False
    assert result["error_code"] == "UNKNOWN_REQUEST_TYPE"


def test_get_router_auto_wires():
    """测试 get_router 自动连接能力"""
    from skill_entry.input_router import get_router
    
    router = get_router()
    registered = router.get_registered_types()
    
    # 应该有多个已注册的类型
    assert len(registered) >= 5
    assert "schedule_task" in registered
    assert "diagnostics" in registered
