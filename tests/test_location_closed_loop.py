"""测试定位能力"""

import pytest


def test_get_address_from_location():
    """测试逆地理编码"""
    from capabilities.get_location import get_address_from_location
    
    result = get_address_from_location(latitude=39.9, longitude=116.4)
    assert result["success"] == True
    assert result["latitude"] == 39.9
    assert result["longitude"] == 116.4


def test_get_location_history():
    """测试获取位置历史"""
    from capabilities.get_location import get_location_history
    
    result = get_location_history(limit=10)
    assert result["success"] == True
    assert "locations" in result
