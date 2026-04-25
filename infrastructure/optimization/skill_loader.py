#!/usr/bin/env python3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
"""
技能延迟加载器
V2.7.0 - 2026-04-10
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

class SkillLoader:
    def __init__(self, skills_path: str):
        self.skills_path = Path(skills_path)
        self.cache: Dict[str, dict] = {}
        self.cache_timeout = 300  # 5分钟缓存
        self.cache_timestamps: Dict[str, float] = {}
        
    def get_skill_list(self) -> List[str]:
        """获取所有技能列表"""
        if not self.skills_path.exists():
            return []
        return [d.name for d in self.skills_path.iterdir() if d.is_dir()]
    
    def load_skill(self, skill_name: str, force: bool = False) -> Optional[dict]:
        """延迟加载技能"""
        # 检查缓存
        if not force and skill_name in self.cache:
            if time.time() - self.cache_timestamps.get(skill_name, 0) < self.cache_timeout:
                return self.cache[skill_name]
        
        skill_path = self.skills_path / skill_name
        if not skill_path.exists():
            return None
        
        skill_data = {
            "name": skill_name,
            "path": str(skill_path),
            "files": {},
            "metadata": {}
        }
        
        # 加载 SKILL.md
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            skill_data["metadata"]["skill_md"] = skill_md.read_text()[:2000]  # 只加载前2000字符
        
        # 加载 package.json
        package_json = skill_path / "package.json"
        if package_json.exists():
            try:
                skill_data["metadata"]["package"] = json.loads(package_json.read_text())
            except:
                pass
        
        # 记录文件列表（不加载内容）
        for file in skill_path.rglob("*"):
            if file.is_file():
                rel_path = file.relative_to(skill_path)
                skill_data["files"][str(rel_path)] = {
                    "size": file.stat().st_size,
                    "modified": file.stat().st_mtime
                }
        
        # 更新缓存
        self.cache[skill_name] = skill_data
        self.cache_timestamps[skill_name] = time.time()
        
        return skill_data
    
    def load_skill_file(self, skill_name: str, file_path: str) -> Optional[str]:
        """按需加载技能文件"""
        full_path = self.skills_path / skill_name / file_path
        if full_path.exists():
            return full_path.read_text()
        return None
    
    def preload_essential_skills(self, skills: List[str] = None):
        """预加载核心技能"""
        essential = skills or [
            "xiaoyi-web-search",
            "xiaoyi-image-search", 
            "find-skills",
            "skill-creator",
            "docx",
            "pdf",
            "pptx"
        ]
        
        for skill in essential:
            if skill in self.get_skill_list():
                self.load_skill(skill)
    
    def clear_cache(self):
        """清理缓存"""
        self.cache.clear()
        self.cache_timestamps.clear()

if __name__ == "__main__":
    loader = SkillLoader("str(PROJECT_ROOT)/skills")
    print(f"技能总数: {len(loader.get_skill_list())}")
    
    # 预加载核心技能
    loader.preload_essential_skills()
    print(f"已缓存: {len(loader.cache)} 个技能")
