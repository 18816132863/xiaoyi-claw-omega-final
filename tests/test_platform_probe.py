"""测试平台探测"""
import pytest
from platform_adapter.runtime_probe import RuntimeProbe


def test_detect_environment():
    """测试环境检测"""
    env = RuntimeProbe.detect_environment()
    
    assert "is_xiaoyi" in env
    assert "is_harmonyos" in env
    assert "is_web" in env
    assert "is_cli" in env
    assert "has_database" in env
    assert "has_redis" in env
    assert "has_docker" in env
    assert "runtime_mode" in env


def test_runtime_mode_values():
    """测试运行模式值"""
    env = RuntimeProbe.detect_environment()
    
    assert env["runtime_mode"] in [
        "skill_default",
        "platform_enhanced",
        "self_hosted_enhanced"
    ]


def test_get_recommended_adapter():
    """测试推荐适配器"""
    adapter = RuntimeProbe.get_recommended_adapter()
    
    assert adapter in ["xiaoyi", "harmonyos", "null"]
