"""
LoopGuard - 循环防护模块
防止任务执行陷入无限循环或重复输出

作者: 鸽子王 🐦
版本: V1.0.0
"""

import time
import hashlib
import json
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum


class LoopType(Enum):
    """循环类型"""
    OUTPUT_LOOP = "output_loop"      # 输出重复
    STATE_LOOP = "state_loop"        # 状态循环
    ACTION_LOOP = "action_loop"      # 动作循环
    CHECK_LOOP = "check_loop"        # 检查循环（本案例）


@dataclass
class LoopAlert:
    """循环告警"""
    loop_type: LoopType
    pattern: str
    repeat_count: int
    first_occurrence: float
    last_occurrence: float
    suggested_action: str
    context: dict = field(default_factory=dict)


class LoopGuard:
    """
    循环防护器
    
    核心功能：
    1. 输出重复检测 - 检测相同或相似输出的重复
    2. 状态循环检测 - 检测状态机的死循环
    3. 动作循环检测 - 检测重复执行相同动作
    4. 自动熔断 - 检测到循环时自动中断
    """
    
    def __init__(
        self,
        max_repeats: int = 3,           # 最大重复次数
        similarity_threshold: float = 0.85,  # 相似度阈值
        window_size: int = 10,          # 滑动窗口大小
        cooldown_seconds: float = 1.0,  # 冷却时间
        auto_break: bool = True,        # 自动熔断
    ):
        self.max_repeats = max_repeats
        self.similarity_threshold = similarity_threshold
        self.window_size = window_size
        self.cooldown_seconds = cooldown_seconds
        self.auto_break = auto_break
        
        # 历史记录
        self.output_history: deque = deque(maxlen=window_size)
        self.state_history: deque = deque(maxlen=window_size)
        self.action_history: deque = deque(maxlen=window_size)
        
        # 循环计数器
        self.loop_counters: dict[str, int] = {}
        
        # 告警回调
        self.alert_callbacks: list[Callable[[LoopAlert], None]] = []
        
        # 熔断状态
        self._tripped = False
        self._trip_reason: Optional[str] = None
        self._trip_time: Optional[float] = None
    
    def add_alert_callback(self, callback: Callable[[LoopAlert], None]):
        """添加告警回调"""
        self.alert_callbacks.append(callback)
    
    def _emit_alert(self, alert: LoopAlert):
        """发送告警"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"[LoopGuard] 告警回调失败: {e}")
    
    def _hash_content(self, content: str) -> str:
        """计算内容哈希"""
        # 标准化内容：去除空白、标点差异
        normalized = ''.join(c.lower() for c in content if c.isalnum())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简化版 Jaccard）"""
        # 分词
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def check_output(self, output: str) -> Optional[LoopAlert]:
        """
        检查输出是否重复
        
        Args:
            output: 待检查的输出内容
            
        Returns:
            如果检测到循环，返回 LoopAlert；否则返回 None
        """
        if self._tripped:
            return None
        
        current_time = time.time()
        output_hash = self._hash_content(output)
        
        # 检查完全重复
        repeat_count = 0
        for hist_hash, hist_time in self.output_history:
            if hist_hash == output_hash:
                repeat_count += 1
        
        # 检查相似重复
        for hist_output, hist_time in self.output_history:
            if isinstance(hist_output, str):
                similarity = self._calculate_similarity(output, hist_output)
                if similarity >= self.similarity_threshold:
                    repeat_count += 1
        
        # 记录历史
        self.output_history.append((output_hash, current_time))
        
        # 判断是否触发循环
        if repeat_count >= self.max_repeats:
            alert = LoopAlert(
                loop_type=LoopType.OUTPUT_LOOP,
                pattern=output[:100] + "..." if len(output) > 100 else output,
                repeat_count=repeat_count,
                first_occurrence=current_time - len(self.output_history),
                last_occurrence=current_time,
                suggested_action="终止当前任务，避免无限循环",
                context={"output_hash": output_hash}
            )
            
            self._emit_alert(alert)
            
            if self.auto_break:
                self._trip(alert.suggested_action)
            
            return alert
        
        return None
    
    def check_state(self, state: str, context: dict = None) -> Optional[LoopAlert]:
        """
        检查状态是否循环
        
        Args:
            state: 当前状态标识
            context: 状态上下文
            
        Returns:
            如果检测到循环，返回 LoopAlert；否则返回 None
        """
        if self._tripped:
            return None
        
        current_time = time.time()
        
        # 检查状态重复
        repeat_count = 0
        for hist_state, hist_time in self.state_history:
            if hist_state == state:
                repeat_count += 1
        
        # 记录历史
        self.state_history.append((state, current_time))
        
        # 判断是否触发循环
        if repeat_count >= self.max_repeats:
            alert = LoopAlert(
                loop_type=LoopType.STATE_LOOP,
                pattern=state,
                repeat_count=repeat_count,
                first_occurrence=current_time - len(self.state_history),
                last_occurrence=current_time,
                suggested_action="状态机陷入循环，检查状态转换逻辑",
                context=context or {}
            )
            
            self._emit_alert(alert)
            
            if self.auto_break:
                self._trip(alert.suggested_action)
            
            return alert
        
        return None
    
    def check_action(self, action: str, params: dict = None) -> Optional[LoopAlert]:
        """
        检查动作是否重复
        
        Args:
            action: 动作名称
            params: 动作参数
            
        Returns:
            如果检测到循环，返回 LoopAlert；否则返回 None
        """
        if self._tripped:
            return None
        
        current_time = time.time()
        action_key = f"{action}:{json.dumps(params, sort_keys=True) if params else ''}"
        action_hash = hashlib.md5(action_key.encode()).hexdigest()[:16]
        
        # 检查动作重复
        repeat_count = 0
        for hist_hash, hist_time in self.action_history:
            if hist_hash == action_hash:
                # 检查时间间隔
                if current_time - hist_time < self.cooldown_seconds * 10:
                    repeat_count += 1
        
        # 记录历史
        self.action_history.append((action_hash, current_time))
        
        # 判断是否触发循环
        if repeat_count >= self.max_repeats:
            alert = LoopAlert(
                loop_type=LoopType.ACTION_LOOP,
                pattern=action,
                repeat_count=repeat_count,
                first_occurrence=current_time - len(self.action_history),
                last_occurrence=current_time,
                suggested_action=f"动作 '{action}' 重复执行，检查执行逻辑",
                context={"params": params}
            )
            
            self._emit_alert(alert)
            
            if self.auto_break:
                self._trip(alert.suggested_action)
            
            return alert
        
        return None
    
    def _trip(self, reason: str):
        """触发熔断"""
        self._tripped = True
        self._trip_reason = reason
        self._trip_time = time.time()
        print(f"[LoopGuard] ⚠️ 熔断触发: {reason}")
    
    def reset(self):
        """重置熔断器"""
        self._tripped = False
        self._trip_reason = None
        self._trip_time = None
        self.output_history.clear()
        self.state_history.clear()
        self.action_history.clear()
        self.loop_counters.clear()
        print("[LoopGuard] ✅ 已重置")
    
    def is_tripped(self) -> bool:
        """检查是否已熔断"""
        return self._tripped
    
    def get_trip_info(self) -> Optional[dict]:
        """获取熔断信息"""
        if not self._tripped:
            return None
        return {
            "reason": self._trip_reason,
            "time": self._trip_time,
            "duration": time.time() - self._trip_time if self._trip_time else 0
        }


class FailureLoopGuard:
    """
    失败循环防护器
    
    防止任务失败后陷入无限重试循环
    
    典型场景：
    - 任务失败 → 重试 → 失败 → 重试 → ...（无限循环）
    - 错误信息重复输出
    - 相同错误反复出现
    """
    
    def __init__(
        self,
        max_retries: int = 3,              # 最大重试次数
        max_same_error: int = 2,           # 相同错误最大次数
        backoff_multiplier: float = 2.0,   # 退避倍数
        initial_cooldown: float = 5.0,     # 初始冷却时间（秒）
        max_cooldown: float = 300.0,       # 最大冷却时间（秒）
        auto_escalate: bool = True,        # 自动升级（超过阈值后停止重试）
    ):
        self.max_retries = max_retries
        self.max_same_error = max_same_error
        self.backoff_multiplier = backoff_multiplier
        self.initial_cooldown = initial_cooldown
        self.max_cooldown = max_cooldown
        self.auto_escalate = auto_escalate
        
        # 失败记录
        self._failure_history: dict[str, list[dict]] = {}  # task_id -> [{error, time, error_hash}]
        self._retry_counts: dict[str, int] = {}
        self._last_retry_time: dict[str, float] = {}
        self._current_cooldown: dict[str, float] = {}
        
        # 锁定状态（超过阈值后锁定）
        self._locked_tasks: set[str] = set()
        self._lock_reasons: dict[str, str] = {}
    
    def _hash_error(self, error: str | Exception) -> str:
        """计算错误哈希"""
        error_str = str(error)
        normalized = ''.join(c.lower() for c in error_str if c.isalnum())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def record_failure(self, task_id: str, error: str | Exception, context: dict = None) -> dict:
        """
        记录失败
        
        Returns:
            dict: {
                "can_retry": bool,           # 是否可以重试
                "retry_count": int,          # 当前重试次数
                "cooldown": float,           # 冷却时间
                "same_error_count": int,     # 相同错误次数
                "should_escalate": bool,     # 是否应该升级处理
                "is_locked": bool,           # 是否已锁定
                "suggestion": str,           # 建议操作
            }
        """
        current_time = time.time()
        error_hash = self._hash_error(error)
        error_str = str(error)
        
        # 初始化记录
        if task_id not in self._failure_history:
            self._failure_history[task_id] = []
            self._retry_counts[task_id] = 0
            self._current_cooldown[task_id] = self.initial_cooldown
        
        # 检查是否已锁定
        if task_id in self._locked_tasks:
            return {
                "can_retry": False,
                "retry_count": self._retry_counts[task_id],
                "cooldown": 0,
                "same_error_count": 0,
                "should_escalate": True,
                "is_locked": True,
                "suggestion": f"任务已锁定，原因: {self._lock_reasons.get(task_id, '未知')}",
            }
        
        # 记录失败
        self._failure_history[task_id].append({
            "error": error_str,
            "error_hash": error_hash,
            "time": current_time,
            "context": context,
        })
        
        # 统计相同错误次数
        same_error_count = sum(
            1 for f in self._failure_history[task_id]
            if f["error_hash"] == error_hash
        )
        
        # 增加重试计数
        self._retry_counts[task_id] += 1
        retry_count = self._retry_counts[task_id]
        
        # 计算冷却时间（指数退避）
        cooldown = min(
            self._current_cooldown[task_id] * (self.backoff_multiplier ** (retry_count - 1)),
            self.max_cooldown
        )
        self._current_cooldown[task_id] = cooldown
        
        # 判断是否应该升级/锁定
        should_escalate = False
        is_locked = False
        suggestion = ""
        
        # 条件1: 超过最大重试次数
        if retry_count >= self.max_retries:
            should_escalate = True
            suggestion = f"重试次数已达上限 ({retry_count}/{self.max_retries})，建议人工介入"
            
            if self.auto_escalate:
                is_locked = True
                self._lock_task(task_id, f"重试次数超限 ({retry_count}次)")
        
        # 条件2: 相同错误重复出现
        if same_error_count >= self.max_same_error:
            should_escalate = True
            suggestion = f"相同错误重复 {same_error_count} 次，问题可能无法自动修复"
            
            if self.auto_escalate:
                is_locked = True
                self._lock_task(task_id, f"相同错误重复 {same_error_count} 次")
        
        # 条件3: 短时间内频繁失败（5分钟内失败超过5次）
        recent_failures = [
            f for f in self._failure_history[task_id]
            if current_time - f["time"] < 300
        ]
        if len(recent_failures) >= 5:
            should_escalate = True
            suggestion = "短时间内频繁失败，可能存在系统性问题"
            
            if self.auto_escalate:
                is_locked = True
                self._lock_task(task_id, "短时间内频繁失败")
        
        # 判断是否可以重试
        can_retry = not is_locked and retry_count < self.max_retries
        
        return {
            "can_retry": can_retry,
            "retry_count": retry_count,
            "cooldown": cooldown if can_retry else 0,
            "same_error_count": same_error_count,
            "should_escalate": should_escalate,
            "is_locked": is_locked,
            "suggestion": suggestion,
        }
    
    def _lock_task(self, task_id: str, reason: str):
        """锁定任务"""
        self._locked_tasks.add(task_id)
        self._lock_reasons[task_id] = reason
        print(f"[FailureLoopGuard] 🔒 任务 {task_id} 已锁定: {reason}")
    
    def can_retry(self, task_id: str) -> bool:
        """检查是否可以重试"""
        if task_id in self._locked_tasks:
            return False
        
        retry_count = self._retry_counts.get(task_id, 0)
        if retry_count >= self.max_retries:
            return False
        
        # 检查冷却时间
        last_time = self._last_retry_time.get(task_id, 0)
        cooldown = self._current_cooldown.get(task_id, self.initial_cooldown)
        
        if time.time() - last_time < cooldown:
            return False
        
        return True
    
    def get_cooldown_remaining(self, task_id: str) -> float:
        """获取剩余冷却时间"""
        last_time = self._last_retry_time.get(task_id, 0)
        cooldown = self._current_cooldown.get(task_id, self.initial_cooldown)
        remaining = cooldown - (time.time() - last_time)
        return max(0, remaining)
    
    def mark_retry_attempt(self, task_id: str):
        """标记重试尝试"""
        self._last_retry_time[task_id] = time.time()
    
    def unlock_task(self, task_id: str) -> bool:
        """解锁任务（人工干预后）"""
        if task_id in self._locked_tasks:
            self._locked_tasks.discard(task_id)
            self._lock_reasons.pop(task_id, None)
            # 重置计数
            self._failure_history.pop(task_id, None)
            self._retry_counts.pop(task_id, None)
            self._current_cooldown.pop(task_id, None)
            print(f"[FailureLoopGuard] 🔓 任务 {task_id} 已解锁")
            return True
        return False
    
    def get_failure_summary(self, task_id: str) -> Optional[dict]:
        """获取失败摘要"""
        if task_id not in self._failure_history:
            return None
        
        failures = self._failure_history[task_id]
        if not failures:
            return None
        
        # 统计错误类型
        error_counts: dict[str, int] = {}
        for f in failures:
            error_counts[f["error_hash"]] = error_counts.get(f["error_hash"], 0) + 1
        
        # 找出最常见的错误
        most_common_hash = max(error_counts, key=error_counts.get)
        most_common_error = next(
            f["error"] for f in failures if f["error_hash"] == most_common_hash
        )
        
        return {
            "total_failures": len(failures),
            "unique_errors": len(error_counts),
            "most_common_error": most_common_error[:200],
            "most_common_count": error_counts[most_common_hash],
            "first_failure_time": failures[0]["time"],
            "last_failure_time": failures[-1]["time"],
            "is_locked": task_id in self._locked_tasks,
            "lock_reason": self._lock_reasons.get(task_id),
        }
    
    def reset(self, task_id: str = None):
        """重置"""
        if task_id:
            self._locked_tasks.discard(task_id)
            self._lock_reasons.pop(task_id, None)
            self._failure_history.pop(task_id, None)
            self._retry_counts.pop(task_id, None)
            self._current_cooldown.pop(task_id, None)
            self._last_retry_time.pop(task_id, None)
        else:
            self._locked_tasks.clear()
            self._lock_reasons.clear()
            self._failure_history.clear()
            self._retry_counts.clear()
            self._current_cooldown.clear()
            self._last_retry_time.clear()
        print("[FailureLoopGuard] ✅ 已重置")


class TaskCompletionGuard:
    """
    任务完成防护器
    
    专门防止"任务已完成"后继续执行的问题（本案例）
    """
    
    def __init__(self):
        self._completed_tasks: set[str] = set()
        self._task_outputs: dict[str, list[str]] = {}
        self._max_outputs_per_task = 5
    
    def mark_completed(self, task_id: str, final_output: str = None):
        """标记任务完成"""
        self._completed_tasks.add(task_id)
        if final_output:
            self._task_outputs[task_id] = [final_output]
    
    def is_completed(self, task_id: str) -> bool:
        """检查任务是否已完成"""
        return task_id in self._completed_tasks
    
    def check_and_record_output(self, task_id: str, output: str) -> bool:
        """
        检查并记录输出
        
        Returns:
            True: 允许输出
            False: 应该阻止输出（任务已完成或输出重复）
        """
        # 任务已完成，阻止后续输出
        if task_id in self._completed_tasks:
            print(f"[TaskCompletionGuard] ⚠️ 任务 {task_id} 已完成，阻止后续输出")
            return False
        
        # 检查输出重复
        if task_id in self._task_outputs:
            outputs = self._task_outputs[task_id]
            if output in outputs:
                print(f"[TaskCompletionGuard] ⚠️ 输出重复，阻止")
                return False
            
            outputs.append(output)
            if len(outputs) > self._max_outputs_per_task:
                print(f"[TaskCompletionGuard] ⚠️ 输出次数超限，可能存在循环")
                return False
        else:
            self._task_outputs[task_id] = [output]
        
        return True
    
    def reset(self, task_id: str = None):
        """重置"""
        if task_id:
            self._completed_tasks.discard(task_id)
            self._task_outputs.pop(task_id, None)
        else:
            self._completed_tasks.clear()
            self._task_outputs.clear()


# 装饰器：自动循环防护
def loop_protected(max_repeats: int = 3):
    """
    循环防护装饰器
    
    用法：
        @loop_protected(max_repeats=3)
        def my_function():
            ...
    """
    def decorator(func: Callable) -> Callable:
        guard = LoopGuard(max_repeats=max_repeats)
        
        def wrapper(*args, **kwargs):
            if guard.is_tripped():
                print(f"[loop_protected] 函数 {func.__name__} 已被熔断")
                return None
            
            result = func(*args, **kwargs)
            
            if isinstance(result, str):
                alert = guard.check_output(result)
                if alert:
                    return f"[循环检测] {alert.suggested_action}"
            
            return result
        
        return wrapper
    return decorator


# 全局实例（单例模式）
_global_loop_guard: Optional[LoopGuard] = None
_global_task_guard: Optional[TaskCompletionGuard] = None
_global_failure_guard: Optional[FailureLoopGuard] = None


def get_loop_guard() -> LoopGuard:
    """获取全局循环防护器"""
    global _global_loop_guard
    if _global_loop_guard is None:
        _global_loop_guard = LoopGuard()
    return _global_loop_guard


def get_task_guard() -> TaskCompletionGuard:
    """获取全局任务完成防护器"""
    global _global_task_guard
    if _global_task_guard is None:
        _global_task_guard = TaskCompletionGuard()
    return _global_task_guard


def get_failure_guard() -> FailureLoopGuard:
    """获取全局失败循环防护器"""
    global _global_failure_guard
    if _global_failure_guard is None:
        _global_failure_guard = FailureLoopGuard()
    return _global_failure_guard


if __name__ == "__main__":
    # 测试用例
    print("=" * 50)
    print("=== LoopGuard 测试 ===")
    print("=" * 50 + "\n")
    
    guard = LoopGuard(max_repeats=3, auto_break=True)
    
    # 添加告警回调
    def on_alert(alert: LoopAlert):
        print(f"🚨 告警: {alert.loop_type.value} - {alert.suggested_action}")
    
    guard.add_alert_callback(on_alert)
    
    # 模拟重复输出
    test_outputs = [
        "已经安装了！让我看看内容：",
        "已经安装了！让我看看内容：",
        "已经安装了！让我看看内容：",
        "已经安装了！让我看看内容：",  # 第4次应该触发
    ]
    
    for i, output in enumerate(test_outputs):
        print(f"\n[输出 {i+1}] {output}")
        alert = guard.check_output(output)
        if alert:
            print(f"⚠️ 检测到循环！")
            break
    
    print("\n" + "=" * 50)
    print("=== TaskCompletionGuard 测试 ===")
    print("=" * 50 + "\n")
    
    task_guard = TaskCompletionGuard()
    task_id = "install_skill_xxx"
    
    # 模拟任务完成
    task_guard.mark_completed(task_id, "安装完成！")
    print(f"任务 {task_id} 已标记完成")
    
    # 尝试继续输出
    allowed = task_guard.check_and_record_output(task_id, "让我再检查一下...")
    print(f"后续输出被允许: {allowed}")  # 应该是 False
    
    print("\n" + "=" * 50)
    print("=== FailureLoopGuard 测试 ===")
    print("=" * 50 + "\n")
    
    failure_guard = FailureLoopGuard(max_retries=3, max_same_error=2, auto_escalate=True)
    task_id = "fetch_data_api"
    
    # 模拟失败重试循环
    errors = [
        "ConnectionError: Failed to connect to server",
        "ConnectionError: Failed to connect to server",  # 相同错误第2次
        "ConnectionError: Failed to connect to server",  # 相同错误第3次 → 锁定
        "TimeoutError: Request timed out",
    ]
    
    for i, error in enumerate(errors):
        print(f"\n[失败 {i+1}] {error[:50]}...")
        result = failure_guard.record_failure(task_id, error)
        print(f"  重试次数: {result['retry_count']}")
        print(f"  相同错误次数: {result['same_error_count']}")
        print(f"  可以重试: {result['can_retry']}")
        print(f"  冷却时间: {result['cooldown']:.1f}s")
        print(f"  已锁定: {result['is_locked']}")
        if result['suggestion']:
            print(f"  💡 建议: {result['suggestion']}")
        
        if result['is_locked']:
            print(f"\n  🔒 任务已锁定，停止重试循环！")
            break
    
    # 查看失败摘要
    print("\n--- 失败摘要 ---")
    summary = failure_guard.get_failure_summary(task_id)
    if summary:
        print(f"总失败次数: {summary['total_failures']}")
        print(f"唯一错误数: {summary['unique_errors']}")
        print(f"最常见错误: {summary['most_common_error'][:50]}...")
        print(f"出现次数: {summary['most_common_count']}")
        print(f"锁定状态: {summary['is_locked']}")
        print(f"锁定原因: {summary['lock_reason']}")
    
    # 解锁后重试
    print("\n--- 解锁任务 ---")
    failure_guard.unlock_task(task_id)
    print(f"任务 {task_id} 已解锁，可以重新尝试")
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成")
    print("=" * 50)
