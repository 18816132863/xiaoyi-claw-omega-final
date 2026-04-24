#!/usr/bin/env python3
"""
心跳执行器 V7.3.0

统一执行所有心跳任务，支持：
- 自动 Git 同步
- 永久守护器刷新
- Metrics 生成
- 架构巡检
- 规则引擎检查
- V7.3.0: 消息队列处理

使用方式：
1. 被 HEARTBEAT.md 心跳触发
2. 手动运行: python scripts/heartbeat_executor.py
3. 定时任务: cron / systemd timer
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent


class HeartbeatExecutor:
    """心跳执行器"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.results: List[Dict[str, Any]] = []
        self.start_time = datetime.now()
        
        # 心跳任务配置
        self.tasks = [
            {
                "id": "one_time_trigger",
                "name": "一次性定时任务",
                "command": [sys.executable, str(self.root / "scripts/one_time_trigger.py")],
                "timeout": 60,
                "priority": -2,  # 最高优先级
                "enabled": True
            },
            {
                "id": "task_daemon",
                "name": "任务守护进程检查",
                "command": [sys.executable, "-c", "import subprocess; subprocess.run(['pgrep', '-f', 'task_daemon.py'], check=False)"],
                "timeout": 10,
                "priority": -1,
                "enabled": True
            },
            {
                "id": "auto_trigger",
                "name": "自动触发器",
                "command": [sys.executable, str(self.root / "scripts/auto_trigger.py")],
                "timeout": 120,
                "priority": 0,
                "enabled": True
            },
            {
                "id": "session_end_detector",
                "name": "会话结束检测",
                "command": [sys.executable, str(self.root / "scripts/session_end_detector.py")],
                "timeout": 180,
                "priority": 1,
                "enabled": True
            },
            {
                "id": "permanent_keeper",
                "name": "永久守护器刷新",
                "command": [sys.executable, str(self.root / "scripts/permanent_keeper.py"), "refresh"],
                "timeout": 60,
                "priority": 2,
                "enabled": True
            },
            {
                "id": "auto_git",
                "name": "自动 Git 同步",
                "command": [sys.executable, str(self.root / "infrastructure/auto_git.py"), "sync", "心跳自动提交"],
                "timeout": 60,
                "priority": 3,
                "enabled": False  # 禁用：由会话结束检测器触发
            },
            {
                "id": "auto_backup",
                "name": "自动备份上传",
                "command": [sys.executable, str(self.root / "infrastructure/auto_backup_uploader.py")],
                "timeout": 60,
                "priority": 4,
                "enabled": False  # 禁用：由会话结束检测器触发
            },
            {
                "id": "metrics_generator",
                "name": "Metrics 生成",
                "command": [sys.executable, str(self.root / "scripts/generate_metrics.py")],
                "timeout": 60,
                "priority": 5,
                "enabled": False  # 禁用：示例脚本有导入错误
            },
            {
                "id": "quick_inspection",
                "name": "快速巡检",
                "command": [sys.executable, str(self.root / "scripts/unified_inspector_v7.py"), "--quick"],
                "timeout": 120,
                "priority": 6,
                "enabled": False  # 禁用：避免耗时过长
            }
        ]
    
    def run_task(self, task: Dict) -> Dict:
        """运行单个任务"""
        result = {
            "id": task["id"],
            "name": task["name"],
            "start_time": datetime.now().isoformat(),
            "success": False,
            "output": "",
            "error": None,
            "duration_ms": 0
        }
        
        if not task.get("enabled", True):
            result["output"] = "任务已禁用"
            return result
        
        import time
        start = time.time()
        
        try:
            proc = subprocess.run(
                task["command"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                timeout=task.get("timeout", 60)
            )
            
            result["success"] = proc.returncode == 0
            result["output"] = proc.stdout[-500:] if proc.stdout else ""
            result["error"] = proc.stderr[-200:] if proc.stderr else None
            
        except subprocess.TimeoutExpired:
            result["error"] = f"超时 ({task.get('timeout', 60)}s)"
        except Exception as e:
            result["error"] = str(e)
        
        result["duration_ms"] = int((time.time() - start) * 1000)
        result["end_time"] = datetime.now().isoformat()
        
        return result
    
    def run_all(self) -> Dict:
        """运行所有任务"""
        print("\n" + "=" * 60)
        print("  心跳执行器 V7.2.0")
        print("=" * 60)
        print(f"\n  开始时间: {self.start_time.isoformat()}")
        print(f"  任务数量: {len(self.tasks)}")
        print("\n" + "-" * 60)
        
        # 按优先级排序
        sorted_tasks = sorted(self.tasks, key=lambda x: x.get("priority", 99))
        
        for task in sorted_tasks:
            print(f"\n  [{task['id']}] {task['name']}...")
            result = self.run_task(task)
            self.results.append(result)
            
            if result["success"]:
                print(f"    ✅ 成功 ({result['duration_ms']}ms)")
            elif result.get("output") == "任务已禁用":
                print(f"    ⏭️  跳过 (已禁用)")
            else:
                print(f"    ❌ 失败: {result.get('error', '未知错误')}")
        
        # 汇总
        end_time = datetime.now()
        total_duration = int((end_time - self.start_time).total_seconds() * 1000)
        success_count = sum(1 for r in self.results if r["success"])
        
        print("\n" + "-" * 60)
        print(f"\n  完成时间: {end_time.isoformat()}")
        print(f"  总耗时: {total_duration}ms")
        print(f"  成功: {success_count}/{len(self.results)}")
        
        # 检查待发送消息
        pending_sends = self._get_pending_sends()
        
        # 保存结果
        report = {
            "version": "V7.3.0",
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration_ms": total_duration,
            "success_count": success_count,
            "total_count": len(self.results),
            "results": self.results,
            "pending_sends": pending_sends
        }
        
        report_path = self.root / "reports/ops/heartbeat_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  报告: {report_path}")
        
        # 输出待发送消息
        if pending_sends:
            print("\n" + "=" * 60)
            print("  📤 待发送消息:")
            print("=" * 60)
            for msg in pending_sends:
                print(f"  - {msg.get('title', '无标题')}: {msg.get('message', '')[:50]}...")
            print("=" * 60)
        
        print("\n" + "=" * 60)
        
        if success_count == len(self.results):
            print("  ✅ HEARTBEAT_OK")
        else:
            print("  ⚠️  部分任务失败")
        print("=" * 60 + "\n")
        
        return report
    
    def _get_pending_sends(self) -> List[Dict[str, Any]]:
        """获取并清空待发送消息"""
        pending_file = self.root / "reports/ops/pending_sends.jsonl"
        
        if not pending_file.exists():
            return []
        
        messages = []
        with open(pending_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    messages.append(json.loads(line.strip()))
                except:
                    pass
        
        # 清空文件
        if messages:
            pending_file.unlink(missing_ok=True)
        
        return messages


def main():
    """主函数"""
    root = get_project_root()
    executor = HeartbeatExecutor(root)
    report = executor.run_all()
    
    # 返回退出码
    return 0 if report["success_count"] == report["total_count"] else 1


if __name__ == "__main__":
    sys.exit(main())
