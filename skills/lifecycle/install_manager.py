"""Skill Install Manager - 技能安装管理器"""

from dataclasses import dataclass
from typing import Dict, Optional, Any
from datetime import datetime
import json
import os

from skills.registry.skill_registry import SkillManifest, SkillCategory, SkillStatus


@dataclass
class InstallResult:
    """安装结果"""
    success: bool
    skill_id: str
    message: str
    manifest: Optional[SkillManifest] = None
    error: Optional[str] = None


class InstallManager:
    """
    技能安装管理器
    
    职责：
    - 安装技能到 registry
    - 写入持久化文件
    - 初始化生命周期状态
    """
    
    def __init__(self, registry_path: str = "skills/registry/skill_registry.json"):
        self.registry_path = registry_path
        self._ensure_registry()
    
    def _ensure_registry(self):
        """确保 registry 文件存在"""
        os.makedirs(os.path.dirname(self.registry_path) or ".", exist_ok=True)
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, 'w') as f:
                json.dump({"skills": [], "version": "1.0.0"}, f, indent=2)
    
    def _load_registry(self) -> Dict:
        """加载 registry"""
        with open(self.registry_path, 'r') as f:
            return json.load(f)
    
    def _save_registry(self, data: Dict):
        """保存 registry"""
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def install(
        self,
        skill_id: str,
        name: str,
        version: str = "1.0.0",
        description: str = "",
        category: str = "other",
        executor_type: str = "skill_md",
        entry_point: str = "",
        timeout_seconds: int = 60,
        tags: list = None,
        required_permissions: list = None,
        metadata: Dict = None
    ) -> InstallResult:
        """
        安装技能
        
        Args:
            skill_id: 技能 ID
            name: 技能名称
            version: 版本
            description: 描述
            category: 分类
            executor_type: 执行器类型
            entry_point: 入口点
            timeout_seconds: 超时时间
            tags: 标签
            required_permissions: 所需权限
            metadata: 元数据
        
        Returns:
            InstallResult
        """
        tags = tags or []
        required_permissions = required_permissions or []
        metadata = metadata or {}
        
        # 检查是否已存在
        registry = self._load_registry()
        existing = [s for s in registry.get("skills", []) if s.get("skill_id") == skill_id]
        
        if existing:
            return InstallResult(
                success=False,
                skill_id=skill_id,
                message=f"Skill {skill_id} already exists",
                error="duplicate_skill_id"
            )
        
        # 创建 manifest
        manifest = SkillManifest(
            skill_id=skill_id,
            name=name,
            version=version,
            description=description,
            category=SkillCategory(category),
            status=SkillStatus.STABLE,
            executor_type=executor_type,
            entry_point=entry_point,
            timeout_seconds=timeout_seconds,
            tags=tags,
            required_permissions=required_permissions,
            metadata=metadata
        )
        
        # 添加到 registry
        skill_data = {
            "skill_id": manifest.skill_id,
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "category": manifest.category.value,
            "status": manifest.status.value,
            "executor_type": manifest.executor_type,
            "entry_point": manifest.entry_point,
            "timeout_seconds": manifest.timeout_seconds,
            "tags": manifest.tags,
            "required_permissions": manifest.required_permissions,
            "metadata": manifest.metadata,
            "lifecycle": {
                "installed_at": datetime.now().isoformat(),
                "enabled": True,
                "deprecated": False,
                "deprecated_at": None,
                "deprecated_reason": None
            }
        }
        
        registry["skills"].append(skill_data)
        self._save_registry(registry)
        
        return InstallResult(
            success=True,
            skill_id=skill_id,
            message=f"Skill {skill_id} installed successfully",
            manifest=manifest
        )
    
    def install_from_manifest(self, manifest: SkillManifest) -> InstallResult:
        """从 manifest 安装"""
        return self.install(
            skill_id=manifest.skill_id,
            name=manifest.name,
            version=manifest.version,
            description=manifest.description,
            category=manifest.category.value,
            executor_type=manifest.executor_type,
            entry_point=manifest.entry_point,
            timeout_seconds=manifest.timeout_seconds,
            tags=manifest.tags,
            required_permissions=manifest.required_permissions,
            metadata=manifest.metadata
        )
    
    def uninstall(self, skill_id: str) -> bool:
        """卸载技能"""
        registry = self._load_registry()
        skills = registry.get("skills", [])
        
        for i, skill in enumerate(skills):
            if skill.get("skill_id") == skill_id:
                skills.pop(i)
                self._save_registry(registry)
                return True
        
        return False
    
    def is_installed(self, skill_id: str) -> bool:
        """检查是否已安装"""
        registry = self._load_registry()
        return any(s.get("skill_id") == skill_id for s in registry.get("skills", []))
    
    def get_installed_skills(self) -> list:
        """获取已安装技能列表"""
        registry = self._load_registry()
        return registry.get("skills", [])
