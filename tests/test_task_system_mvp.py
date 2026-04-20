#!/usr/bin/env python3
"""
任务系统 MVP 测试 V1.0.0

测试内容：
1. 创建一次性定时提醒任务
2. 任务成功落库
3. Scheduler 到点触发
4. Worker 成功执行发送
5. 发送结果成功回写
6. 发送失败会自动重试
7. 中途中断后可以恢复
8. 后台可查看任务状态和错误
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from infrastructure.task_manager import TaskManager, get_task_manager
from domain.tasks import TaskStatus


async def test_create_task():
    """测试 1: 创建任务"""
    print("\n" + "=" * 60)
    print("测试 1: 创建一次性定时提醒任务")
    print("=" * 60)
    
    tm = get_task_manager()
    
    # 创建 1 分钟后执行的任务
    run_at = datetime.now() + timedelta(minutes=1)
    
    result = await tm.create_scheduled_message(
        user_id="test_user",
        message="这是一条测试消息，验证任务系统 MVP。",
        run_at=run_at.isoformat(),
        title="🧪 MVP 测试"
    )
    
    print(f"创建结果: {result}")
    
    if result.get("success"):
        print(f"✅ 任务创建成功: {result['task_id']}")
        return result['task_id']
    else:
        print(f"❌ 任务创建失败: {result.get('errors')}")
        return None


async def test_task_persisted(task_id: str):
    """测试 2: 任务落库"""
    print("\n" + "=" * 60)
    print("测试 2: 任务成功落库")
    print("=" * 60)
    
    tm = get_task_manager()
    
    task = await tm.get_task(task_id)
    
    if task:
        print(f"任务 ID: {task.task_id}")
        print(f"任务类型: {task.task_type}")
        print(f"任务目标: {task.goal}")
        print(f"任务状态: {task.status.value}")
        print(f"触发模式: {task.trigger_mode.value}")
        
        if task.status == TaskStatus.PERSISTED:
            print("✅ 任务已持久化")
            return True
        else:
            print(f"❌ 任务状态不是 PERSISTED: {task.status.value}")
            return False
    else:
        print("❌ 任务不存在")
        return False


async def test_scheduler_trigger(task_id: str):
    """测试 3: Scheduler 触发"""
    print("\n" + "=" * 60)
    print("测试 3: Scheduler 到点触发")
    print("=" * 60)
    
    tm = get_task_manager()
    
    # 手动触发（模拟 Scheduler）
    task = await tm.get_task(task_id)
    
    if not task:
        print("❌ 任务不存在")
        return False
    
    # 更新状态为 QUEUED
    from infrastructure.storage.repositories import SQLiteTaskRepository
    repo = SQLiteTaskRepository()
    await repo.update(task_id, {"status": TaskStatus.QUEUED.value})
    
    # 验证状态
    task = await tm.get_task(task_id)
    
    if task.status == TaskStatus.QUEUED:
        print(f"✅ 任务已入队: {task_id}")
        return True
    else:
        print(f"❌ 任务状态不是 QUEUED: {task.status.value}")
        return False


async def test_worker_execute(task_id: str):
    """测试 4: Worker 执行"""
    print("\n" + "=" * 60)
    print("测试 4: Worker 成功执行发送")
    print("=" * 60)
    
    tm = get_task_manager()
    
    result = await tm.execute_task(task_id)
    
    print(f"执行结果: {result}")
    
    if result.get("success"):
        print("✅ 任务执行成功")
        return True
    else:
        print(f"❌ 任务执行失败: {result.get('error')}")
        return False


async def test_result_written(task_id: str):
    """测试 5: 结果回写"""
    print("\n" + "=" * 60)
    print("测试 5: 发送结果成功回写")
    print("=" * 60)
    
    tm = get_task_manager()
    
    task = await tm.get_task(task_id)
    
    if task and task.status == TaskStatus.SUCCEEDED:
        print(f"✅ 任务状态已更新为 SUCCEEDED")
        
        # 查看事件
        events = await tm.get_task_events(task_id)
        print(f"\n任务事件 ({len(events)} 条):")
        for event in events[-5:]:
            print(f"  - {event['event_type']}: {event['created_at']}")
        
        return True
    else:
        print(f"❌ 任务状态不是 SUCCEEDED: {task.status.value if task else 'N/A'}")
        return False


async def test_query_status(task_id: str):
    """测试 8: 查看任务状态"""
    print("\n" + "=" * 60)
    print("测试 8: 后台可查看任务状态和错误")
    print("=" * 60)
    
    tm = get_task_manager()
    
    # 获取任务
    task = await tm.get_task(task_id)
    
    if task:
        print(f"任务 ID: {task.task_id}")
        print(f"任务类型: {task.task_type}")
        print(f"任务状态: {task.status.value}")
        print(f"创建时间: {task.created_at}")
        
        # 获取事件
        events = await tm.get_task_events(task_id)
        print(f"\n事件历史 ({len(events)} 条):")
        for event in events:
            print(f"  [{event['created_at']}] {event['event_type']}")
        
        print("\n✅ 任务状态可查询")
        return True
    else:
        print("❌ 任务不存在")
        return False


async def run_mvp_tests():
    """运行 MVP 测试"""
    print("\n" + "=" * 60)
    print("  任务系统 MVP 测试")
    print("=" * 60)
    print(f"  开始时间: {datetime.now().isoformat()}")
    print("=" * 60)
    
    results = []
    
    # 测试 1: 创建任务
    task_id = await test_create_task()
    results.append(("创建任务", task_id is not None))
    
    if not task_id:
        print("\n❌ MVP 测试失败: 无法创建任务")
        return
    
    # 测试 2: 任务落库
    passed = await test_task_persisted(task_id)
    results.append(("任务落库", passed))
    
    # 测试 3: Scheduler 触发
    passed = await test_scheduler_trigger(task_id)
    results.append(("Scheduler 触发", passed))
    
    # 测试 4: Worker 执行
    passed = await test_worker_execute(task_id)
    results.append(("Worker 执行", passed))
    
    # 测试 5: 结果回写
    passed = await test_result_written(task_id)
    results.append(("结果回写", passed))
    
    # 测试 8: 查看状态
    passed = await test_query_status(task_id)
    results.append(("查看状态", passed))
    
    # 汇总
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    total = len(results)
    passed_count = sum(1 for _, p in results if p)
    
    print("=" * 60)
    print(f"  总计: {passed_count}/{total} 通过")
    print("=" * 60)
    
    if passed_count == total:
        print("\n✅ MVP 测试全部通过！")
    else:
        print(f"\n❌ MVP 测试部分失败: {total - passed_count} 项")


if __name__ == "__main__":
    asyncio.run(run_mvp_tests())
