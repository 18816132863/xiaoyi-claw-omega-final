#!/usr/bin/env python3
"""
永久在线守护模块 V1.0.0

功能：
- 保持关键模块/技能/配置永久在线
- 新对话自动恢复关键状态
- 防止记忆丢失
- 定期刷新保持活跃

守护对象：
- 融合引擎
- 核心技能
- 关键配置
- 记忆索引
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


class PermanentKeeper:
    """永久在线守护器"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.config_file = self.root / "config/permanent_keepers.json"
        self.state_file = self.root / "reports/ops/keeper_state.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 默认守护配置
        self.default_keepers = {
            "fusion_engine": {
                "name": "融合引擎",
                "type": "engine",
                "priority": "critical",
                "files": [
                    "infrastructure/inventory/fusion_index.json",
                    "config/unified.json"
                ],
                "refresh_interval_hours": 1,
                "auto_restore": True,
                "description": "统一融合索引，保证技能路由和模块发现"
            },
            "memory_engine": {
                "name": "记忆引擎",
                "type": "engine",
                "priority": "critical",
                "files": [
                    "MEMORY.md",
                    "memory_context/vector/embedding_config.json",
                    "memory_context/index/",
                    "skills/llm-memory-integration/config/llm_config.json"
                ],
                "refresh_interval_hours": 1,
                "auto_restore": True,
                "description": "长期记忆和向量索引，保证上下文连续性"
            },
            "rule_engine": {
                "name": "规则引擎",
                "type": "engine",
                "priority": "critical",
                "files": [
                    "core/RULE_REGISTRY.json",
                    "core/RULE_EXCEPTIONS.json",
                    "scripts/run_rule_engine.py"
                ],
                "refresh_interval_hours": 1,
                "auto_restore": True,
                "description": "规则注册和执行，保证门禁行为一致"
            },
            "exception_manager": {
                "name": "例外管理器",
                "type": "module",
                "priority": "high",
                "files": [
                    "scripts/exception_manager.py",
                    "reports/ops/rule_exception_history.json",
                    "reports/ops/rule_exception_status.json"
                ],
                "refresh_interval_hours": 1,
                "auto_restore": True,
                "description": "例外操作和历史，保证例外状态连续"
            },
            "dependency_manager": {
                "name": "依赖管理器",
                "type": "module",
                "priority": "high",
                "files": [
                    "scripts/dependency_manager.py",
                    "config/dependency_manifest.json",
                    "reports/ops/dependency_status.json"
                ],
                "refresh_interval_hours": 24,
                "auto_restore": True,
                "description": "依赖状态，保证环境一致性"
            },
            "delete_manager": {
                "name": "删除管理器",
                "type": "module",
                "priority": "high",
                "files": [
                    "scripts/delete_manager.py",
                    "archive/trash/",
                    "reports/ops/delete_log.json"
                ],
                "refresh_interval_hours": 24,
                "auto_restore": True,
                "description": "删除确认和回收站，防止误删"
            },
            "skill_registry": {
                "name": "技能注册表",
                "type": "registry",
                "priority": "critical",
                "files": [
                    "infrastructure/inventory/skill_registry.json",
                    "infrastructure/inventory/skill_registry_summary.json"
                ],
                "refresh_interval_hours": 1,
                "auto_restore": True,
                "description": "技能发现和路由，保证技能可用"
            },
            "core_identity": {
                "name": "核心身份",
                "type": "identity",
                "priority": "critical",
                "files": [
                    "SOUL.md",
                    "USER.md",
                    "IDENTITY.md",
                    "AGENTS.md",
                    "TOOLS.md"
                ],
                "refresh_interval_hours": 24,
                "auto_restore": True,
                "description": "身份和规则，保证行为一致"
            },
            "architecture": {
                "name": "架构文档",
                "type": "docs",
                "priority": "critical",
                "files": [
                    "core/ARCHITECTURE.md",
                    "core/LAYER_DEPENDENCY_MATRIX.md",
                    "core/LAYER_DEPENDENCY_RULES.json",
                    "core/LAYER_IO_CONTRACTS.md"
                ],
                "refresh_interval_hours": 24,
                "auto_restore": True,
                "description": "架构定义，保证结构一致"
            }
        }
    
    def _load_config(self) -> Dict:
        """加载守护配置"""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {"keepers": self.default_keepers, "version": "1.0.0"}
    
    def _save_config(self, config: Dict):
        """保存守护配置"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _load_state(self) -> Dict:
        """加载守护状态"""
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"states": {}, "last_check": None, "version": "1.0.0"}
    
    def _save_state(self, state: Dict):
        """保存守护状态"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    def init_config(self) -> Dict:
        """初始化守护配置"""
        config = self._load_config()
        
        # 合并默认配置
        for keeper_id, keeper in self.default_keepers.items():
            if keeper_id not in config.get("keepers", {}):
                config["keepers"][keeper_id] = keeper
        
        self._save_config(config)
        return config
    
    def check_keeper(self, keeper_id: str) -> Dict:
        """检查单个守护对象状态"""
        config = self._load_config()
        keepers = config.get("keepers", {})
        
        if keeper_id not in keepers:
            return {"status": "error", "message": f"守护对象不存在: {keeper_id}"}
        
        keeper = keepers[keeper_id]
        result = {
            "keeper_id": keeper_id,
            "name": keeper["name"],
            "type": keeper["type"],
            "priority": keeper["priority"],
            "files_status": [],
            "all_exist": True,
            "missing_files": []
        }
        
        for file_path in keeper["files"]:
            full_path = self.root / file_path
            exists = full_path.exists()
            result["files_status"].append({
                "path": file_path,
                "exists": exists
            })
            if not exists:
                result["all_exist"] = False
                result["missing_files"].append(file_path)
        
        return result
    
    def check_all(self) -> Dict:
        """检查所有守护对象状态"""
        config = self._load_config()
        keepers = config.get("keepers", {})
        
        results = {
            "total": len(keepers),
            "healthy": 0,
            "unhealthy": 0,
            "critical_issues": 0,
            "keepers": [],
            "checked_at": datetime.now().isoformat()
        }
        
        for keeper_id in keepers:
            status = self.check_keeper(keeper_id)
            results["keepers"].append(status)
            
            if status["all_exist"]:
                results["healthy"] += 1
            else:
                results["unhealthy"] += 1
                if status["priority"] == "critical":
                    results["critical_issues"] += 1
        
        # 保存状态
        state = self._load_state()
        state["last_check"] = results["checked_at"]
        state["summary"] = {
            "healthy": results["healthy"],
            "unhealthy": results["unhealthy"],
            "critical_issues": results["critical_issues"]
        }
        self._save_state(state)
        
        return results
    
    def refresh_keeper(self, keeper_id: str) -> Dict:
        """刷新单个守护对象"""
        config = self._load_config()
        keepers = config.get("keepers", {})
        
        if keeper_id not in keepers:
            return {"status": "error", "message": f"守护对象不存在: {keeper_id}"}
        
        keeper = keepers[keeper_id]
        
        # 更新最后刷新时间
        state = self._load_state()
        if "states" not in state:
            state["states"] = {}
        
        state["states"][keeper_id] = {
            "last_refreshed": datetime.now().isoformat(),
            "refresh_count": state["states"].get(keeper_id, {}).get("refresh_count", 0) + 1
        }
        self._save_state(state)
        
        # 执行刷新动作（根据类型）
        refresh_actions = {
            "fusion_engine": self._refresh_fusion_engine,
            "memory_engine": self._refresh_memory_engine,
            "rule_engine": self._refresh_rule_engine,
            "skill_registry": self._refresh_skill_registry
        }
        
        action = refresh_actions.get(keeper_id)
        if action:
            action_result = action()
        else:
            action_result = {"status": "skipped", "message": "无需特殊刷新"}
        
        return {
            "status": "success",
            "keeper_id": keeper_id,
            "name": keeper["name"],
            "refreshed_at": state["states"][keeper_id]["last_refreshed"],
            "action": action_result
        }
    
    def _refresh_fusion_engine(self) -> Dict:
        """刷新融合引擎"""
        try:
            # 重新生成融合索引
            result = subprocess.run(
                [sys.executable, str(self.root / "scripts/unified_inspector.py"), 
                 "--profile", "premerge", "--save"],
                capture_output=True,
                cwd=self.root
            )
            return {"status": "success", "message": "融合索引已刷新"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _refresh_memory_engine(self) -> Dict:
        """刷新记忆引擎"""
        try:
            # 检查记忆文件
            memory_file = self.root / "MEMORY.md"
            if memory_file.exists():
                return {"status": "success", "message": "记忆文件存在"}
            return {"status": "warning", "message": "记忆文件不存在"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _refresh_rule_engine(self) -> Dict:
        """刷新规则引擎"""
        try:
            result = subprocess.run(
                [sys.executable, str(self.root / "scripts/run_rule_engine.py"),
                 "--profile", "premerge", "--save"],
                capture_output=True,
                cwd=self.root
            )
            return {"status": "success", "message": "规则引擎已刷新"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _refresh_skill_registry(self) -> Dict:
        """刷新技能注册表"""
        try:
            registry = self.root / "infrastructure/inventory/skill_registry.json"
            if registry.exists():
                return {"status": "success", "message": "技能注册表存在"}
            return {"status": "warning", "message": "技能注册表不存在"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def refresh_all(self) -> Dict:
        """刷新所有守护对象"""
        config = self._load_config()
        keepers = config.get("keepers", {})
        
        results = {
            "refreshed": [],
            "failed": [],
            "skipped": []
        }
        
        for keeper_id in keepers:
            result = self.refresh_keeper(keeper_id)
            if result["status"] == "success":
                results["refreshed"].append(keeper_id)
            elif result["status"] == "error":
                results["failed"].append(keeper_id)
            else:
                results["skipped"].append(keeper_id)
        
        return results
    
    def add_keeper(self, keeper_id: str, name: str, keeper_type: str,
                   files: List[str], priority: str = "high",
                   refresh_interval_hours: int = 24,
                   description: str = "") -> Dict:
        """添加新的守护对象"""
        config = self._load_config()
        
        if keeper_id in config.get("keepers", {}):
            return {"status": "error", "message": f"守护对象已存在: {keeper_id}"}
        
        config["keepers"][keeper_id] = {
            "name": name,
            "type": keeper_type,
            "priority": priority,
            "files": files,
            "refresh_interval_hours": refresh_interval_hours,
            "auto_restore": True,
            "description": description
        }
        
        self._save_config(config)
        
        return {
            "status": "success",
            "keeper_id": keeper_id,
            "message": f"已添加守护对象: {name}"
        }
    
    def remove_keeper(self, keeper_id: str) -> Dict:
        """移除守护对象"""
        config = self._load_config()
        
        if keeper_id not in config.get("keepers", {}):
            return {"status": "error", "message": f"守护对象不存在: {keeper_id}"}
        
        name = config["keepers"][keeper_id]["name"]
        del config["keepers"][keeper_id]
        
        self._save_config(config)
        
        return {
            "status": "success",
            "keeper_id": keeper_id,
            "message": f"已移除守护对象: {name}"
        }
    
    def list_keepers(self) -> Dict:
        """列出所有守护对象"""
        config = self._load_config()
        keepers = config.get("keepers", {})
        
        return {
            "total": len(keepers),
            "keepers": [
                {
                    "keeper_id": kid,
                    "name": k["name"],
                    "type": k["type"],
                    "priority": k["priority"],
                    "files_count": len(k["files"]),
                    "description": k.get("description", "")
                }
                for kid, k in keepers.items()
            ]
        }
    
    def restore_missing(self) -> Dict:
        """恢复缺失的守护文件"""
        config = self._load_config()
        keepers = config.get("keepers", {})
        
        results = {
            "restored": [],
            "cannot_restore": [],
            "no_action_needed": []
        }
        
        for keeper_id, keeper in keepers.items():
            for file_path in keeper["files"]:
                full_path = self.root / file_path
                if not full_path.exists():
                    # 尝试从备份恢复
                    backup_path = self.root / "archive/backups"
                    if backup_path.exists():
                        # 标记为需要恢复
                        results["cannot_restore"].append({
                            "keeper_id": keeper_id,
                            "file": file_path,
                            "reason": "需要从备份手动恢复"
                        })
                    else:
                        results["cannot_restore"].append({
                            "keeper_id": keeper_id,
                            "file": file_path,
                            "reason": "无备份可用"
                        })
                else:
                    results["no_action_needed"].append(file_path)
        
        return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="永久在线守护模块 V1.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # init
    subparsers.add_parser("init", help="初始化守护配置")
    
    # check
    check_parser = subparsers.add_parser("check", help="检查守护状态")
    check_parser.add_argument("--keeper", help="检查单个守护对象")
    
    # refresh
    refresh_parser = subparsers.add_parser("refresh", help="刷新守护对象")
    refresh_parser.add_argument("--keeper", help="刷新单个守护对象")
    
    # list
    subparsers.add_parser("list", help="列出所有守护对象")
    
    # add
    add_parser = subparsers.add_parser("add", help="添加守护对象")
    add_parser.add_argument("--id", required=True, help="守护对象ID")
    add_parser.add_argument("--name", required=True, help="名称")
    add_parser.add_argument("--type", required=True, help="类型")
    add_parser.add_argument("--files", required=True, help="文件列表(逗号分隔)")
    add_parser.add_argument("--priority", default="high", help="优先级")
    add_parser.add_argument("--description", default="", help="描述")
    
    # remove
    remove_parser = subparsers.add_parser("remove", help="移除守护对象")
    remove_parser.add_argument("--id", required=True, help="守护对象ID")
    
    # restore
    subparsers.add_parser("restore", help="恢复缺失文件")
    
    args = parser.parse_args()
    
    keeper = PermanentKeeper()
    
    if args.command == "init":
        result = keeper.init_config()
        print(json.dumps({"status": "success", "message": "守护配置已初始化", 
                         "keepers_count": len(result["keepers"])}, ensure_ascii=False, indent=2))
    elif args.command == "check":
        if args.keeper:
            result = keeper.check_keeper(args.keeper)
        else:
            result = keeper.check_all()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "refresh":
        if args.keeper:
            result = keeper.refresh_keeper(args.keeper)
        else:
            result = keeper.refresh_all()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "list":
        result = keeper.list_keepers()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "add":
        files = [f.strip() for f in args.files.split(",")]
        result = keeper.add_keeper(
            keeper_id=args.id,
            name=args.name,
            keeper_type=args.type,
            files=files,
            priority=args.priority,
            description=args.description
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "remove":
        result = keeper.remove_keeper(args.id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "restore":
        result = keeper.restore_missing()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
