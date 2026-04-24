#!/usr/bin/env python3
"""
联网辅助功能优化引擎 V2
目标：搜索 < 50ms，网页抓取 < 100ms
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib
import time
import re
from urllib.parse import urlparse

class SearchIntent(Enum):
    REALTIME = "realtime"
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    NEWS = "news"
    SHOPPING = "shopping"
    GENERAL = "general"

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str
    score: float = 0.0

@dataclass
class ExtractedContent:
    title: str
    content: str
    url: str
    content_type: str
    extraction_time_ms: float

# ============ 搜索引擎路由 ============

class IntentRouter:
    """意图路由 - 按意图选择搜索引擎"""
    
    ENGINE_MAP = {
        SearchIntent.REALTIME: ["google", "bing"],
        SearchIntent.TECHNICAL: ["github", "stackoverflow"],
        SearchIntent.ACADEMIC: ["arxiv", "scholar"],
        SearchIntent.NEWS: ["google_news", "reddit"],
        SearchIntent.SHOPPING: ["amazon", "shopping"],
        SearchIntent.GENERAL: ["google", "bing"],
    }
    
    def route(self, intent: SearchIntent) -> List[str]:
        return self.ENGINE_MAP.get(intent, self.ENGINE_MAP[SearchIntent.GENERAL])
    
    def detect_intent(self, query: str) -> SearchIntent:
        """检测搜索意图"""
        query_lower = query.lower()
        
        # 实时信息
        if any(w in query_lower for w in ["今天", "现在", "最新", "current", "latest"]):
            return SearchIntent.REALTIME
        
        # 技术文档
        if any(w in query_lower for w in ["如何", "怎么", "代码", "error", "bug", "api", "文档"]):
            return SearchIntent.TECHNICAL
        
        # 学术论文
        if any(w in query_lower for w in ["论文", "研究", "paper", "research", "arxiv"]):
            return SearchIntent.ACADEMIC
        
        # 新闻
        if any(w in query_lower for w in ["新闻", "消息", "news", "头条"]):
            return SearchIntent.NEWS
        
        # 购物
        if any(w in query_lower for w in ["价格", "购买", "price", "buy", "购物"]):
            return SearchIntent.SHOPPING
        
        return SearchIntent.GENERAL

# ============ 搜索缓存 ============

class SearchCache:
    """搜索结果缓存"""
    
    def __init__(self, size: int = 50000):
        self.cache = {}
        self.size = size
        self.hits = 0
        self.misses = 0
    
    def get(self, query: str) -> Optional[List[SearchResult]]:
        key = self._make_key(query)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None
    
    def set(self, query: str, results: List[SearchResult]):
        key = self._make_key(query)
        if len(self.cache) >= self.size:
            # LRU 淘汰
            oldest = next(iter(self.cache))
            del self.cache[oldest]
        self.cache[key] = results
    
    def _make_key(self, query: str) -> str:
        return hashlib.md5(query.lower().encode()).hexdigest()
    
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

# ============ RRF 融合器 ============

class RRFMerger:
    """RRF (Reciprocal Rank Fusion) 结果融合"""
    
    def __init__(self, k: int = 60):
        self.k = k
    
    def merge(self, results_list: List[List[SearchResult]]) -> List[SearchResult]:
        """融合多个搜索结果"""
        scores = defaultdict(float)
        result_map = {}
        
        for results in results_list:
            for rank, result in enumerate(results):
                # RRF 分数
                rrf_score = 1 / (self.k + rank + 1)
                scores[result.url] += rrf_score
                result_map[result.url] = result
        
        # 按分数排序
        sorted_urls = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        merged = []
        for url in sorted_urls:
            result = result_map[url]
            result.score = scores[url]
            merged.append(result)
        
        return merged

# ============ 内容提取器 ============

class ContentExtractor:
    """智能内容提取"""
    
    def __init__(self):
        self.extractors = {
            "article": self._extract_article,
            "api": self._extract_api,
            "doc": self._extract_doc,
            "news": self._extract_news,
        }
    
    async def extract(self, html: str, url: str) -> ExtractedContent:
        """提取内容"""
        start = time.perf_counter()
        
        # 检测内容类型
        content_type = self._detect_type(html, url)
        
        # 选择提取器
        extractor = self.extractors.get(content_type, self._extract_article)
        
        # 提取
        title, content = extractor(html)
        
        latency = (time.perf_counter() - start) * 1000
        
        return ExtractedContent(
            title=title,
            content=content,
            url=url,
            content_type=content_type,
            extraction_time_ms=latency
        )
    
    def _detect_type(self, html: str, url: str) -> str:
        if "api" in url or "/v1/" in url or "/v2/" in url:
            return "api"
        if "docs" in url or "documentation" in url:
            return "doc"
        if "news" in url or "article" in url:
            return "news"
        return "article"
    
    def _extract_article(self, html: str) -> tuple:
        """提取文章内容"""
        # 简化实现
        title_match = re.search(r'<title>(.*?)</title>', html, re.I)
        title = title_match.group(1) if title_match else ""
        
        # 移除标签
        content = re.sub(r'<[^>]+>', ' ', html)
        content = re.sub(r'\s+', ' ', content).strip()[:5000]
        
        return title, content
    
    def _extract_api(self, html: str) -> tuple:
        """提取 API 响应"""
        return "API Response", html[:2000]
    
    def _extract_doc(self, html: str) -> tuple:
        """提取文档"""
        return self._extract_article(html)
    
    def _extract_news(self, html: str) -> tuple:
        """提取新闻"""
        return self._extract_article(html)

# ============ 连接池管理 ============

class ConnectionPool:
    """HTTP 连接池"""
    
    def __init__(self, max_connections: int = 100):
        self.session = None
        self.max_connections = max_connections
    
    async def init(self):
        """初始化连接池"""
        connector = aiohttp.TCPConnector(
            limit=self.max_connections,
            limit_per_host=20,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=5, connect=0.5)
        )
    
    async def fetch(self, url: str) -> str:
        """抓取网页"""
        async with self.session.get(url) as response:
            return await response.text()
    
    async def close(self):
        """关闭连接池"""
        if self.session:
            await self.session.close()

# ============ 预取引擎 ============

class PrefetchEngine:
    """预取引擎"""
    
    def __init__(self, pool: ConnectionPool):
        self.pool = pool
        self.cache = {}
    
    async def prefetch_links(self, html: str, base_url: str) -> List[str]:
        """预取链接"""
        # 提取链接
        links = re.findall(r'href=["\']([^"\']+)["\']', html)
        
        # 过滤和评分
        scored = []
        for link in links:
            if link.startswith('/'):
                link = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}{link}"
            if link.startswith('http'):
                score = self._score_link(link, base_url)
                if score > 0.5:
                    scored.append((link, score))
        
        # 排序
        scored.sort(key=lambda x: x[1], reverse=True)
        top_links = [l for l, s in scored[:10]]
        
        # 异步预取
        for link in top_links:
            asyncio.create_task(self._prefetch(link))
        
        return top_links
    
    def _score_link(self, link: str, base_url: str) -> float:
        """评分链接"""
        score = 0.5
        
        # 同域名加分
        if urlparse(link).netloc == urlparse(base_url).netloc:
            score += 0.3
        
        # 相关路径加分
        if any(p in link for p in ['doc', 'api', 'guide', 'tutorial']):
            score += 0.2
        
        return min(score, 1.0)
    
    async def _prefetch(self, url: str):
        """预取 URL"""
        try:
            html = await self.pool.fetch(url)
            self.cache[url] = html
        except:
            pass

# ============ 联网辅助引擎 ============

class NetworkAssistantEngine:
    """联网辅助引擎"""
    
    def __init__(self):
        self.router = IntentRouter()
        self.cache = SearchCache()
        self.merger = RRFMerger()
        self.extractor = ContentExtractor()
        self.pool = ConnectionPool()
        self.prefetcher = None
    
    async def init(self):
        """初始化"""
        await self.pool.init()
        self.prefetcher = PrefetchEngine(self.pool)
    
    async def search(self, query: str) -> List[SearchResult]:
        """搜索"""
        # 检查缓存
        cached = self.cache.get(query)
        if cached:
            return cached
        
        # 检测意图
        intent = self.router.detect_intent(query)
        engines = self.router.route(intent)
        
        # 模拟搜索
        results = [
            SearchResult(
                title=f"Result for: {query}",
                url=f"https://example.com/{i}",
                snippet=f"This is result {i} for query: {query}",
                source=engines[i % len(engines)]
            )
            for i in range(10)
        ]
        
        # 缓存
        self.cache.set(query, results)
        
        return results
    
    async def fetch(self, url: str) -> ExtractedContent:
        """抓取网页"""
        html = await self.pool.fetch(url)
        content = await self.extractor.extract(html, url)
        
        # 预取相关链接
        asyncio.create_task(self.prefetcher.prefetch_links(html, url))
        
        return content
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "cache_hit_rate": f"{self.cache.hit_rate() * 100:.1f}%",
            "cached_queries": len(self.cache.cache),
            "prefetched_urls": len(self.prefetcher.cache) if self.prefetcher else 0,
        }
    
    async def close(self):
        """关闭"""
        await self.pool.close()

# ============ 测试 ============

async def test_network_engine():
    """测试联网辅助引擎"""
    engine = NetworkAssistantEngine()
    await engine.init()
    
    print("=" * 50)
    print("联网辅助功能优化引擎 V2 测试")
    print("=" * 50)
    
    # 测试搜索
    print("\n测试搜索:")
    start = time.perf_counter()
    results = await engine.search("Python asyncio 教程")
    latency = (time.perf_counter() - start) * 1000
    print(f"搜索延迟: {latency:.2f}ms")
    print(f"结果数: {len(results)}")
    
    # 测试缓存命中
    print("\n测试缓存命中:")
    start = time.perf_counter()
    results = await engine.search("Python asyncio 教程")
    latency = (time.perf_counter() - start) * 1000
    print(f"缓存命中延迟: {latency:.2f}ms")
    
    # 统计
    print("\n" + "=" * 50)
    print(f"统计: {engine.get_stats()}")
    print("=" * 50)
    
    await engine.close()

if __name__ == "__main__":
    asyncio.run(test_network_engine())
