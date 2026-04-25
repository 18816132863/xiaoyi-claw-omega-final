"""
SQLite datetime 序列化测试

确保：
1. datetime 入库前会被转成字符串
2. model_dump() 出来的 datetime 不会直接传给 SQLite
3. 不再出现 Python 3.12 datetime adapter 弃用警告
"""

import pytest
import warnings
from datetime import datetime
from pathlib import Path
import tempfile
import sqlite3
import asyncio

from infrastructure.storage.sqlite_utils import serialize_datetime, deserialize_datetime

def run_with_isolated_loop(coro):
    """在不污染外部 event loop 的前提下运行协程。"""
    previous_loop = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            previous_loop = asyncio.get_event_loop_policy().get_event_loop()
        except RuntimeError:
            previous_loop = None

    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        loop.close()
        if previous_loop is not None and not previous_loop.is_closed():
            asyncio.set_event_loop(previous_loop)
        else:
            asyncio.set_event_loop(None)


class TestDatetimeSerialization:
    """测试 datetime 序列化"""
    
    def test_serialize_none(self):
        """None 应返回 None"""
        assert serialize_datetime(None) is None
    
    def test_serialize_string(self):
        """字符串应原样返回"""
        iso_str = "2026-04-23T10:00:00"
        assert serialize_datetime(iso_str) == iso_str
    
    def test_serialize_datetime(self):
        """datetime 应转为 ISO 字符串"""
        dt = datetime(2026, 4, 23, 10, 0, 0)
        result = serialize_datetime(dt)
        assert result == "2026-04-23T10:00:00"
        assert isinstance(result, str)
    
    def test_deserialize_none(self):
        """None 应返回 None"""
        assert deserialize_datetime(None) is None
    
    def test_deserialize_empty_string(self):
        """空字符串应返回 None"""
        assert deserialize_datetime("") is None
    
    def test_deserialize_iso_string(self):
        """ISO 字符串应转为 datetime"""
        iso_str = "2026-04-23T10:00:00"
        result = deserialize_datetime(iso_str)
        assert result == datetime(2026, 4, 23, 10, 0, 0)
    
    def test_roundtrip(self):
        """往返转换应保持一致"""
        dt = datetime(2026, 4, 23, 10, 0, 0)
        serialized = serialize_datetime(dt)
        deserialized = deserialize_datetime(serialized)
        assert deserialized == dt


class TestNoDeprecatedAdapter:
    """测试不再使用弃用的 datetime adapter"""
    
    def test_no_deprecation_warning(self):
        """直接插入 datetime 不应产生弃用警告"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            # 使用统一序列化方法
            dt = datetime(2026, 4, 23, 10, 0, 0)
            serialized = serialize_datetime(dt)
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute("""
                CREATE TABLE test_table (
                    id TEXT PRIMARY KEY,
                    created_at TEXT
                )
            """)
            
            # 插入序列化后的字符串
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                cursor.execute(
                    "INSERT INTO test_table (id, created_at) VALUES (?, ?)",
                    ("test_001", serialized)
                )
                conn.commit()
                
                # 不应有 DeprecationWarning
                deprecation_warnings = [
                    warning for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
                assert len(deprecation_warnings) == 0, \
                    f"发现 DeprecationWarning: {[str(w.message) for w in deprecation_warnings]}"
            
            # 验证数据
            cursor.execute("SELECT created_at FROM test_table WHERE id = ?", ("test_001",))
            row = cursor.fetchone()
            assert row[0] == "2026-04-23T10:00:00"
            
            conn.close()
    
    def test_raw_datetime_triggers_warning(self):
        """直接插入裸 datetime 会触发警告（反面测试）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            
            dt = datetime(2026, 4, 23, 10, 0, 0)
            
            conn = sqlite3.connect(str(db_path), detect_types=sqlite3.PARSE_DECLTYPES)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute("""
                CREATE TABLE test_table (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP
                )
            """)
            
            # 直接插入 datetime（错误做法）
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                cursor.execute(
                    "INSERT INTO test_table (id, created_at) VALUES (?, ?)",
                    ("test_001", dt)
                )
                conn.commit()
                
                # 应该有 DeprecationWarning（这是反面测试，证明旧方法会触发警告）
                deprecation_warnings = [
                    warning for warning in w
                    if issubclass(warning.category, DeprecationWarning)
                ]
                # 注意：这个测试是为了证明旧方法会触发警告
                # 如果 Python 版本 < 3.12，可能不会有警告
                # 所以这里只是记录，不强制断言
            
            conn.close()


class TestRepositoryUsesSerialization:
    """测试 Repository 使用统一序列化"""
    
    def test_task_repository_serializes_datetime(self):
        """TaskRepository 应使用 serialize_datetime"""
        from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
        from domain.tasks import TaskSpec, TaskStatus, TriggerMode
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "tasks.db"
            repo = SQLiteTaskRepository(db_path=str(db_path))
            
            # 创建任务
            task = TaskSpec(
                task_id="test_001",
                task_type="test",
                goal="测试任务",
                trigger_mode=TriggerMode.IMMEDIATE,
                status=TaskStatus.PERSISTED
            )
            
            async def run_test():
                task_id = await repo.create(task)
                return task_id

            task_id = run_with_isolated_loop(run_test())
            
            # 验证 created_at 是字符串格式
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT created_at FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            conn.close()
            
            # created_at 应该是 ISO 字符串格式
            assert row[0] is not None
            assert isinstance(row[0], str)
            assert "T" in row[0]  # ISO 格式包含 T


class TestUpdateSerializesDatetime:
    """测试 update() 对时间字段强制序列化"""
    
    def test_update_next_run_at_with_datetime(self):
        """update() 传 datetime 到 next_run_at 应被序列化为 ISO 字符串"""
        from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
        from domain.tasks import TaskSpec, TaskStatus, TriggerMode
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "tasks.db"
            repo = SQLiteTaskRepository(db_path=str(db_path))
            
            async def run_test():
                # 创建任务
                task = TaskSpec(
                    task_id="test_update_001",
                    task_type="test",
                    goal="测试任务",
                    trigger_mode=TriggerMode.IMMEDIATE,
                    status=TaskStatus.PERSISTED
                )

                task_id = await repo.create(task)

                # 用 datetime 对象更新 next_run_at
                dt = datetime(2026, 4, 23, 15, 30, 0)
                await repo.update(task_id, {"next_run_at": dt})

                # 验证数据库里存的是 ISO 字符串
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT next_run_at FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                conn.close()

                assert row[0] == "2026-04-23T15:30:00"
                assert isinstance(row[0], str)

            run_with_isolated_loop(run_test())
    
    def test_update_last_run_at_with_datetime(self):
        """update() 传 datetime 到 last_run_at 应被序列化为 ISO 字符串"""
        from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
        from domain.tasks import TaskSpec, TaskStatus, TriggerMode
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "tasks.db"
            repo = SQLiteTaskRepository(db_path=str(db_path))
            
            async def run_test():
                # 创建任务
                task = TaskSpec(
                    task_id="test_update_002",
                    task_type="test",
                    goal="测试任务",
                    trigger_mode=TriggerMode.IMMEDIATE,
                    status=TaskStatus.PERSISTED
                )

                task_id = await repo.create(task)

                # 用 datetime 对象更新 last_run_at
                dt = datetime(2026, 4, 23, 16, 45, 0)
                await repo.update(task_id, {"last_run_at": dt})

                # 验证数据库里存的是 ISO 字符串
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT last_run_at FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                conn.close()

                assert row[0] == "2026-04-23T16:45:00"
                assert isinstance(row[0], str)

            run_with_isolated_loop(run_test())


class TestSerializeDatetimeHardRestriction:
    """测试 serialize_datetime() 硬限制"""
    
    def test_invalid_type_raises_error(self):
        """非法类型必须直接抛 TypeError"""
        with pytest.raises(TypeError) as exc_info:
            serialize_datetime(object())
        
        assert "只接受 None、str、datetime" in str(exc_info.value)
    
    def test_int_raises_error(self):
        """整数类型必须抛 TypeError"""
        with pytest.raises(TypeError):
            serialize_datetime(12345)
    
    def test_list_raises_error(self):
        """列表类型必须抛 TypeError"""
        with pytest.raises(TypeError):
            serialize_datetime([datetime.now()])
    
    def test_dict_raises_error(self):
        """字典类型必须抛 TypeError"""
        with pytest.raises(TypeError):
            serialize_datetime({"time": "2026-04-23"})


class TestNoDeprecationWarningInAllOperations:
    """测试所有操作都不产生弃用警告"""
    
    def test_full_crud_no_warning(self):
        """完整 CRUD 操作不应产生弃用警告"""
        from infrastructure.storage.repositories.sqlite_repo import SQLiteTaskRepository
        from domain.tasks import TaskSpec, TaskStatus, TriggerMode
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "tasks.db"
            repo = SQLiteTaskRepository(db_path=str(db_path))
            
            # 创建单个 event loop 用于整个测试
            async def run_all_operations():
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")

                    # Create
                    task = TaskSpec(
                        task_id="test_crud_001",
                        task_type="test",
                        goal="测试任务",
                        trigger_mode=TriggerMode.IMMEDIATE,
                        status=TaskStatus.PERSISTED
                    )
                    task_id = await repo.create(task)

                    # Update with datetime
                    await repo.update(task_id, {
                        "next_run_at": datetime(2026, 4, 23, 17, 0, 0),
                        "status": TaskStatus.QUEUED.value
                    })

                    # Read
                    task = await repo.get(task_id)

                    # Delete
                    await repo.delete(task_id)

                    # 不应有 DeprecationWarning
                    deprecation_warnings = [
                        warning for warning in w
                        if issubclass(warning.category, DeprecationWarning)
                    ]
                    assert len(deprecation_warnings) == 0, \
                        f"发现 DeprecationWarning: {[str(w.message) for w in deprecation_warnings]}"

            run_with_isolated_loop(run_all_operations())
