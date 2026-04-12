"""
文件保护模块 V2.0
防止在升级优化过程中误删有用文件

V2.0 改进：
1. 使用 path_resolver 统一路径
2. 更新保护清单为当前架构
3. 移除旧架构引用
"""

import os
import json
from pathlib import Path
from datetime import datetime

# 使用 path_resolver 获取路径
from infrastructure.path_resolver import get_project_root

class FileGuardian:
    """文件保护守护者 V2.0"""
    
    # 核心受保护文件 (当前架构)
    CORE_PROTECTED = [
        # L1 核心认知层
        "AGENTS.md",
        "SOUL.md", 
        "USER.md",
        "TOOLS.md",
        "IDENTITY.md",
        "MEMORY.md",
        "HEARTBEAT.md",
        
        # 架构文件 (当前唯一主架构)
        "core/ARCHITECTURE.md",
        "core/ARCHITECTURE_INTEGRITY.md",
        
        # L5 安全治理层
        "governance/guard/file_guardian.py",
        "governance/guard/protected_files.json",
        "governance/security.py",
        "governance/audit.py",
        
        # L6 基础设施层
        "infrastructure/path_resolver.py",
        "infrastructure/inventory/skill_registry.json",
        "infrastructure/inventory/skill_inverted_index.json",
        "infrastructure/token_budget.py",
    ]
    
    # 按类型受保护的文件模式
    PROTECTED_PATTERNS = {
        "memory": ["memory/*.md", "MEMORY.md"],
        "skills": ["skills/*/SKILL.md"],
        "config": ["*.json"],
    }
    
    def __init__(self):
        self.workspace = get_project_root()
        self.guard_dir = self.workspace / "governance" / "guard"
        self.protected_list_path = self.guard_dir / "protected_files.json"
        self.delete_log_path = self.guard_dir / "delete_log.json"
        
        self.protected = self._load_protected_list()
        self.delete_log = self._load_delete_log()
    
    def _load_protected_list(self) -> dict:
        """加载受保护文件列表"""
        if self.protected_list_path.exists():
            with open(self.protected_list_path) as f:
                return json.load(f)
        return {"core": self.CORE_PROTECTED, "user_added": []}
    
    def _save_protected_list(self):
        """保存受保护文件列表"""
        self.guard_dir.mkdir(parents=True, exist_ok=True)
        with open(self.protected_list_path, 'w') as f:
            json.dump(self.protected, f, indent=2, ensure_ascii=False)
    
    def _load_delete_log(self) -> list:
        """加载删除日志"""
        if self.delete_log_path.exists():
            with open(self.delete_log_path) as f:
                return json.load(f)
        return []
    
    def _log_delete_request(self, file_path: str, reason: str, status: str):
        """记录删除请求"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file": file_path,
            "reason": reason,
            "status": status,
            "necessity": self._analyze_necessity(file_path)
        }
        self.delete_log.append(entry)
        self.guard_dir.mkdir(parents=True, exist_ok=True)
        with open(self.delete_log_path, 'w') as f:
            json.dump(self.delete_log, f, indent=2, ensure_ascii=False)
    
    def _analyze_necessity(self, file_path: str) -> dict:
        """分析文件的必要性和作用"""
        path = self.workspace / file_path
        result = {
            "exists": path.exists(),
            "size": path.stat().st_size if path.exists() else 0,
            "type": path.suffix,
            "description": self._get_file_description(file_path)
        }
        return result
    
    def _get_file_description(self, file_path: str) -> str:
        """获取文件描述"""
        descriptions = {
            # L1 核心文件
            "AGENTS.md": "工作空间规则，定义每次会话的加载流程和六层架构",
            "SOUL.md": "身份定义，定义AI的性格和行为准则",
            "USER.md": "用户信息，记录用户的偏好和上下文",
            "TOOLS.md": "工具规则，定义工具的使用优先级和约束",
            "IDENTITY.md": "身份标识，定义AI的名称和形象",
            "MEMORY.md": "长期记忆，存储重要的历史信息",
            "HEARTBEAT.md": "心跳任务定义",
            
            # 架构文件
            "core/ARCHITECTURE.md": "唯一主架构文档，定义六层架构",
            "core/ARCHITECTURE_INTEGRITY.md": "架构完整性规范",
            
            # L5 安全文件
            "governance/guard/file_guardian.py": "文件保护模块，防止误删重要文件",
            "governance/guard/protected_files.json": "受保护文件列表",
            "governance/security.py": "安全检查模块",
            "governance/audit.py": "审计日志模块",
            
            # L6 基础设施文件
            "infrastructure/path_resolver.py": "路径解析模块，统一路径入口",
            "infrastructure/inventory/skill_registry.json": "技能注册表，唯一真源",
            "infrastructure/inventory/skill_inverted_index.json": "技能反向索引",
            "infrastructure/token_budget.py": "Token 预算管理",
        }
        return descriptions.get(file_path, "未知文件，需要人工评估")
    
    def is_protected(self, file_path: str) -> tuple:
        """检查文件是否受保护"""
        # 检查核心保护列表
        all_protected = self.protected.get("core", []) + self.protected.get("user_added", [])
        
        for protected_path in all_protected:
            if isinstance(protected_path, dict):
                protected_path = protected_path.get("path", "")
            if file_path == protected_path or file_path.endswith(protected_path):
                return True, f"核心受保护文件: {protected_path}"
        
        # 检查模式匹配
        import fnmatch
        for pattern_type, patterns in self.PROTECTED_PATTERNS.items():
            for pattern in patterns:
                if fnmatch.fnmatch(file_path, pattern):
                    return True, f"受保护模式({pattern_type}): {pattern}"
        
        return False, "未受保护"
    
    def request_delete(self, file_path: str, reason: str) -> dict:
        """请求删除文件 - 必须经过人工确认"""
        is_protected, protection_reason = self.is_protected(file_path)
        necessity = self._analyze_necessity(file_path)
        self._log_delete_request(file_path, reason, "pending")
        
        return {
            "action": "DELETE_CONFIRMATION_REQUIRED",
            "file": file_path,
            "is_protected": is_protected,
            "protection_reason": protection_reason if is_protected else None,
            "reason_for_delete": reason,
            "file_info": necessity,
            "require_manual_confirm": True
        }
    
    def confirm_delete(self, file_path: str, user_confirm: str) -> dict:
        """确认删除"""
        if user_confirm.lower() not in ["确认删除", "confirm", "yes"]:
            for entry in reversed(self.delete_log):
                if entry["file"] == file_path and entry["status"] == "pending":
                    entry["status"] = "rejected"
                    break
            with open(self.delete_log_path, 'w') as f:
                json.dump(self.delete_log, f, indent=2)
            
            return {
                "action": "DELETE_CANCELLED",
                "file": file_path,
                "message": f"删除已取消: {file_path}"
            }
        
        for entry in reversed(self.delete_log):
            if entry["file"] == file_path and entry["status"] == "pending":
                entry["status"] = "approved"
                break
        with open(self.delete_log_path, 'w') as f:
            json.dump(self.delete_log, f, indent=2)
        
        path = self.workspace / file_path
        if path.exists():
            import shutil
            trash_dir = self.workspace / ".trash"
            trash_dir.mkdir(exist_ok=True)
            shutil.move(str(path), str(trash_dir / path.name))
            
            return {
                "action": "DELETE_COMPLETED",
                "file": file_path,
                "message": f"文件已移至回收站: {file_path}"
            }
        else:
            return {
                "action": "FILE_NOT_FOUND",
                "file": file_path,
                "message": f"文件不存在: {file_path}"
            }
    
    def add_protection(self, file_path: str, reason: str):
        """添加文件到保护列表"""
        if "user_added" not in self.protected:
            self.protected["user_added"] = []
        
        self.protected["user_added"].append({
            "path": file_path,
            "reason": reason,
            "added_at": datetime.now().isoformat()
        })
        
        self._save_protected_list()
        
        return {
            "action": "PROTECTION_ADDED",
            "file": file_path,
            "message": f"已添加到保护列表: {file_path}"
        }


# 全局实例
file_guardian = FileGuardian()


def check_before_delete(file_path: str, reason: str = "") -> dict:
    """删除前检查 - 必须调用此函数"""
    return file_guardian.request_delete(file_path, reason)


def confirm_and_delete(file_path: str, user_confirm: str) -> dict:
    """确认后删除"""
    return file_guardian.confirm_delete(file_path, user_confirm)


def protect_file(file_path: str, reason: str) -> dict:
    """保护文件"""
    return file_guardian.add_protection(file_path, reason)
