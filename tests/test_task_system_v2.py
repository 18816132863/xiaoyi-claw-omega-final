#!/usr/bin/env python3
"""
任务系统完整测试 V2.0.0

测试内容：
1. once 定时任务创建和执行
2. 失败重试
3. pause/resume
4. interrupt/resume
5. 状态查询
6. 工具调用记录
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from infrastructure.task_manager import get_task_manager
from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
from domain.tasks import TaskStatus


async def test_once_task():
    """测试 1: once 定时任务"""
    print("\n" + "=" * 60)
    print("测试 1: once 定时任务创建和执行")
    print("=" * 60)
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建任务
    result = await tm.create_scheduled_message(
        user_id="test_user",
        message="这是一条 once 定时任务测试消息",
        run_at=(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
        title="🧪 Once 测试"
    )
    
    task_id = result.get("task_id")
    print(f"创建任务: {task_id}")
    print(f"状态: {result.get('status')}")
    
    # 入队并执行
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    result = await tm.execute_task(task_id)
    
    print(f"执行结果: {result}")
    
    # 查询状态
    task = await tm.get_task(task_id)
    print(f"最终状态: {task.status.value}")
    
    # 查询事件
    events = await tm.get_task_events(task_id)
    print(f"事件数量: {len(events)}")
    
    for event in events:
        print(f"  - {event['event_type']}: {event['created_at']}")
    
    return task_id


async def test_retry():
    """测试 2: 失败重试"""
    print("\n" + "=" * 60)
    print("测试 2: 失败重试")
    print("=" * 60)
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建一个会失败的任务（使用不存在的工具）
    from domain.tasks import TaskSpec, StepSpec, TriggerMode
    
    spec = TaskSpec(
        task_type="test_retry",
        goal="测试重试",
        trigger_mode=TriggerMode.IMMEDIATE,
        inputs={"message": "测试"},
        steps=[
            StepSpec(
                step_index=1,
                step_name="fail_step",
                tool_name="nonexistent_tool",  # 不存在的工具
                input_mapping={}
            )
        ],
        required_tools=["nonexistent_tool"]
    )
    
    result = await tm.task_service.create_task(spec)
    task_id = result.get("task_id")
    
    print(f"创建任务: {task_id}")
    
    # 入队并执行
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    result = await tm.execute_task(task_id)
    
    print(f"第一次执行结果: {result}")
    
    # 查询状态
    task = await tm.get_task(task_id)
    print(f"状态: {task.status.value}")
    print(f"重试次数: {task.retry_policy.max_attempts}")
    
    return task_id


async def test_pause_resume():
    """测试 3: pause/resume"""
    print("\n" + "=" * 60)
    print("测试 3: pause/resume")
    print("=" * 60)
    
    tm = get_task_manager()
    repo = SQLiteTaskRepository()
    
    # 创建任务
    result = await tm.create_scheduled_message(
        user_id="test_user",
        message="pause/resume 测试",
        run_at=(datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
        title="🧪 Pause 测试"
    )
    
    task_id = result.get("task_id")
    print(f"创建任务: {task_id}")
    
    # 入队
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    
    # 暂停
    result = await tm.pause_task(task_id)
    print(f"暂停结果: {result}")
    
    # 查询状态
    task = await tm.get_task(task_id)
    print(f"暂停后状态: {task.status.value}")
    
    # 恢复
    result = await tm.resume_task(task_id)
    print(f"恢复结果: {result}")
    
    # 查询状态
    task = await tm.get_task(task_id)
    print(f"恢复后状态: {task.status.value}")
    
    return task_id


async def test_interrupt_resume():
    """测试 4: interrupt/resume"""
    print("\n" + "=" * 60)
    print("测试 4: interrupt/resume (LangGraph)")
    print("=" * 60)
    
    from infrastructure.langgraph import get_workflow
    
    workflow = get_workflow()
    
    # 创建任务
    tm = get_task_manager()
    result = await tm.create_scheduled_message(
        user_id="test_user",
        message="interrupt/resume 测试",
        run_at=(datetime.now() + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
        title="🧪 Interrupt 测试"
    )
    
    task_id = result.get("task_id")
    print(f"创建任务: {task_id}")
    
    # 中断
    workflow.interrupt(task_id)
    print("已中断")
    
    # 检查检查点
    checkpoint_file = Path(f"data/checkpoints/{task_id}.json")
    if checkpoint_file.exists():
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
        print(f"检查点状态: {checkpoint.get('status')}")
    
    # 恢复
    result = workflow.resume(task_id)
    print(f"恢复结果: {result}")
    
    return task_id


async def test_query():
    """测试 5: 状态查询"""
    print("\n" + "=" * 60)
    print("测试 5: 状态查询")
    print("=" * 60)
    
    tm = get_task_manager()
    
    # 列出所有任务
    tasks = await tm.list_tasks("test_user", limit=10)
    print(f"任务数量: {len(tasks)}")
    
    for task in tasks:
        print(f"  - {task.task_id[:8]}... | {task.task_type} | {task.status.value}")
    
    # 查询工具调用
    if tasks:
        task_id = tasks[0].task_id
        tool_calls = await tm.get_tool_calls(task_id)
        print(f"\n工具调用记录: {len(tool_calls)} 条")
        
        for call in tool_calls[:3]:
            print(f"  - {call.get('tool_name')}: {call.get('status')}")


async def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  任务系统完整测试 V2.0.0")
    print("=" * 60)
    print(f"  时间: {datetime.now().isoformat()}")
    print("=" * 60)
    
    # 测试 1: once 定时任务
    task_id_1 = await test_once_task()
    
    # 测试 2: 失败重试
    task_id_2 = await test_retry()
    
    # 测试 3: pause/resume
    task_id_3 = await test_pause_resume()
    
    # 测试 4: interrupt/resume
    task_id_4 = await test_interrupt_resume()
    
    # 测试 5: 状态查询
    await test_query()
    
    # 汇总
    print("\n" + "=" * 60)
    print("  测试汇总")
    print("=" * 60)
    print(f"  once 定时任务: {task_id_1}")
    print(f"  失败重试: {task_id_2}")
    print(f"  pause/resume: {task_id_3}")
    print(f"  interrupt/resume: {task_id_4}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
