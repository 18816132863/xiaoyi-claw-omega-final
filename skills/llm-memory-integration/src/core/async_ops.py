#!/usr/bin/env python3
"""
异步 I/O 优化模块 (v4.1)
异步向量搜索、异步 LLM 调用、并发请求处理
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

# 可选依赖：aiohttp
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    aiohttp = None
    HAS_AIOHTTP = False


class AsyncVectorSearch:
    """
    异步向量搜索
    """
    
    def __init__(self, vectors: np.ndarray, max_workers: int = 4):
        """
        初始化异步搜索器
        
        Args:
            vectors: 向量矩阵 (n, dim)
            max_workers: 最大工作线程数
        """
        self.vectors = vectors.astype(np.float32)
        self.vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def search(
        self,
        query: np.ndarray,
        top_k: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        异步搜索
        
        Args:
            query: 查询向量
            top_k: 返回数量
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: (索引, 得分)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._sync_search,
            query,
            top_k
        )
    
    def _sync_search(
        self,
        query: np.ndarray,
        top_k: int
    ) -> Tuple[np.ndarray, np.ndarray]:
        """同步搜索（在线程池中执行）"""
        query_norm = query / (np.linalg.norm(query) + 1e-10)
        scores = np.dot(self.vectors_norm, query_norm)
        
        if top_k >= len(scores):
            indices = np.argsort(scores)[::-1]
        else:
            indices = np.argpartition(scores, -top_k)[-top_k:]
            indices = indices[np.argsort(scores[indices])[::-1]]
        
        return indices, scores[indices]
    
    async def batch_search(
        self,
        queries: np.ndarray,
        top_k: int = 10
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        异步批量搜索
        
        Args:
            queries: 查询向量矩阵
            top_k: 每个查询返回的数量
        
        Returns:
            List[Tuple[np.ndarray, np.ndarray]]: 每个查询的结果
        """
        tasks = [self.search(query, top_k) for query in queries]
        return await asyncio.gather(*tasks)
    
    def close(self):
        """关闭线程池"""
        self.executor.shutdown(wait=True)


class AsyncLLMClient:
    """
    异步 LLM 客户端
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str = "gpt-4",
        max_concurrent: int = 10
    ):
        """
        初始化异步 LLM 客户端
        
        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型名称
            max_concurrent: 最大并发数
        """
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp 未安装，请运行: pip install aiohttp")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
    
    async def _get_session(self):
        """获取 HTTP 会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self.session
    
    async def complete(
        self,
        prompt: str,
        max_tokens: int = 150,
        temperature: float = 0.5
    ) -> str:
        """
        异步完成
        
        Args:
            prompt: 提示词
            max_tokens: 最大 token 数
            temperature: 温度
        
        Returns:
            str: 完成结果
        """
        async with self.semaphore:
            session = await self._get_session()
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                result = await response.json()
                return result['choices'][0]['message']['content']
    
    async def batch_complete(
        self,
        prompts: List[str],
        max_tokens: int = 150,
        temperature: float = 0.5
    ) -> List[str]:
        """
        异步批量完成
        
        Args:
            prompts: 提示词列表
            max_tokens: 最大 token 数
            temperature: 温度
        
        Returns:
            List[str]: 完成结果列表
        """
        tasks = [self.complete(prompt, max_tokens, temperature) for prompt in prompts]
        return await asyncio.gather(*tasks)
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()


class AsyncEmbeddingClient:
    """
    异步 Embedding 客户端
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str = "text-embedding-ada-002",
        max_concurrent: int = 10
    ):
        """
        初始化异步 Embedding 客户端
        
        Args:
            base_url: API 基础 URL
            api_key: API 密钥
            model: 模型名称
            max_concurrent: 最大并发数
        """
        if not HAS_AIOHTTP:
            raise ImportError("aiohttp 未安装，请运行: pip install aiohttp")
        
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
    
    async def _get_session(self):
        """获取 HTTP 会话"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self.session
    
    async def embed(self, text: str) -> np.ndarray:
        """
        异步获取 embedding
        
        Args:
            text: 文本
        
        Returns:
            np.ndarray: 向量
        """
        async with self.semaphore:
            session = await self._get_session()
            
            payload = {
                "model": self.model,
                "input": text
            }
            
            async with session.post(
                f"{self.base_url}/embeddings",
                json=payload
            ) as response:
                result = await response.json()
                return np.array(result['data'][0]['embedding'], dtype=np.float32)
    
    async def batch_embed(self, texts: List[str]) -> np.ndarray:
        """
        异步批量获取 embedding
        
        Args:
            texts: 文本列表
        
        Returns:
            np.ndarray: 向量矩阵
        """
        tasks = [self.embed(text) for text in texts]
        vectors = await asyncio.gather(*tasks)
        return np.array(vectors, dtype=np.float32)
    
    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()


class AsyncMemoryPipeline:
    """
    异步记忆管道
    整合向量搜索 + LLM 分析
    """
    
    def __init__(
        self,
        vectors: np.ndarray,
        llm_config: Optional[Dict] = None,
        embedding_config: Optional[Dict] = None
    ):
        """
        初始化异步记忆管道
        
        Args:
            vectors: 向量矩阵
            llm_config: LLM 配置
            embedding_config: Embedding 配置
        """
        self.vector_search = AsyncVectorSearch(vectors)
        
        self.llm_client = None
        self.embedding_client = None
        
        if llm_config:
            self.llm_client = AsyncLLMClient(
                base_url=llm_config.get('base_url', ''),
                api_key=llm_config.get('api_key', ''),
                model=llm_config.get('model', 'gpt-4')
            )
        
        if embedding_config:
            self.embedding_client = AsyncEmbeddingClient(
                base_url=embedding_config.get('base_url', ''),
                api_key=embedding_config.get('api_key', ''),
                model=embedding_config.get('model', 'text-embedding-ada-002')
            )
    
    async def search_and_analyze(
        self,
        query: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        异步搜索并分析
        
        Args:
            query: 查询文本
            top_k: 返回数量
        
        Returns:
            Dict: 搜索和分析结果
        """
        # 获取 query embedding
        if self.embedding_client:
            query_vector = await self.embedding_client.embed(query)
        else:
            # 使用随机向量（测试用）
            query_vector = np.random.randn(4096).astype(np.float32)
        
        # 向量搜索
        indices, scores = await self.vector_search.search(query_vector, top_k)
        
        # LLM 分析（可选）
        analysis = None
        if self.llm_client:
            prompt = f"分析以下搜索结果的相关性：\n查询：{query}\n结果数量：{len(indices)}"
            analysis = await self.llm_client.complete(prompt)
        
        return {
            'indices': indices,
            'scores': scores,
            'analysis': analysis
        }
    
    async def close(self):
        """关闭所有资源"""
        self.vector_search.close()
        if self.llm_client:
            await self.llm_client.close()
        if self.embedding_client:
            await self.embedding_client.close()


if __name__ == "__main__":
    # 测试
    async def test():
        print("=== 异步 I/O 测试 ===")
        
        dim = 4096
        n_vectors = 10000
        vectors = np.random.randn(n_vectors, dim).astype(np.float32)
        queries = np.random.randn(10, dim).astype(np.float32)
        
        # 异步向量搜索
        search = AsyncVectorSearch(vectors)
        
        start = time.time()
        results = await search.batch_search(queries, top_k=20)
        elapsed = time.time() - start
        print(f"异步批量搜索耗时: {elapsed*1000:.2f}ms")
        
        search.close()
    
    asyncio.run(test())
