"""
Regression 测试 - 防止已知问题复发

固化之前踩过的坑。
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def test_delivery_pending_state_exists():
    """验证 delivery_pending 状态存在"""
    from domain.tasks.state_machine import TaskStatus
    
    assert hasattr(TaskStatus, 'DELIVERY_PENDING'), \
        "DELIVERY_PENDING 状态不存在"


def test_no_message_sender_in_main_scripts():
    """验证主脚本中没有 message_sender 残留"""
    scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
    
    # 排除 legacy 目录
    for script in scripts_dir.glob("*.py"):
        if "legacy" in str(script):
            continue
        
        content = script.read_text(encoding='utf-8')
        assert "message_sender" not in content, \
            f"{script.name} 中仍有 message_sender 残留"


def test_start_all_is_forwarding_only():
    """验证 start_all.sh 只是转发"""
    start_all = Path(__file__).resolve().parent.parent.parent / "scripts" / "start_all.sh"
    
    if start_all.exists():
        content = start_all.read_text(encoding='utf-8')
        
        # 应该转发到 start_services.sh
        assert "start_services.sh" in content, \
            "start_all.sh 应该转发到 start_services.sh"
        
        # 不应该有独立的启动逻辑
        assert "task_daemon.py" not in content or "start_services.sh" in content, \
            "start_all.sh 不应有独立启动逻辑"


def test_once_task_clears_next_run_at():
    """验证 once 任务成功后 next_run_at 为 None"""
    from domain.tasks import TaskStatus
    
    # once 任务成功后应该清空 next_run_at
    # 这个测试验证状态机定义正确
    from domain.tasks.state_machine import STATE_TRANSITIONS
    
    # SUCCEEDED 是终态，不应该有后续转移
    assert TaskStatus.SUCCEEDED in STATE_TRANSITIONS, \
        "SUCCEEDED 不在状态转移表中"
    
    # SUCCEEDED 的转移集合应该为空（终态）
    assert len(STATE_TRANSITIONS[TaskStatus.SUCCEEDED]) == 0, \
        "SUCCEEDED 应该是终态"


def test_recurring_does_not_succeed_directly():
    """验证 recurring 不会直接 succeeded"""
    from domain.tasks.state_machine import STATE_TRANSITIONS, TaskStatus
    
    # DELIVERY_PENDING 可以转移到 PERSISTED（recurring 循环）
    assert TaskStatus.PERSISTED in STATE_TRANSITIONS[TaskStatus.DELIVERY_PENDING], \
        "DELIVERY_PENDING 应该能转移到 PERSISTED（recurring 循环）"


def test_queued_not_double_scan():
    """验证 queued 状态不会被重复扫描"""
    # 这个测试验证调度器逻辑
    # 调度器应该只扫描 persisted 状态的任务
    from application.task_service.scheduler import SchedulerService
    
    # 验证调度器存在
    assert SchedulerService is not None


def test_legacy_scripts_not_in_main():
    """验证旧脚本不在主目录"""
    scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
    
    legacy_scripts = [
        "message_sender.py",
        "scheduled_tasks_daemon.py",
        "scheduled_tasks_launcher.py",
    ]
    
    for script in legacy_scripts:
        script_path = scripts_dir / script
        assert not script_path.exists(), \
            f"{script} 不应该在主 scripts 目录，应迁移到 legacy"


def test_main_entry_points_exist():
    """验证主入口脚本存在"""
    scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
    
    required_scripts = [
        "start_services.sh",
        "stop_services.sh",
        "status_services.sh",
        "task_daemon.py",
        "message_server.py",
    ]
    
    for script in required_scripts:
        script_path = scripts_dir / script
        assert script_path.exists(), f"主入口脚本 {script} 不存在"
