"""
Skill Package Loader - 技能包加载器
负责读取和校验 skill package
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import re


@dataclass
class SkillPackage:
    """技能包"""
    skill_id: str
    name: str
    version: str
    description: str
    entry_point: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    status: str = "active"
    health_status: str = "unknown"
    dependencies: List[Dict[str, Any]] = field(default_factory=list)
    compatible_profiles: List[str] = field(default_factory=lambda: ["default"])
    compatible_runtime_versions: List[str] = field(default_factory=list)
    author: Optional[str] = None
    license: Optional[str] = None
    homepage: Optional[str] = None
    repository: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    timeout_ms: int = 30000
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    rate_limit: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    package_path: Optional[str] = None
    loaded_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "entry_point": self.entry_point,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "status": self.status,
            "health_status": self.health_status,
            "dependencies": self.dependencies,
            "compatible_profiles": self.compatible_profiles,
            "compatible_runtime_versions": self.compatible_runtime_versions,
            "author": self.author,
            "license": self.license,
            "homepage": self.homepage,
            "repository": self.repository,
            "keywords": self.keywords,
            "category": self.category,
            "tags": self.tags,
            "timeout_ms": self.timeout_ms,
            "retry_policy": self.retry_policy,
            "rate_limit": self.rate_limit,
            "metadata": self.metadata,
            "package_path": self.package_path,
            "loaded_at": self.loaded_at
        }


@dataclass
class LoadResult:
    """加载结果"""
    success: bool
    package: Optional[SkillPackage] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "package": self.package.to_dict() if self.package else None,
            "errors": self.errors,
            "warnings": self.warnings
        }


class SkillPackageLoader:
    """
    技能包加载器

    职责：
    - 读取 skill package 文件
    - 校验 package 结构
    - 验证版本格式
    - 检查必需字段
    """

    def __init__(self, schema_path: str = None):
        self.schema_path = schema_path or "skills/contracts/skill_package.schema.json"
        self._schema: Optional[Dict] = None
        self._loaded_packages: Dict[str, SkillPackage] = {}

    def load(self, package_path: str) -> LoadResult:
        """
        加载技能包

        Args:
            package_path: package.json 文件路径或包含 package.json 的目录

        Returns:
            LoadResult
        """
        errors = []
        warnings = []

        # 确定文件路径
        if os.path.isdir(package_path):
            package_file = os.path.join(package_path, "package.json")
        else:
            package_file = package_path

        if not os.path.exists(package_file):
            return LoadResult(
                success=False,
                errors=[f"Package file not found: {package_file}"]
            )

        # 读取文件
        try:
            with open(package_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return LoadResult(
                success=False,
                errors=[f"Invalid JSON: {e}"]
            )
        except Exception as e:
            return LoadResult(
                success=False,
                errors=[f"Failed to read file: {e}"]
            )

        # 校验必需字段
        required_fields = [
            "skill_id", "name", "version", "description",
            "entry_point", "input_schema", "output_schema"
        ]

        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")

        if errors:
            return LoadResult(success=False, errors=errors)

        # 验证 skill_id 格式
        if not re.match(r'^[a-z0-9_]+$', data["skill_id"]):
            errors.append(f"Invalid skill_id format: {data['skill_id']}")

        # 验证版本格式
        if not re.match(r'^\d+\.\d+\.\d+(-[a-z0-9]+)?$', data["version"]):
            errors.append(f"Invalid version format: {data['version']}")

        # 验证状态
        valid_statuses = ["draft", "active", "deprecated", "retired"]
        if data.get("status", "active") not in valid_statuses:
            errors.append(f"Invalid status: {data.get('status')}")

        # 验证健康状态
        valid_health = ["healthy", "degraded", "unhealthy", "unknown"]
        if data.get("health_status", "unknown") not in valid_health:
            warnings.append(f"Invalid health_status: {data.get('health_status')}, using 'unknown'")
            data["health_status"] = "unknown"

        if errors:
            return LoadResult(success=False, errors=errors)

        # 创建 SkillPackage
        package = SkillPackage(
            skill_id=data["skill_id"],
            name=data["name"],
            version=data["version"],
            description=data["description"],
            entry_point=data["entry_point"],
            input_schema=data["input_schema"],
            output_schema=data["output_schema"],
            status=data.get("status", "active"),
            health_status=data.get("health_status", "unknown"),
            dependencies=data.get("dependencies", []),
            compatible_profiles=data.get("compatible_profiles", ["default"]),
            compatible_runtime_versions=data.get("compatible_runtime_versions", []),
            author=data.get("author"),
            license=data.get("license"),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
            keywords=data.get("keywords", []),
            category=data.get("category"),
            tags=data.get("tags", []),
            timeout_ms=data.get("timeout_ms", 30000),
            retry_policy=data.get("retry_policy", {}),
            rate_limit=data.get("rate_limit", {}),
            metadata=data.get("metadata", {}),
            package_path=os.path.dirname(package_file),
            loaded_at=datetime.now().isoformat()
        )

        # 缓存
        cache_key = f"{package.skill_id}@{package.version}"
        self._loaded_packages[cache_key] = package

        return LoadResult(
            success=True,
            package=package,
            warnings=warnings
        )

    def load_directory(self, skills_dir: str) -> Dict[str, LoadResult]:
        """
        加载目录下所有技能包

        Args:
            skills_dir: 技能目录

        Returns:
            Dict[skill_id, LoadResult]
        """
        results = {}

        if not os.path.isdir(skills_dir):
            return results

        for item in os.listdir(skills_dir):
            item_path = os.path.join(skills_dir, item)
            if os.path.isdir(item_path):
                package_file = os.path.join(item_path, "package.json")
                if os.path.exists(package_file):
                    result = self.load(package_file)
                    if result.success and result.package:
                        results[result.package.skill_id] = result

        return results

    def get(self, skill_id: str, version: str = None) -> Optional[SkillPackage]:
        """
        获取已加载的技能包

        Args:
            skill_id: 技能 ID
            version: 版本（可选，默认最新）

        Returns:
            SkillPackage or None
        """
        if version:
            cache_key = f"{skill_id}@{version}"
            return self._loaded_packages.get(cache_key)

        # 获取最新版本
        matching = [
            (k, p) for k, p in self._loaded_packages.items()
            if p.skill_id == skill_id
        ]

        if not matching:
            return None

        # 按版本排序，返回最新
        def version_key(item):
            v = item[1].version
            parts = v.split('-')[0].split('.')
            return tuple(int(p) for p in parts)

        matching.sort(key=version_key, reverse=True)
        return matching[0][1]

    def list_loaded(self) -> List[SkillPackage]:
        """列出所有已加载的技能包"""
        return list(self._loaded_packages.values())

    def clear_cache(self):
        """清空缓存"""
        self._loaded_packages.clear()


# 全局单例
_skill_package_loader = None


def get_skill_package_loader() -> SkillPackageLoader:
    """获取技能包加载器单例"""
    global _skill_package_loader
    if _skill_package_loader is None:
        _skill_package_loader = SkillPackageLoader()
    return _skill_package_loader
