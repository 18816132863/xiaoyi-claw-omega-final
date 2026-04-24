"""
Skill Package Loader
技能包加载器
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json
import threading
from pathlib import Path


def _get_project_root() -> Path:
    """动态获取项目根目录"""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "core").exists() and (parent / "infrastructure").exists():
            return parent
    return current.parents[4]


@dataclass
class SkillPackage:
    """技能包"""
    package_id: str
    name: str
    version: str
    path: Path
    manifest: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: str = "active"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "package_id": self.package_id,
            "name": self.name,
            "version": self.version,
            "path": str(self.path),
            "manifest": self.manifest,
            "dependencies": self.dependencies,
            "status": self.status
        }


@dataclass
class LoadResult:
    """加载结果"""
    success: bool
    package: Optional[SkillPackage]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class SkillPackageLoader:
    """技能包加载器"""
    
    def __init__(self, skills_dir: Optional[Path] = None):
        if skills_dir is None:
            project_root = _get_project_root()
            skills_dir = project_root / "skills"
        
        self.skills_dir = Path(skills_dir)
        self._packages: Dict[str, SkillPackage] = {}
        self._lock = threading.RLock()
        self._scan()
    
    def _scan(self):
        """扫描技能目录"""
        if not self.skills_dir.exists():
            return
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    self._load_package(skill_dir)
    
    def _load_package(self, skill_dir: Path):
        """加载技能包"""
        skill_id = skill_dir.name
        skill_md = skill_dir / "SKILL.md"
        
        # 解析 SKILL.md 获取基本信息
        name = skill_id
        version = "1.0.0"
        dependencies = []
        
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()
                # 简单解析
                for line in content.split('\n'):
                    if line.startswith('# '):
                        name = line[2:].strip()
                    elif 'version' in line.lower():
                        parts = line.split(':')
                        if len(parts) > 1:
                            version = parts[1].strip()
        except Exception:
            pass
        
        package = SkillPackage(
            package_id=skill_id,
            name=name,
            version=version,
            path=skill_dir,
            dependencies=dependencies
        )
        
        self._packages[skill_id] = package
    
    def load(self, skill_id: str) -> Optional[SkillPackage]:
        """加载指定技能包"""
        return self._packages.get(skill_id)
    
    def load_from_path(self, skill_dir: Path) -> LoadResult:
        """从路径加载技能包"""
        try:
            self._load_package(skill_dir)
            package = self._packages.get(skill_dir.name)
            return LoadResult(
                success=True,
                package=package,
                warnings=[],
                errors=[]
            )
        except Exception as e:
            return LoadResult(
                success=False,
                package=None,
                warnings=[],
                errors=[str(e)]
            )
    
    def list_all(self) -> List[SkillPackage]:
        """列出所有技能包"""
        return list(self._packages.values())
    
    def reload(self):
        """重新扫描"""
        with self._lock:
            self._packages.clear()
            self._scan()
