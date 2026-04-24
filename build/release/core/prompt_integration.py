#!/usr/bin/env python3
"""
提示词与架构集成 - V4.3.2
唯一真源：只读取 core/ 目录

V4.3.2 改进：
- 停止塞代码片段（含 2000 字截断）
- 改塞结构化摘要：职责、输入、输出、边界、禁止事项
- 大幅降低 Token 消耗
"""

import os
import sys
import re
import json
from typing import Dict, Any, Optional, List
from pathlib import Path

# ============================================================
# 路径解析 - 统一规则
# ============================================================

def get_project_root() -> Path:
    """
    获取项目根目录 - 统一规则
    1. 环境变量优先
    2. 自动发现（向上查找 core/ARCHITECTURE.md）
    3. 相对路径回退
    """
    # 1. 环境变量优先
    env_root = os.environ.get('OPENCLAW_WORKSPACE')
    if env_root and Path(env_root).exists():
        return Path(env_root)
    
    # 2. 自动发现
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    
    # 3. 相对路径回退
    return Path(__file__).resolve().parent.parent

# 全局项目根
PROJECT_ROOT = get_project_root()
CORE_DIR = PROJECT_ROOT / 'core'

# ============================================================
# V4.3.2: 结构化摘要定义
# ============================================================

LAYER_SUMMARIES = {
    1: {
        "name": "Core",
        "role": "核心认知、身份、规则",
        "inputs": ["用户输入", "会话上下文"],
        "outputs": ["身份确认", "规则约束"],
        "boundaries": ["不执行外部操作", "不修改系统状态"],
        "forbidden": ["绕过安全检查", "直接调用 L6 工具"]
    },
    2: {
        "name": "Memory Context",
        "role": "记忆上下文、知识库",
        "inputs": ["查询关键词", "时间范围"],
        "outputs": ["记忆片段", "知识检索结果"],
        "boundaries": ["只读操作", "不修改记忆结构"],
        "forbidden": ["删除记忆", "修改历史"]
    },
    3: {
        "name": "Orchestration",
        "role": "任务编排、工作流",
        "inputs": ["用户意图", "任务列表"],
        "outputs": ["子任务", "执行计划"],
        "boundaries": ["不直接执行", "只做编排"],
        "forbidden": ["跳过依赖检查", "无限递归"]
    },
    4: {
        "name": "Execution",
        "role": "能力执行、技能网关",
        "inputs": ["技能名称", "执行参数"],
        "outputs": ["执行结果", "错误码"],
        "boundaries": ["受 L5 监督", "超时可中断"],
        "forbidden": ["绕过网关", "未授权操作"]
    },
    5: {
        "name": "Governance",
        "role": "稳定治理、安全审计",
        "inputs": ["操作请求", "权限检查"],
        "outputs": ["授权结果", "审计日志"],
        "boundaries": ["只做检查", "不执行业务"],
        "forbidden": ["绕过验证", "忽略错误"]
    },
    6: {
        "name": "Infrastructure",
        "role": "基础设施、工具链",
        "inputs": ["工具调用", "资源请求"],
        "outputs": ["工具结果", "资源状态"],
        "boundaries": ["受 L5 控制", "资源受限"],
        "forbidden": ["无限资源", "绕过限流"]
    }
}

CORE_FILES = [
    'AGENTS.md',
    'TOOLS.md', 
    'IDENTITY.md',
    'SOUL.md',
    'USER.md',
    'HEARTBEAT.md'
]

class PromptOrchestrator:
    """提示词编排器 - V4.3.2: 结构化摘要"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.core_dir = CORE_DIR
        self.loaded_layers: Dict[int, str] = {}
    
    def _read_core_file(self, filename: str) -> str:
        """读取核心文件 - 只从 core/ 目录读取"""
        filepath = self.core_dir / filename
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
        return ""
    
    def load_layer(self, layer: int) -> str:
        """按层加载提示词 - V4.3.2: 返回结构化摘要"""
        if layer in self.loaded_layers:
            return self.loaded_layers[layer]
        
        # V4.3.2: 使用结构化摘要
        summary = LAYER_SUMMARIES.get(layer)
        if summary:
            content = self._format_summary(summary)
        else:
            content = ""
        
        self.loaded_layers[layer] = content
        return content
    
    def _format_summary(self, summary: Dict) -> str:
        """V4.3.2: 格式化摘要为提示词"""
        lines = [
            f"## {summary['name']} 层",
            f"职责: {summary['role']}",
            f"输入: {', '.join(summary['inputs'])}",
            f"输出: {', '.join(summary['outputs'])}",
            f"边界: {', '.join(summary['boundaries'])}",
            f"禁止: {', '.join(summary['forbidden'])}"
        ]
        return "\n".join(lines)
    
    def _load_core(self) -> str:
        """加载核心层 - 只读取 core/ 目录"""
        parts = []
        
        for filename in CORE_FILES:
            content = self._read_core_file(filename)
            if content:
                # 移除兼容副本标记
                content = re.sub(r'^# 兼容副本.*\n', '', content)
                # V4.3.2: 只保留前 500 字符（身份定义）
                content = content[:500]
                parts.append(content)
        
        return "\n\n".join(parts)
    
    def load_minimal(self) -> str:
        """加载最小提示词 - V4.3.2: 只加载 L1 摘要"""
        core = self._load_core()
        l1_summary = self.load_layer(1)
        return f"{core}\n\n{l1_summary}"
    
    def load_full(self) -> str:
        """加载完整提示词 - V4.3.2: 所有层摘要"""
        all_parts = [self._load_core()]
        for layer in range(1, 7):
            content = self.load_layer(layer)
            if content:
                all_parts.append(content)
        return "\n\n".join(all_parts)
    
    def get_token_estimate(self, layer: int = None) -> int:
        """估算 Token - V4.3.2: 更精确估算"""
        if layer:
            content = self.load_layer(layer)
        else:
            content = self.load_minimal()
        
        chinese = len(re.findall(r'[\u4e00-\u9fff]', content))
        other = len(content) - chinese
        return int(chinese / 2 + other / 4)
    
    def clear_cache(self):
        """清理缓存"""
        self.loaded_layers.clear()

# ============================================================
# 全局实例
# ============================================================

_orchestrator: Optional[PromptOrchestrator] = None

def get_prompt_orchestrator() -> PromptOrchestrator:
    """获取全局提示词编排器"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = PromptOrchestrator()
    return _orchestrator
