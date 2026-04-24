"""Manifest 构建器 - V4.3.1

将 SKILL.md 转换为运行时 manifest，运行时只读 manifest。
"""

from typing import Dict, List, Any
from pathlib import Path
from infrastructure.path_resolver import get_project_root
import json
import re
from dataclasses import dataclass

@dataclass
class SkillManifest:
    """技能清单"""
    id: str
    name: str
    version: str
    description: str
    entry: str
    triggers: List[str]
    inputs: Dict[str, str]
    outputs: Dict[str, str]
    dependencies: List[str]

class ManifestBuilder:
    """Manifest 构建器"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.skills_dir = self.workspace / "skills"
        self.output_dir = self.workspace / "infrastructure/manifest"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def build_all(self) -> Dict[str, SkillManifest]:
        """构建所有技能的 manifest"""
        manifests = {}
        
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                manifest = self._build_one(skill_dir.name, skill_md)
                if manifest:
                    manifests[manifest.id] = manifest
        
        # 保存合并的 manifest
        output_file = self.output_dir / "skills_manifest.json"
        with open(output_file, "w") as f:
            json.dump({
                "version": "4.3.1",
                "count": len(manifests),
                "skills": {k: self._to_dict(v) for k, v in manifests.items()}
            }, f, indent=2, ensure_ascii=False)
        
        return manifests
    
    def _build_one(self, skill_id: str, skill_md: Path) -> SkillManifest:
        """构建单个 manifest"""
        content = skill_md.read_text()
        
        # 提取字段
        name = self._extract_field(content, "name") or skill_id
        version = self._extract_field(content, "version") or "1.0.0"
        description = self._extract_field(content, "description") or ""
        
        # 提取触发词
        triggers = self._extract_triggers(content)
        
        return SkillManifest(
            id=skill_id,
            name=name,
            version=version,
            description=description,
            entry=f"skills/{skill_id}/SKILL.md",
            triggers=triggers,
            inputs={},
            outputs={},
            dependencies=[]
        )
    
    def _extract_field(self, content: str, field: str) -> str:
        """提取字段"""
        pattern = rf"^{field}:\s*(.+)$"
        match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    def _extract_triggers(self, content: str) -> List[str]:
        """提取触发词"""
        triggers = []
        
        # 查找触发词部分
        if "触发词" in content:
            parts = content.split("触发词")
            if len(parts) > 1:
                trigger_section = parts[1].split("\n\n")[0]
                # 提取中文词汇
                triggers = re.findall(r'[\u4e00-\u9fa5]+', trigger_section)
        
        return triggers[:10]
    
    def _to_dict(self, manifest: SkillManifest) -> dict:
        """转换为字典"""
        return {
            "id": manifest.id,
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "entry": manifest.entry,
            "triggers": manifest.triggers
        }
