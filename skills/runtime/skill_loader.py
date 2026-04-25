"""
技能加载器

负责加载和初始化技能
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import importlib.util


class SkillLoader:
    """技能加载器"""
    
    def __init__(self, skills_dir: Path = None):
        self.skills_dir = skills_dir or Path("skills")
        self.loaded_skills: Dict[str, Any] = {}
    
    def load_skill(self, skill_id: str) -> Optional[Any]:
        """加载单个技能"""
        skill_path = self.skills_dir / skill_id
        
        if not skill_path.exists():
            return None
        
        # 查找入口文件
        entry_files = ["skill.py", "main.py", "__init__.py"]
        entry_file = None
        
        for ef in entry_files:
            if (skill_path / ef).exists():
                entry_file = skill_path / ef
                break
        
        if not entry_file:
            return None
        
        # 动态加载
        try:
            spec = importlib.util.spec_from_file_location(skill_id, entry_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.loaded_skills[skill_id] = module
                return module
        except Exception as e:
            print(f"加载技能 {skill_id} 失败: {e}")
        
        return None
    
    def load_all(self) -> Dict[str, Any]:
        """加载所有技能"""
        if not self.skills_dir.exists():
            return {}
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                self.load_skill(skill_dir.name)
        
        return self.loaded_skills
    
    def unload_skill(self, skill_id: str) -> bool:
        """卸载技能"""
        if skill_id in self.loaded_skills:
            del self.loaded_skills[skill_id]
            return True
        return False
    
    def reload_skill(self, skill_id: str) -> Optional[Any]:
        """重新加载技能"""
        self.unload_skill(skill_id)
        return self.load_skill(skill_id)
    
    def get_loaded_skills(self) -> List[str]:
        """获取已加载的技能列表"""
        return list(self.loaded_skills.keys())


__all__ = ["SkillLoader"]
