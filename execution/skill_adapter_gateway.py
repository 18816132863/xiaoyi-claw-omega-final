#!/usr/bin/env python3
"""
技能适配网关 - V1.0.0

职责：
1. 读取 registry
2. 按 entry_point 定位真实技能文件
3. 用 importlib 按文件路径加载模块
4. 调用 run(params) 并返回统一结果
"""

import os
import sys
import json
import importlib.util
from pathlib import Path
from typing import Dict, Optional, Any

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent

def load_json(path: Path) -> Optional[Dict]:
    if not path.exists():
        return None
    try:
        return json.load(open(path, encoding='utf-8'))
    except:
        return None

class SkillAdapterGateway:
    """技能适配网关"""

    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.registry_path = self.root / "infrastructure" / "inventory" / "skill_registry.json"
        self._registry = None

    @property
    def registry(self) -> Dict:
        if self._registry is None:
            self._registry = load_json(self.registry_path) or {}
        return self._registry

    def get_skill_info(self, skill_name: str) -> Optional[Dict]:
        """获取技能信息"""
        return self.registry.get("skills", {}).get(skill_name)

    def is_skill_available(self, skill_name: str) -> bool:
        """检查技能是否可用"""
        info = self.get_skill_info(skill_name)
        if not info:
            return False
        return info.get("registered", False) and info.get("routable", False) and info.get("callable", False)

    def load_skill_module(self, skill_name: str):
        """按文件路径加载技能模块"""
        info = self.get_skill_info(skill_name)
        if not info:
            raise ValueError(f"技能未注册: {skill_name}")

        entry_point = info.get("entry_point")
        if not entry_point:
            raise ValueError(f"技能缺少 entry_point: {skill_name}")

        # 解析文件路径
        skill_path = self.root / entry_point
        if not skill_path.exists():
            raise FileNotFoundError(f"技能文件不存在: {skill_path}")

        # 按文件路径加载模块
        module_name = f"skill_{skill_name.replace('-', '_')}"
        spec = importlib.util.spec_from_file_location(module_name, skill_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"无法加载技能模块: {skill_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

    def execute(self, skill_name: str, params: Dict) -> Dict:
        """
        执行技能

        Args:
            skill_name: 技能名称
            params: 执行参数

        Returns:
            {"success": bool, "data": {...}, "error": {...}}
        """
        try:
            # 检查技能是否可用
            if not self.is_skill_available(skill_name):
                return {
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "SKILL_NOT_AVAILABLE",
                        "message": f"技能不可用: {skill_name}"
                    }
                }

            # 加载模块
            module = self.load_skill_module(skill_name)

            # 获取 run 函数
            run_func = getattr(module, "run", None)
            if run_func is None:
                return {
                    "success": False,
                    "data": None,
                    "error": {
                        "code": "NO_RUN_FUNCTION",
                        "message": f"技能模块缺少 run 函数: {skill_name}"
                    }
                }

            # 执行
            result = run_func(params)

            # 标准化返回值
            if isinstance(result, dict):
                if "success" in result:
                    return result
                else:
                    # 兼容旧格式
                    return {
                        "success": True,
                        "data": result,
                        "error": None
                    }
            else:
                return {
                    "success": True,
                    "data": {"result": result},
                    "error": None
                }

        except FileNotFoundError as e:
            return {
                "success": False,
                "data": None,
                "error": {"code": "FILE_NOT_FOUND", "message": str(e)}
            }
        except ImportError as e:
            return {
                "success": False,
                "data": None,
                "error": {"code": "IMPORT_ERROR", "message": str(e)}
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": {"code": "EXECUTION_ERROR", "message": str(e)}
            }

# 全局实例
_gateway = None

def get_gateway() -> SkillAdapterGateway:
    global _gateway
    if _gateway is None:
        _gateway = SkillAdapterGateway()
    return _gateway

def execute_skill(skill_name: str, params: Dict) -> Dict:
    """执行技能的便捷函数"""
    return get_gateway().execute(skill_name, params)
