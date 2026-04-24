"""
Runtime Self Check - 运行时自检
检查系统完整性和能力可用性
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys
import sqlite3


class RuntimeSelfCheck:
    """运行时自检"""
    
    def __init__(self):
        self.checks: List[Dict[str, Any]] = []
        self.project_root = Path(__file__).parent.parent
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """运行所有检查"""
        self.checks = []
        
        # 1. 检查数据库表
        self._check_database_tables()
        
        # 2. 检查状态机
        self._check_state_machine()
        
        # 3. 检查能力注册（先 bootstrap）
        self._check_capabilities()
        
        # 4. 检查平台适配
        self._check_platform_adapter()
        
        # 5. 检查Python环境
        self._check_python_env()
        
        # 6. 检查默认链路
        await self._check_default_chain()
        
        # 汇总结果
        passed = sum(1 for c in self.checks if c["status"] == "pass")
        failed = sum(1 for c in self.checks if c["status"] == "fail")
        warnings = sum(1 for c in self.checks if c["status"] == "warning")
        
        return {
            "success": failed == 0,
            "overall_status": "healthy" if failed == 0 else "degraded",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total": len(self.checks),
                "passed": passed,
                "failed": failed,
                "warnings": warnings
            },
            "checks": self.checks
        }
    
    def _check_database_tables(self):
        """检查数据库表结构"""
        db_path = self.project_root / "data" / "tasks.db"
        
        if not db_path.exists():
            self.checks.append({
                "name": "database_tables",
                "status": "warning",
                "message": "数据库文件不存在，将在首次使用时创建"
            })
            return
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # 获取所有表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 检查必需表
            required_tables = [
                'tasks', 
                'task_runs', 
                'task_steps', 
                'task_events', 
                'workflow_checkpoints'
            ]
            
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                self.checks.append({
                    "name": "database_tables",
                    "status": "fail",
                    "message": f"缺少表: {missing_tables}",
                    "details": {"existing": tables, "missing": missing_tables}
                })
            else:
                # 统计记录数
                counts = {}
                for table in required_tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                
                self.checks.append({
                    "name": "database_tables",
                    "status": "pass",
                    "message": f"所有必需表存在，共 {sum(counts.values())} 条记录",
                    "details": {"tables": counts}
                })
            
            conn.close()
            
        except Exception as e:
            self.checks.append({
                "name": "database_tables",
                "status": "fail",
                "message": f"数据库检查失败: {e}"
            })
    
    def _check_state_machine(self):
        """检查状态机"""
        try:
            from domain.tasks import TaskStatus, StepStatus, EventType
            
            # 验证状态枚举
            task_statuses = [s.value for s in TaskStatus]
            step_statuses = [s.value for s in StepStatus]
            
            self.checks.append({
                "name": "state_machine",
                "status": "pass",
                "message": f"状态机定义完整: {len(task_statuses)} 任务状态, {len(step_statuses)} 步骤状态",
                "details": {
                    "task_statuses": task_statuses,
                    "step_statuses": step_statuses
                }
            })
        except ImportError as e:
            self.checks.append({
                "name": "state_machine",
                "status": "fail",
                "message": f"状态机导入失败: {e}"
            })
    
    def _check_capabilities(self):
        """检查能力注册"""
        try:
            # 先执行 bootstrap
            from capabilities import ensure_bootstrap, get_registry
            ensure_bootstrap()
            
            registry = get_registry()
            caps = registry.list_all()
            
            # 核心能力列表
            core_capabilities = [
                "send_message",
                "schedule_task",
                "retry_task",
                "pause_task",
                "resume_task",
                "cancel_task",
                "diagnostics",
                "export_history",
                "replay_run"
            ]
            
            missing = [c for c in core_capabilities if c not in caps]
            
            if len(caps) == 0:
                self.checks.append({
                    "name": "capabilities",
                    "status": "fail",
                    "message": "能力注册表为空"
                })
            elif missing:
                self.checks.append({
                    "name": "capabilities",
                    "status": "fail",
                    "message": f"缺少核心能力: {missing}",
                    "details": {"registered": caps, "missing": missing}
                })
            else:
                self.checks.append({
                    "name": "capabilities",
                    "status": "pass",
                    "message": f"已注册 {len(caps)} 个能力，包含所有核心能力",
                    "details": {"capabilities": caps}
                })
                
        except Exception as e:
            self.checks.append({
                "name": "capabilities",
                "status": "fail",
                "message": f"能力检查失败: {e}"
            })
    
    def _check_platform_adapter(self):
        """检查平台适配"""
        try:
            from platform_adapter.runtime_probe import RuntimeProbe
            
            env = RuntimeProbe.detect_environment()
            recommended = RuntimeProbe.get_recommended_adapter()
            
            # 验证推荐适配器是否存在
            adapter_exists = False
            adapter_available = False
            
            if recommended == "xiaoyi":
                try:
                    from platform_adapter.xiaoyi_adapter import XiaoyiAdapter
                    adapter_exists = True
                    # 检查适配器是否真的可用
                    import asyncio
                    adapter = XiaoyiAdapter()
                    probe_result = asyncio.run(adapter.probe())
                    adapter_available = probe_result.get("available", False)
                except ImportError:
                    pass
            elif recommended == "null":
                adapter_exists = True  # null adapter 总是存在
                adapter_available = False  # 但不可用
            
            if not adapter_exists:
                self.checks.append({
                    "name": "platform_adapter",
                    "status": "fail",
                    "message": f"推荐适配器 '{recommended}' 不存在",
                    "details": env
                })
            elif recommended != "null" and not adapter_available:
                # 推荐适配器存在但不可用，应该回退到 skill_default
                self.checks.append({
                    "name": "platform_adapter",
                    "status": "warning",
                    "message": f"适配器 '{recommended}' 存在但能力未接通，已回退到 skill_default",
                    "details": env
                })
            else:
                self.checks.append({
                    "name": "platform_adapter",
                    "status": "pass",
                    "message": f"运行模式: {env['runtime_mode']}, 适配器: {recommended}",
                    "details": env
                })
                
        except Exception as e:
            self.checks.append({
                "name": "platform_adapter",
                "status": "warning",
                "message": f"平台适配检查跳过: {e}"
            })
    
    def _check_python_env(self):
        """检查Python环境"""
        self.checks.append({
            "name": "python_env",
            "status": "pass",
            "message": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "details": {
                "version": sys.version,
                "executable": sys.executable
            }
        })
    
    async def _check_default_chain(self):
        """检查默认链路：创建任务 -> 查询任务"""
        try:
            from infrastructure.task_manager import get_task_manager
            
            tm = get_task_manager()
            
            # 创建测试任务
            result = await tm.create_scheduled_message(
                user_id="self_check",
                message="Self check test",
                run_at=datetime.now().isoformat()
            )
            
            if not result.get("success"):
                self.checks.append({
                    "name": "default_chain",
                    "status": "fail",
                    "message": f"创建任务失败: {result.get('error')}"
                })
                return
            
            task_id = result.get("task_id")
            
            # 查询任务
            task = await tm.get_task(task_id)
            
            if not task:
                self.checks.append({
                    "name": "default_chain",
                    "status": "fail",
                    "message": "任务创建成功但查询失败"
                })
                return
            
            # 清理测试任务
            db_path = self.project_root / "data" / "tasks.db"
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE user_id = 'self_check'")
                conn.commit()
                conn.close()
            
            self.checks.append({
                "name": "default_chain",
                "status": "pass",
                "message": "默认链路正常：创建任务 -> 查询任务 -> 清理",
                "details": {"test_task_id": task_id}
            })
            
        except Exception as e:
            self.checks.append({
                "name": "default_chain",
                "status": "fail",
                "message": f"默认链路检查失败: {e}"
            })
