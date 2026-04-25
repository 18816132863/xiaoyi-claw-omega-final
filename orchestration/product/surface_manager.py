#!/usr/bin/env python3
"""
产品封装层管理器 - V2.8.0

标准模式定义：
- 分析模式：数据分析、报告生成
- 执行模式：任务执行、工作流运行
- 审计模式：架构检查、代码审计
- 项目推进模式：项目跟踪、状态管理

标准入口定义：
- 任务入口：执行单个任务
- 项目入口：管理项目
- 产物入口：查看产物
- 审计入口：执行审计

标准角色定义：
- 老板视角：总览、决策支持
- 运营视角：执行、监控
- 选品视角：分析、对比
- 架构视角：审计、优化

标准输出定义：
- 报告：Markdown/DOCX
- 表格：CSV/XLSX
- 指令书：TXT
- 阶段总结：Markdown
- 待办清单：Markdown
"""

import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

from infrastructure.path_resolver import get_project_root

class Mode(Enum):
    ANALYSIS = "analysis"       # 分析模式
    EXECUTION = "execution"     # 执行模式
    AUDIT = "audit"             # 审计模式
    PROJECT = "project"         # 项目推进模式

class Entry(Enum):
    TASK = "task"               # 任务入口
    PROJECT = "project"         # 项目入口
    PRODUCT = "product"         # 产物入口
    AUDIT = "audit"             # 审计入口

class Role(Enum):
    BOSS = "boss"               # 老板视角
    OPERATOR = "operator"       # 运营视角
    SELECTOR = "selector"       # 选品视角
    ARCHITECT = "architect"     # 架构视角

class OutputType(Enum):
    REPORT = "report"           # 报告
    TABLE = "table"             # 表格
    INSTRUCTION = "instruction" # 指令书
    SUMMARY = "summary"         # 阶段总结
    TODO_LIST = "todo_list"     # 待办清单

@dataclass
class ProductMode:
    """产品模式"""
    name: str
    description: str
    available_entries: List[str]
    available_roles: List[str]
    default_output: str

@dataclass
class ProductEntry:
    """产品入口"""
    name: str
    description: str
    required_params: List[str]
    optional_params: List[str]
    supported_modes: List[str]

@dataclass
class ProductRole:
    """产品角色"""
    name: str
    description: str
    allowed_modes: List[str]
    allowed_entries: List[str]
    default_outputs: List[str]

class ProductSurfaceManager:
    """产品封装层管理器"""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.config_path = self.project_root / 'product' / 'surface_config.json'
        
        # 定义模式
        self.modes: Dict[str, ProductMode] = {
            Mode.ANALYSIS.value: ProductMode(
                name=Mode.ANALYSIS.value,
                description="分析模式 - 数据分析、报告生成",
                available_entries=[Entry.TASK.value, Entry.PRODUCT.value],
                available_roles=[Role.BOSS.value, Role.SELECTOR.value],
                default_output=OutputType.REPORT.value
            ),
            Mode.EXECUTION.value: ProductMode(
                name=Mode.EXECUTION.value,
                description="执行模式 - 任务执行、工作流运行",
                available_entries=[Entry.TASK.value, Entry.PROJECT.value],
                available_roles=[Role.OPERATOR.value],
                default_output=OutputType.INSTRUCTION.value
            ),
            Mode.AUDIT.value: ProductMode(
                name=Mode.AUDIT.value,
                description="审计模式 - 架构检查、代码审计",
                available_entries=[Entry.AUDIT.value, Entry.PRODUCT.value],
                available_roles=[Role.ARCHITECT.value],
                default_output=OutputType.REPORT.value
            ),
            Mode.PROJECT.value: ProductMode(
                name=Mode.PROJECT.value,
                description="项目推进模式 - 项目跟踪、状态管理",
                available_entries=[Entry.PROJECT.value, Entry.TASK.value],
                available_roles=[Role.BOSS.value, Role.OPERATOR.value],
                default_output=OutputType.SUMMARY.value
            )
        }
        
        # 定义入口
        self.entries: Dict[str, ProductEntry] = {
            Entry.TASK.value: ProductEntry(
                name=Entry.TASK.value,
                description="任务入口 - 执行单个任务",
                required_params=["task_type"],
                optional_params=["workflow", "params", "output_format"],
                supported_modes=[Mode.ANALYSIS.value, Mode.EXECUTION.value, Mode.PROJECT.value]
            ),
            Entry.PROJECT.value: ProductEntry(
                name=Entry.PROJECT.value,
                description="项目入口 - 管理项目",
                required_params=["action"],
                optional_params=["project_id", "project_name", "params"],
                supported_modes=[Mode.EXECUTION.value, Mode.PROJECT.value]
            ),
            Entry.PRODUCT.value: ProductEntry(
                name=Entry.PRODUCT.value,
                description="产物入口 - 查看产物",
                required_params=[],
                optional_params=["product_type", "project", "limit"],
                supported_modes=[Mode.ANALYSIS.value, Mode.AUDIT.value, Mode.EXECUTION.value]
            ),
            Entry.AUDIT.value: ProductEntry(
                name=Entry.AUDIT.value,
                description="审计入口 - 执行审计",
                required_params=["audit_type"],
                optional_params=["scope", "depth"],
                supported_modes=[Mode.AUDIT.value]
            )
        }
        
        # 定义角色
        self.roles: Dict[str, ProductRole] = {
            Role.BOSS.value: ProductRole(
                name=Role.BOSS.value,
                description="老板视角 - 总览、决策支持",
                allowed_modes=[Mode.ANALYSIS.value, Mode.PROJECT.value],
                allowed_entries=[Entry.TASK.value, Entry.PROJECT.value, Entry.PRODUCT.value],
                default_outputs=[OutputType.REPORT.value, OutputType.SUMMARY.value]
            ),
            Role.OPERATOR.value: ProductRole(
                name=Role.OPERATOR.value,
                description="运营视角 - 执行、监控",
                allowed_modes=[Mode.EXECUTION.value, Mode.PROJECT.value],
                allowed_entries=[Entry.TASK.value, Entry.PROJECT.value, Entry.PRODUCT.value],
                default_outputs=[OutputType.INSTRUCTION.value, OutputType.TODO_LIST.value]
            ),
            Role.SELECTOR.value: ProductRole(
                name=Role.SELECTOR.value,
                description="选品视角 - 分析、对比",
                allowed_modes=[Mode.ANALYSIS.value],
                allowed_entries=[Entry.TASK.value, Entry.PRODUCT.value],
                default_outputs=[OutputType.TABLE.value, OutputType.REPORT.value]
            ),
            Role.ARCHITECT.value: ProductRole(
                name=Role.ARCHITECT.value,
                description="架构视角 - 审计、优化",
                allowed_modes=[Mode.AUDIT.value],
                allowed_entries=[Entry.AUDIT.value, Entry.PRODUCT.value],
                default_outputs=[OutputType.REPORT.value]
            )
        }
        
        # 当前状态
        self.current_mode: Optional[str] = None
        self.current_role: Optional[str] = None
    
    def set_mode(self, mode: str) -> Dict:
        """设置模式"""
        if mode not in self.modes:
            return {"error": f"未知模式: {mode}"}
        
        self.current_mode = mode
        mode_info = self.modes[mode]
        
        return {
            "status": "success",
            "mode": mode,
            "description": mode_info.description,
            "available_entries": mode_info.available_entries,
            "available_roles": mode_info.available_roles
        }
    
    def set_role(self, role: str) -> Dict:
        """设置角色"""
        if role not in self.roles:
            return {"error": f"未知角色: {role}"}
        
        self.current_role = role
        role_info = self.roles[role]
        
        return {
            "status": "success",
            "role": role,
            "description": role_info.description,
            "allowed_modes": role_info.allowed_modes,
            "allowed_entries": role_info.allowed_entries
        }
    
    def call_entry(self, entry: str, params: Dict) -> Dict:
        """调用入口"""
        if entry not in self.entries:
            return {"error": f"未知入口: {entry}"}
        
        entry_info = self.entries[entry]
        
        # 检查模式兼容
        if self.current_mode and self.current_mode not in entry_info.supported_modes:
            return {"error": f"当前模式 {self.current_mode} 不支持入口 {entry}"}
        
        # 检查必需参数
        missing = [p for p in entry_info.required_params if p not in params]
        if missing:
            return {"error": f"缺少必需参数: {missing}"}
        
        # 执行入口逻辑
        return self._execute_entry(entry, params)
    
    def _execute_entry(self, entry: str, params: Dict) -> Dict:
        """执行入口逻辑"""
        if entry == Entry.TASK.value:
            return self._execute_task(params)
        elif entry == Entry.PROJECT.value:
            return self._execute_project(params)
        elif entry == Entry.PRODUCT.value:
            return self._execute_product(params)
        elif entry == Entry.AUDIT.value:
            return self._execute_audit(params)
        return {"error": "未实现的入口"}
    
    def _execute_task(self, params: Dict) -> Dict:
        """执行任务"""
        task_type = params.get("task_type")
        workflow = params.get("workflow")
        
        return {
            "status": "success",
            "entry": "task",
            "task_type": task_type,
            "workflow": workflow or "auto_selected",
            "message": f"任务已提交: {task_type}"
        }
    
    def _execute_project(self, params: Dict) -> Dict:
        """执行项目管理"""
        action = params.get("action")
        
        return {
            "status": "success",
            "entry": "project",
            "action": action,
            "message": f"项目操作已执行: {action}"
        }
    
    def _execute_product(self, params: Dict) -> Dict:
        """查看产物"""
        product_type = params.get("product_type", "all")
        limit = params.get("limit", 10)
        
        return {
            "status": "success",
            "entry": "product",
            "product_type": product_type,
            "limit": limit,
            "message": f"产物列表已获取"
        }
    
    def _execute_audit(self, params: Dict) -> Dict:
        """执行审计"""
        audit_type = params.get("audit_type")
        
        return {
            "status": "success",
            "entry": "audit",
            "audit_type": audit_type,
            "message": f"审计已执行: {audit_type}"
        }
    
    def get_available_modes(self) -> List[Dict]:
        """获取可用模式"""
        return [
            {"name": m.name, "description": m.description}
            for m in self.modes.values()
        ]
    
    def get_available_entries(self) -> List[Dict]:
        """获取可用入口"""
        return [
            {"name": e.name, "description": e.description, "required_params": e.required_params}
            for e in self.entries.values()
        ]
    
    def get_available_roles(self) -> List[Dict]:
        """获取可用角色"""
        return [
            {"name": r.name, "description": r.description}
            for r in self.roles.values()
        ]
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "current_mode": self.current_mode,
            "current_role": self.current_role,
            "available_modes": len(self.modes),
            "available_entries": len(self.entries),
            "available_roles": len(self.roles)
        }
    
    def get_report(self) -> str:
        """生成报告"""
        lines = [
            "# 产品封装层报告",
            "",
            "## 当前状态",
            f"- 模式: {self.current_mode or '未设置'}",
            f"- 角色: {self.current_role or '未设置'}",
            "",
            "## 可用模式",
            ""
        ]
        
        for mode in self.modes.values():
            lines.append(f"- **{mode.name}**: {mode.description}")
        
        lines.extend([
            "",
            "## 可用入口",
            ""
        ])
        
        for entry in self.entries.values():
            lines.append(f"- **{entry.name}**: {entry.description}")
        
        lines.extend([
            "",
            "## 可用角色",
            ""
        ])
        
        for role in self.roles.values():
            lines.append(f"- **{role.name}**: {role.description}")
        
        return "\n".join(lines)

# 全局实例
_surface_manager = None

def get_surface_manager() -> ProductSurfaceManager:
    global _surface_manager
    if _surface_manager is None:
        _surface_manager = ProductSurfaceManager()
    return _surface_manager
