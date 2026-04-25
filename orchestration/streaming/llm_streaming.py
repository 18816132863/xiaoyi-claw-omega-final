#!/usr/bin/env python3
"""
LLM 流式输出模块 (v5.0)
流式响应、SSE 支持、WebSocket 支持
"""

import json
import time
import asyncio
from typing import AsyncGenerator, Callable, Optional, Dict, Any, List


class StreamChunk:
    """
    流式响应块
    """
    
    def __init__(
        self,
        content: str,
        finish: bool = False,
        metadata: Optional[Dict] = None
    ):
        """
        初始化流式块
        
        Args:
            content: 内容
            finish: 是否结束
            metadata: 元数据
        """
        self.content = content
        self.finish = finish
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_sse(self) -> str:
        """
        转换为 SSE 格式
        
        Returns:
            str: SSE 格式字符串
        """
        data = {
            'content': self.content,
            'finish': self.finish,
            'timestamp': self.timestamp
        }
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    
    def to_json(self) -> str:
        """
        转换为 JSON 格式
        
        Returns:
            str: JSON 字符串
        """
        return json.dumps({
            'content': self.content,
            'finish': self.finish,
            'timestamp': self.timestamp
        }, ensure_ascii=False)


class LLMStreamer:
    """
    LLM 流式输出器
    """
    
    def __init__(
        self,
        llm_client: Any = None,
        chunk_size: int = 10,
        timeout: float = 30.0
    ):
        """
        初始化流式输出器
        
        Args:
            llm_client: LLM 客户端
            chunk_size: 块大小（字符数）
            timeout: 超时时间
        """
        self.llm_client = llm_client
        self.chunk_size = chunk_size
        self.timeout = timeout
        
        print(f"LLM 流式输出器初始化:")
        print(f"  块大小: {chunk_size} 字符")
        print(f"  超时: {timeout}s")
    
    async def stream(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        流式生成
        
        Args:
            prompt: 提示词
            max_tokens: 最大 token 数
            temperature: 温度
        
        Yields:
            StreamChunk: 流式块
        """
        # 简化实现：模拟流式输出
        # 实际实现应调用 LLM API 的流式接口
        
        # 模拟生成内容
        full_response = f"这是对 '{prompt[:30]}...' 的回答。这是一个模拟的流式响应，用于演示流式输出功能。在实际应用中，这里会调用真实的 LLM API 来生成内容。"
        
        # 分块输出
        for i in range(0, len(full_response), self.chunk_size):
            chunk_content = full_response[i:i + self.chunk_size]
            is_finish = i + self.chunk_size >= len(full_response)
            
            yield StreamChunk(
                content=chunk_content,
                finish=is_finish,
                metadata={'chunk_index': i // self.chunk_size}
            )
            
            # 模拟延迟
            await asyncio.sleep(0.05)
    
    async def stream_with_callback(
        self,
        prompt: str,
        callback: Callable[[StreamChunk], None],
        max_tokens: int = 500,
        temperature: float = 0.7
    ):
        """
        带回调的流式生成
        
        Args:
            prompt: 提示词
            callback: 回调函数
            max_tokens: 最大 token 数
            temperature: 温度
        """
        async for chunk in self.stream(prompt, max_tokens, temperature):
            callback(chunk)
    
    async def stream_to_list(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> List[StreamChunk]:
        """
        流式生成并收集到列表
        
        Args:
            prompt: 提示词
            max_tokens: 最大 token 数
            temperature: 温度
        
        Returns:
            List[StreamChunk]: 流式块列表
        """
        chunks = []
        async for chunk in self.stream(prompt, max_tokens, temperature):
            chunks.append(chunk)
        return chunks


class SSEServer:
    """
    SSE (Server-Sent Events) 服务器
    """
    
    def __init__(self, streamer: LLMStreamer):
        """
        初始化 SSE 服务器
        
        Args:
            streamer: 流式输出器
        """
        self.streamer = streamer
        self.connections = set()
    
    async def handle_request(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        处理 SSE 请求
        
        Args:
            prompt: 提示词
        
        Yields:
            str: SSE 格式数据
        """
        async for chunk in self.streamer.stream(prompt):
            yield chunk.to_sse()


class WebSocketHandler:
    """
    WebSocket 处理器
    """
    
    def __init__(self, streamer: LLMStreamer):
        """
        初始化 WebSocket 处理器
        
        Args:
            streamer: 流式输出器
        """
        self.streamer = streamer
    
    async def handle_message(self, message: str) -> AsyncGenerator[str, None]:
        """
        处理 WebSocket 消息
        
        Args:
            message: 消息内容
        
        Yields:
            str: JSON 格式数据
        """
        try:
            data = json.loads(message)
            prompt = data.get('prompt', '')
            
            async for chunk in self.streamer.stream(prompt):
                yield chunk.to_json()
        
        except json.JSONDecodeError:
            yield json.dumps({'error': 'Invalid JSON'})


if __name__ == "__main__":
    # 测试
    async def test():
        print("=== LLM 流式输出测试 ===")
        
        streamer = LLMStreamer(chunk_size=20)
        
        # 流式生成
        print("\n流式输出:")
        async for chunk in streamer.stream("介绍一下向量搜索"):
            print(chunk.content, end='', flush=True)
            if chunk.finish:
                print("\n[完成]")
        
        # 收集到列表
        print("\n收集到列表:")
        chunks = await streamer.stream_to_list("测试问题")
        print(f"共 {len(chunks)} 个块")
        
        # SSE 格式
        print("\nSSE 格式:")
        async for sse in SSEServer(streamer).handle_request("测试"):
            print(sse.strip())
            break  # 只打印第一个
    
    asyncio.run(test())
