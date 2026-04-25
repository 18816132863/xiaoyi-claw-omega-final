#!/usr/bin/env python3
"""
NVIDIA API 适配器
将投机解码器连接到 NVIDIA DeepSeek API
"""

import os
import json
import aiohttp
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class NVIDIAConfig:
    """NVIDIA API 配置"""
    api_key: str
    base_url: str = "https://integrate.api.nvidia.com/v1"
    
    @classmethod
    def from_env(cls) -> "NVIDIAConfig":
        """从环境变量加载配置"""
        return cls(
            api_key=os.environ.get("NVIDIA_API_KEY", ""),
            base_url=os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
        )


class NVIDIAAPIClient:
    """NVIDIA API 客户端"""
    
    def __init__(self, config: Optional[NVIDIAConfig] = None):
        """
        初始化客户端
        
        Args:
            config: NVIDIA API 配置
        """
        self.config = config or NVIDIAConfig.from_env()
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """进入上下文"""
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.session:
            await self.session.close()
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 100,
        temperature: float = 0.0,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        调用聊天补全 API
        
        Args:
            model: 模型名称
            messages: 消息列表
            max_tokens: 最大 token 数
            temperature: 温度参数
            stream: 是否流式输出
        
        Returns:
            Dict[str, Any]: API 响应
        """
        url = f"{self.config.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        async with self.session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()
    
    async def generate_tokens(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 10,
        temperature: float = 0.0
    ) -> List[str]:
        """
        生成 token 列表
        
        Args:
            model: 模型名称
            prompt: 输入提示
            max_tokens: 最大 token 数
            temperature: 温度参数
        
        Returns:
            List[str]: 生成的 token 列表
        """
        messages = [{"role": "user", "content": prompt}]
        
        response = await self.chat_completion(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # 提取生成的文本
        content = response["choices"][0]["message"]["content"]
        
        # 简单分词 (实际应用中应使用 tokenizer)
        tokens = list(content)
        
        return tokens


class NVIDIADraftModel:
    """NVIDIA 草稿模型"""
    
    def __init__(
        self,
        model_name: str = "deepseek-ai/deepseek-v4-flash",
        max_draft_tokens: int = 4
    ):
        """
        初始化草稿模型
        
        Args:
            model_name: 模型名称
            max_draft_tokens: 最大草稿 token 数
        """
        self.model_name = model_name
        self.max_draft_tokens = max_draft_tokens
        self.client = NVIDIAAPIClient()
    
    async def generate_draft(
        self,
        prompt: str,
        context: Optional[str] = None,
        num_tokens: Optional[int] = None
    ) -> List[Any]:
        """
        生成草稿 token
        
        Args:
            prompt: 输入提示
            context: 上下文
            num_tokens: 生成 token 数
        
        Returns:
            List: 草稿 token 列表
        """
        num_tokens = num_tokens or self.max_draft_tokens
        
        full_prompt = f"{context}\n{prompt}" if context else prompt
        
        async with self.client as client:
            tokens = await client.generate_tokens(
                model=self.model_name,
                prompt=full_prompt,
                max_tokens=num_tokens
            )
        
        # 包装为 DraftToken 格式
        from .speculative_decoder import DraftToken
        
        draft_tokens = []
        for i, token in enumerate(tokens[:num_tokens]):
            draft_tokens.append(DraftToken(
                token=token,
                token_id=i,
                probability=0.9 - i * 0.1,
                position=i
            ))
        
        return draft_tokens


class NVIDIATargetModel:
    """NVIDIA 目标模型"""
    
    def __init__(
        self,
        model_name: str = "deepseek-ai/deepseek-v4-pro"
    ):
        """
        初始化目标模型
        
        Args:
            model_name: 模型名称
        """
        self.model_name = model_name
        self.client = NVIDIAAPIClient()
    
    async def verify_tokens(
        self,
        prompt: str,
        draft_tokens: List[Any],
        context: Optional[str] = None
    ):
        """
        验证草稿 token
        
        Args:
            prompt: 输入提示
            draft_tokens: 草稿 token 列表
            context: 上下文
        
        Returns:
            Tuple: 验证结果和接受的 token
        """
        from .speculative_decoder import VerificationResult
        
        full_prompt = f"{context}\n{prompt}" if context else prompt
        
        # 使用目标模型生成相同数量的 token
        async with self.client as client:
            target_tokens = await client.generate_tokens(
                model=self.model_name,
                prompt=full_prompt,
                max_tokens=len(draft_tokens)
            )
        
        # 比较 token
        accepted_tokens = []
        for i, (draft, target) in enumerate(zip(draft_tokens, target_tokens)):
            if draft.token == target:
                accepted_tokens.append(draft.token)
            else:
                break
        
        if len(accepted_tokens) == len(draft_tokens):
            result = VerificationResult.ACCEPTED
        elif len(accepted_tokens) == 0:
            result = VerificationResult.REJECTED
        else:
            result = VerificationResult.PARTIAL
        
        return result, accepted_tokens


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("NVIDIA API 适配器测试")
        print("=" * 60)
        
        # 测试配置
        config = NVIDIAConfig.from_env()
        print(f"API Key: {config.api_key[:10]}...")
        print(f"Base URL: {config.base_url}")
    
    asyncio.run(test())
