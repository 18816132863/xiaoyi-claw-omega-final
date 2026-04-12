#!/usr/bin/env python3
"""
动态提示词系统（安全加固版）
V2.8.1 - 2026-04-10

安全加固：
1. 路径白名单机制 - 只允许读取指定目录下的文件
2. 敏感内容过滤 - 过滤密钥、令牌等敏感信息
3. 文件大小限制 - 防止读取过大文件
"""

import os
import re
from typing import Dict, Any, Optional, List
from pathlib import Path
from string import Template

class SecurityConfig:
    """安全配置"""
    
    # 允许读取的目录白名单（相对路径）
    ALLOWED_DIRS = [
        "skills",
        "core",
        "memory",
        "templates",
    ]
    
    # 允许读取的文件白名单
    ALLOWED_FILES = [
        "AGENTS.md",
        "SOUL.md",
        "TOOLS.md",
        "USER.md",
        "MEMORY.md",
    ]
    
    # 敏感信息正则
    SENSITIVE_PATTERNS = [
        r'(?i)(api[_-]?key|token|secret|password|passwd|pwd)\s*[=:]\s*["\']?[\w\-]{10,}["\']?',
        r'(?i)(bearer\s+[\w\-\.]+)',
        r'(?i)(ghp_[a-zA-Z0-9]{36})',
        r'(?i)(sk-[a-zA-Z0-9]{48})',
        r'(?i)(clh_[a-zA-Z0-9\-]{30,})',
        r'(?i)(["\'][\w\-]{32,}["\'])',  # 长字符串可能是密钥
    ]
    
    # 最大文件大小 (bytes)
    MAX_FILE_SIZE = 100 * 1024  # 100KB
    
    # 最大目录深度
    MAX_DEPTH = 3

class PathValidator:
    """路径验证器"""
    
    def __init__(self, workspace: Path):
        self.workspace = workspace.resolve()
        self.config = SecurityConfig()
    
    def is_safe_path(self, path: Path) -> tuple:
        """检查路径是否安全"""
        try:
            # 解析绝对路径
            abs_path = path.resolve()
            
            # 检查是否在工作空间内
            if not str(abs_path).startswith(str(self.workspace)):
                return False, "路径不在工作空间内"
            
            # 检查路径深度
            rel_path = abs_path.relative_to(self.workspace)
            depth = len(rel_path.parts)
            if depth > self.config.MAX_DEPTH:
                return False, f"路径深度超过限制: {depth} > {self.config.MAX_DEPTH}"
            
            # 检查是否在白名单目录
            if rel_path.parts:
                first_dir = rel_path.parts[0]
                if first_dir not in self.config.ALLOWED_DIRS:
                    # 检查是否是白名单文件
                    if rel_path.name not in self.config.ALLOWED_FILES:
                        return False, f"目录不在白名单内: {first_dir}"
            
            return True, "路径安全"
        
        except Exception as e:
            return False, f"路径验证失败: {e}"
    
    def is_safe_file(self, path: Path) -> tuple:
        """检查文件是否安全可读"""
        # 先检查路径
        safe, msg = self.is_safe_path(path)
        if not safe:
            return False, msg
        
        # 检查文件大小
        if path.exists() and path.is_file():
            size = path.stat().st_size
            if size > self.config.MAX_FILE_SIZE:
                return False, f"文件过大: {size} > {self.config.MAX_FILE_SIZE}"
        
        return True, "文件安全"

class ContentSanitizer:
    """内容脱敏器"""
    
    def __init__(self):
        self.config = SecurityConfig()
    
    def sanitize(self, content: str) -> str:
        """脱敏敏感信息"""
        for pattern in self.config.SENSITIVE_PATTERNS:
            content = re.sub(pattern, '[REDACTED]', content)
        return content
    
    def sanitize_dict(self, data: Dict) -> Dict:
        """脱敏字典中的敏感信息"""
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.sanitize(value)
            elif isinstance(value, dict):
                result[key] = self.sanitize_dict(value)
            else:
                result[key] = value
        return result

class DynamicPromptBuilder:
    """动态提示词构建器（安全加固版）"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.variables: Dict[str, Any] = {}
        self.templates: Dict[str, str] = {}
        self.validator = PathValidator(self.workspace)
        self.sanitizer = ContentSanitizer()
    
    def set_variable(self, name: str, value: Any):
        """设置变量（自动脱敏）"""
        if isinstance(value, str):
            value = self.sanitizer.sanitize(value)
        elif isinstance(value, dict):
            value = self.sanitizer.sanitize_dict(value)
        self.variables[name] = value
    
    def load_template(self, name: str, path: str):
        """加载模板文件（安全检查）"""
        template_path = self.workspace / path
        
        # 安全检查
        safe, msg = self.validator.is_safe_file(template_path)
        if not safe:
            return  # 静默失败，不抛出异常
        
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            self.templates[name] = self.sanitizer.sanitize(content)
    
    def build(self, template_name: str = None, template_content: str = None,
              extra_vars: Dict[str, Any] = None) -> str:
        """构建提示词"""
        if template_content:
            template = self.sanitizer.sanitize(template_content)
        elif template_name and template_name in self.templates:
            template = self.templates[template_name]
        else:
            return ""
        
        all_vars = {**self.variables}
        if extra_vars:
            all_vars.update(self.sanitizer.sanitize_dict(extra_vars))
        
        result = template
        for key, value in all_vars.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        
        return result
    
    def build_from_file(self, path: str, variables: Dict[str, Any] = None) -> str:
        """从文件构建（安全检查）"""
        file_path = self.workspace / path
        
        safe, msg = self.validator.is_safe_file(file_path)
        if not safe:
            return ""
        
        if not file_path.exists():
            return ""
        
        template = file_path.read_text(encoding='utf-8')
        return self.build(template_content=template, extra_vars=variables)

class SystemPromptManager:
    """系统提示词管理器（安全加固版）"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.builder = DynamicPromptBuilder(workspace)
        self.validator = PathValidator(self.workspace)
        self.sanitizer = ContentSanitizer()
        
        self._init_default_variables()
    
    def _init_default_variables(self):
        """初始化默认变量"""
        from datetime import datetime
        
        self.builder.set_variable("date", datetime.now().strftime("%Y-%m-%d"))
        self.builder.set_variable("time", datetime.now().strftime("%H:%M:%S"))
        # 不暴露完整工作空间路径
        self.builder.set_variable("workspace", "[WORKSPACE]")
    
    def _safe_read_file(self, path: Path) -> str:
        """安全读取文件"""
        safe, msg = self.validator.is_safe_file(path)
        if not safe:
            return ""
        
        if not path.exists():
            return ""
        
        content = path.read_text(encoding='utf-8')
        return self.sanitizer.sanitize(content)
    
    def get_startup_prompt(self) -> str:
        """获取启动提示词"""
        prompt_parts = []
        
        # 只读取白名单文件
        for filename in SecurityConfig.ALLOWED_FILES:
            file_path = self.workspace / filename
            content = self._safe_read_file(file_path)
            if content:
                prompt_parts.append(content)
        
        return "\n".join(prompt_parts)
    
    def get_memory_prompt(self) -> str:
        """获取记忆提示词"""
        memory_parts = []
        
        # 只读取 memory 目录下的文件
        memory_dir = self.workspace / "memory"
        if memory_dir.exists():
            for mem_file in memory_dir.glob("*.md"):
                content = self._safe_read_file(mem_file)
                if content:
                    memory_parts.append(f"## {mem_file.stem}\n{content}")
        
        if memory_parts:
            return "\n\n".join(memory_parts)
        return ""
    
    def get_skill_prompt(self, skill_name: str) -> str:
        """获取技能提示词"""
        skill_dir = self.workspace / "skills" / skill_name
        
        # 安全检查
        safe, msg = self.validator.is_safe_path(skill_dir)
        if not safe:
            return ""
        
        if not skill_dir.exists():
            return ""
        
        parts = []
        
        skill_file = skill_dir / "SKILL.md"
        content = self._safe_read_file(skill_file)
        if content:
            parts.append(content)
        
        return "\n".join(parts)
    
    def update_variable(self, name: str, value: Any):
        """更新变量"""
        self.builder.set_variable(name, value)
    
    def get_token_estimate(self) -> int:
        """估算 Token 数"""
        prompt = self.get_startup_prompt()
        chinese = len(re.findall(r'[\u4e00-\u9fff]', prompt))
        other = len(prompt) - chinese
        return int(chinese / 2 + other / 4)

# 全局实例
_prompt_manager: Optional[SystemPromptManager] = None

def get_prompt_manager() -> SystemPromptManager:
    """获取全局提示词管理器"""
    global _prompt_manager
    if _prompt_manager is None:
        from infrastructure.path_resolver import get_project_root
        _prompt_manager = SystemPromptManager(str(get_project_root()))
    return _prompt_manager


# ============================================================
# 引导模块集成
# ============================================================

def get_guide_prompt() -> str:
    """获取引导提示词"""
    try:
        from guide.assistant_guide import get_guide
        guide = get_guide()
        return guide.get_quick_reference()
    except Exception:
        return ""

# 在系统提示词中包含引导信息
def enhance_prompt_with_guide(base_prompt: str) -> str:
    """在基础提示词中添加引导信息"""
    guide_prompt = get_guide_prompt()
    if guide_prompt:
        return f"{base_prompt}\n\n---\n{guide_prompt}"
    return base_prompt
