"""
测试兼容性 Shim
验证旧路径 shim 只做导出，不含真实实现
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_infrastructure_config_is_shim():
    """测试 infrastructure/config 是 shim"""
    infra_config_path = project_root / "infrastructure" / "config"
    
    if not infra_config_path.exists():
        return  # 目录不存在，跳过
    
    # 检查是否有真实资源文件
    allowed_files = {"__init__.py", "README_DEPRECATED.md", "__pycache__"}
    real_files = []
    
    for f in infra_config_path.iterdir():
        if f.name not in allowed_files:
            real_files.append(f.name)
    
    assert len(real_files) == 0, f"infrastructure/config/ 包含真实文件: {real_files}"
    
    # 检查 __init__.py 是否是 shim
    init_file = infra_config_path / "__init__.py"
    if init_file.exists():
        content = init_file.read_text()
        # shim 应该有 DEPRECATED 标记和 from config 导入
        assert "DEPRECATED" in content or "from config" in content, \
            "infrastructure/config/__init__.py 应该是 shim，标记为 DEPRECATED"


def test_execution_workflows_is_shim():
    """测试 execution/workflows 是 shim"""
    exec_workflows_path = project_root / "execution" / "workflows"
    
    if not exec_workflows_path.exists():
        return  # 目录不存在，跳过
    
    # 检查是否有真实资源文件
    allowed_files = {"__init__.py", "README_DEPRECATED.md", "__pycache__"}
    real_files = []
    
    for f in exec_workflows_path.iterdir():
        if f.name not in allowed_files:
            real_files.append(f.name)
    
    assert len(real_files) == 0, f"execution/workflows/ 包含真实文件: {real_files}"


def test_execution_collaboration_is_shim():
    """测试 execution/collaboration 是 shim"""
    exec_collab_path = project_root / "execution" / "collaboration"
    
    if not exec_collab_path.exists():
        return  # 目录不存在，跳过
    
    # 检查是否有真实资源文件
    allowed_files = {"__init__.py", "README_DEPRECATED.md", "__pycache__"}
    real_files = []
    
    for f in exec_collab_path.iterdir():
        if f.name not in allowed_files:
            real_files.append(f.name)
    
    assert len(real_files) == 0, f"execution/collaboration/ 包含真实文件: {real_files}"


def test_domain_tasks_exports_from_specs():
    """测试 domain/tasks 从 specs 导入"""
    from domain.tasks import TaskStatus, StepStatus, EventType
    
    # 验证这些是从 specs.py 导入的
    from domain.tasks.specs import TaskStatus as SpecsTaskStatus
    from domain.tasks.specs import StepStatus as SpecsStepStatus
    from domain.tasks.specs import EventType as SpecsEventType
    
    assert TaskStatus is SpecsTaskStatus
    assert StepStatus is SpecsStepStatus
    assert EventType is SpecsEventType


def test_capabilities_exports_from_registry():
    """测试 capabilities 从 registry 导入"""
    from capabilities import CapabilityRegistry, CapabilityStatus
    
    # 验证这些是从 registry.py 导入的
    from capabilities.registry import CapabilityRegistry as RegCapabilityRegistry
    from capabilities.registry import CapabilityStatus as RegCapabilityStatus
    
    assert CapabilityRegistry is RegCapabilityRegistry
    assert CapabilityStatus is RegCapabilityStatus


def test_platform_adapter_no_capability_status_conflict():
    """测试 platform_adapter 没有 CapabilityStatus 冲突"""
    from platform_adapter.base import PlatformCapabilityState
    
    # 验证 PlatformCapabilityState 存在
    assert PlatformCapabilityState is not None
    
    # 验证 capabilities.registry.CapabilityStatus 是不同的类
    from capabilities.registry import CapabilityStatus
    assert CapabilityStatus is not PlatformCapabilityState


if __name__ == "__main__":
    test_infrastructure_config_is_shim()
    test_execution_workflows_is_shim()
    test_execution_collaboration_is_shim()
    test_domain_tasks_exports_from_specs()
    test_capabilities_exports_from_registry()
    test_platform_adapter_no_capability_status_conflict()
    print("✅ 所有兼容性 shim 测试通过")
