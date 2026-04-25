#!/usr/bin/env python3
"""
配置验证模块
确保配置正确性
"""

from dataclasses import dataclass
from typing import Optional, List
import json
from pathlib import Path

@dataclass
class EmbeddingConfig:
    """Embedding 配置"""
    api_url: str
    api_key: str
    model: str
    dimensions: int = 4096
    
    def validate(self):
        if not self.api_url:
            raise ValueError("❌ api_url 不能为空")
        if not self.api_url.startswith(('http://', 'https://')):
            raise ValueError("❌ api_url 必须以 http:// 或 https:// 开头")
        if not self.api_key or self.api_key == "YOUR_EMBEDDING_API_KEY":
            raise ValueError("❌ 请配置有效的 api_key")
        if not self.model:
            raise ValueError("❌ model 不能为空")
        if self.dimensions < 128 or self.dimensions > 8192:
            raise ValueError("❌ dimensions 必须在 128-8192 之间")

@dataclass
class LLMConfig:
    """LLM 配置"""
    api_url: str
    api_key: str
    model: str
    max_tokens: int = 150
    temperature: float = 0.5
    
    def validate(self):
        if not self.api_url:
            raise ValueError("❌ api_url 不能为空")
        if not self.api_url.startswith(('http://', 'https://')):
            raise ValueError("❌ api_url 必须以 http:// 或 https:// 开头")
        if not self.api_key or self.api_key == "YOUR_LLM_API_KEY":
            raise ValueError("❌ 请配置有效的 api_key")
        if not self.model:
            raise ValueError("❌ model 不能为空")
        if self.max_tokens < 1 or self.max_tokens > 32000:
            raise ValueError("❌ max_tokens 必须在 1-32000 之间")
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("❌ temperature 必须在 0-2 之间")

@dataclass
class MemoryConfig:
    """记忆配置"""
    max_memories_per_session: int = 50
    every_n_conversations: int = 3
    l1_idle_timeout_seconds: int = 30
    max_results: int = 12
    score_threshold: float = 0.2
    
    def validate(self):
        if self.max_memories_per_session < 1:
            raise ValueError("❌ max_memories_per_session 必须 >= 1")
        if self.every_n_conversations < 1:
            raise ValueError("❌ every_n_conversations 必须 >= 1")
        if self.max_results < 1 or self.max_results > 100:
            raise ValueError("❌ max_results 必须在 1-100 之间")
        if self.score_threshold < 0 or self.score_threshold > 1:
            raise ValueError("❌ score_threshold 必须在 0-1 之间")

def validate_config(config_path: Path) -> dict:
    """
    验证配置文件
    
    Returns:
        验证结果
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not config_path.exists():
        result["valid"] = False
        result["errors"].append(f"配置文件不存在: {config_path}")
        return result
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        result["valid"] = False
        result["errors"].append(f"配置文件格式错误: {e}")
        return result
    
    # 验证 Embedding 配置
    if "embedding" in config:
        try:
            emb = config["embedding"]
            emb_config = EmbeddingConfig(
                api_url=emb.get("base_url", ""),
                api_key=emb.get("api_key", ""),
                model=emb.get("model", ""),
                dimensions=emb.get("dimensions", 4096)
            )
            emb_config.validate()
        except ValueError as e:
            result["errors"].append(str(e))
    
    # 验证 LLM 配置
    if "llm" in config:
        try:
            llm = config["llm"]
            llm_config = LLMConfig(
                api_url=llm.get("base_url", ""),
                api_key=llm.get("api_key", ""),
                model=llm.get("model", ""),
                max_tokens=llm.get("max_tokens", 150),
                temperature=llm.get("temperature", 0.5)
            )
            llm_config.validate()
        except ValueError as e:
            result["errors"].append(str(e))
    
    # 验证 Memory 配置
    if "memory" in config:
        try:
            mem = config["memory"]
            mem_config = MemoryConfig(
                max_memories_per_session=mem.get("max_memories_per_session", 50),
                every_n_conversations=mem.get("every_n_conversations", 3),
                l1_idle_timeout_seconds=mem.get("l1_idle_timeout_seconds", 30),
                max_results=mem.get("max_results", 12),
                score_threshold=mem.get("score_threshold", 0.2)
            )
            mem_config.validate()
        except ValueError as e:
            result["errors"].append(str(e))
    
    result["valid"] = len(result["errors"]) == 0
    return result
