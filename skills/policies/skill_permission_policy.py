"""
技能权限策略

定义技能的权限控制和访问策略
"""

from enum import Enum
from typing import Dict, List, Optional, Set


class Permission(Enum):
    """权限类型"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


class SkillPermissionPolicy:
    """技能权限策略"""
    
    # 默认权限映射
    DEFAULT_PERMISSIONS = {
        "xiaoyi-gui-agent": {Permission.EXECUTE, Permission.READ},
        "send_message": {Permission.EXECUTE},
        "create_note": {Permission.WRITE, Permission.READ},
        "delete_file": {Permission.DELETE},
        "web_search": {Permission.READ, Permission.EXECUTE},
    }
    
    # 敏感能力
    SENSITIVE_CAPABILITIES = [
        "MESSAGE_SENDING",
        "MAKE_CALL",
        "DELETE_FILE",
        "DELETE_PHOTO",
        "PAYMENT",
    ]
    
    def __init__(self):
        self.permissions: Dict[str, Set[Permission]] = {
            k: set(v) for k, v in self.DEFAULT_PERMISSIONS.items()
        }
        self.granted_skills: Set[str] = set()
        self.denied_skills: Set[str] = set()
    
    def grant(self, skill_id: str, permissions: List[Permission] = None):
        """授予权限"""
        if permissions:
            if skill_id not in self.permissions:
                self.permissions[skill_id] = set()
            self.permissions[skill_id].update(permissions)
        
        self.granted_skills.add(skill_id)
        self.denied_skills.discard(skill_id)
    
    def revoke(self, skill_id: str, permissions: List[Permission] = None):
        """撤销权限"""
        if permissions and skill_id in self.permissions:
            self.permissions[skill_id] -= set(permissions)
        else:
            self.permissions.pop(skill_id, None)
        
        self.granted_skills.discard(skill_id)
    
    def deny(self, skill_id: str):
        """拒绝技能"""
        self.denied_skills.add(skill_id)
        self.granted_skills.discard(skill_id)
    
    def has_permission(self, skill_id: str, permission: Permission) -> bool:
        """检查是否有权限"""
        if skill_id in self.denied_skills:
            return False
        
        if skill_id in self.granted_skills:
            return True
        
        return permission in self.permissions.get(skill_id, set())
    
    def can_execute(self, skill_id: str) -> bool:
        """检查是否可以执行"""
        return self.has_permission(skill_id, Permission.EXECUTE)
    
    def can_read(self, skill_id: str) -> bool:
        """检查是否可以读取"""
        return self.has_permission(skill_id, Permission.READ)
    
    def can_write(self, skill_id: str) -> bool:
        """检查是否可以写入"""
        return self.has_permission(skill_id, Permission.WRITE)
    
    def can_delete(self, skill_id: str) -> bool:
        """检查是否可以删除"""
        return self.has_permission(skill_id, Permission.DELETE)
    
    def is_sensitive(self, capability: str) -> bool:
        """检查是否是敏感能力"""
        return capability in self.SENSITIVE_CAPABILITIES
    
    def get_permissions(self, skill_id: str) -> Set[Permission]:
        """获取技能权限"""
        return self.permissions.get(skill_id, set())


__all__ = ["SkillPermissionPolicy", "Permission"]
