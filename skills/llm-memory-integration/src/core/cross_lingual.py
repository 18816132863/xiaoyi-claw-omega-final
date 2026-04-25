#!/usr/bin/env python3
"""
跨语言搜索模块 (v5.0)
多语言支持、语言检测、跨语言向量对齐
"""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import re


class LanguageDetector:
    """
    语言检测器
    """
    
    def __init__(self):
        """初始化语言检测器"""
        # 简单的语言特征
        self.language_features = {
            'zh': r'[\u4e00-\u9fff]',
            'en': r'[a-zA-Z]',
            'ja': r'[\u3040-\u309f\u30a0-\u30ff]',
            'ko': r'[\uac00-\ud7af]',
            'ru': r'[\u0400-\u04ff]',
            'ar': r'[\u0600-\u06ff]'
        }
        
        print("语言检测器初始化完成")
    
    def detect(self, text: str) -> str:
        """
        检测语言
        
        Args:
            text: 文本
        
        Returns:
            str: 语言代码
        """
        # 统计各语言字符数
        counts = {}
        for lang, pattern in self.language_features.items():
            matches = re.findall(pattern, text)
            counts[lang] = len(matches)
        
        # 返回最多的语言
        if not counts or max(counts.values()) == 0:
            return 'unknown'
        
        return max(counts, key=counts.get)


class CrossLingualEncoder:
    """
    跨语言编码器
    将不同语言的文本映射到统一向量空间
    """
    
    def __init__(
        self,
        model: str = "multilingual-e5-base",
        supported_languages: List[str] = None
    ):
        """
        初始化跨语言编码器
        
        Args:
            model: 多语言模型
            supported_languages: 支持的语言列表
        """
        self.model = model
        self.supported_languages = supported_languages or ['zh', 'en', 'ja', 'ko', 'ru', 'ar']
        self.detector = LanguageDetector()
        
        print(f"跨语言编码器初始化:")
        print(f"  模型: {model}")
        print(f"  支持语言: {self.supported_languages}")
    
    def encode(self, text: str, language: Optional[str] = None) -> np.ndarray:
        """
        编码文本（跨语言）
        
        Args:
            text: 文本
            language: 语言代码（可选）
        
        Returns:
            np.ndarray: 向量
        """
        # 检测语言
        if language is None:
            language = self.detector.detect(text)
        
        # 简化实现：使用随机向量
        # 实际实现应使用多语言模型
        return np.random.randn(768).astype(np.float32)
    
    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """
        批量编码
        
        Args:
            texts: 文本列表
        
        Returns:
            np.ndarray: 向量矩阵
        """
        vectors = [self.encode(text) for text in texts]
        return np.array(vectors, dtype=np.float32)


class CrossLingualSearcher:
    """
    跨语言搜索器
    支持多语言搜索
    """
    
    def __init__(
        self,
        encoder: Optional[CrossLingualEncoder] = None
    ):
        """
        初始化跨语言搜索器
        
        Args:
            encoder: 跨语言编码器
        """
        self.encoder = encoder or CrossLingualEncoder()
        self.detector = self.encoder.detector
        
        # 向量存储
        self.vectors = []
        self.metadata = []
        
        print("跨语言搜索器初始化完成")
    
    def add(self, text: str, language: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        添加文本
        
        Args:
            text: 文本
            language: 语言代码
            metadata: 元数据
        """
        # 检测语言
        if language is None:
            language = self.detector.detect(text)
        
        # 编码
        vector = self.encoder.encode(text, language)
        
        # 存储
        self.vectors.append(vector)
        self.metadata.append({
            'text': text,
            'language': language,
            'metadata': metadata or {}
        })
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        languages: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        跨语言搜索
        
        Args:
            query: 查询文本
            top_k: 返回数量
            languages: 过滤语言
        
        Returns:
            List[Dict]: 搜索结果
        """
        if not self.vectors:
            return []
        
        # 编码查询
        query_vector = self.encoder.encode(query)
        
        # 计算相似度
        vectors = np.array(self.vectors)
        query_norm = query_vector / (np.linalg.norm(query_vector) + 1e-10)
        vectors_norm = vectors / (np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10)
        scores = np.dot(vectors_norm, query_norm)
        
        # 收集结果
        results = []
        for i, score in enumerate(scores):
            if languages and self.metadata[i]['language'] not in languages:
                continue
            
            results.append({
                'score': float(score),
                'text': self.metadata[i]['text'],
                'language': self.metadata[i]['language'],
                'metadata': self.metadata[i]['metadata']
            })
        
        # 排序并返回
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def translate_query(self, query: str, target_language: str) -> str:
        """
        翻译查询（简化实现）
        
        Args:
            query: 查询文本
            target_language: 目标语言
        
        Returns:
            str: 翻译结果
        """
        # 简化实现：返回原文
        # 实际实现应调用翻译 API
        return query
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        language_counts = {}
        for m in self.metadata:
            lang = m['language']
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        return {
            'total_count': len(self.metadata),
            'language_distribution': language_counts
        }


if __name__ == "__main__":
    # 测试
    print("=== 跨语言搜索测试 ===")
    
    searcher = CrossLingualSearcher()
    
    # 添加多语言数据
    searcher.add("这是一段中文文本", language='zh')
    searcher.add("This is an English text", language='en')
    searcher.add("これは日本語のテキストです", language='ja')
    searcher.add("이것은 한국어 텍스트입니다", language='ko')
    
    # 搜索
    results = searcher.search("中文", top_k=5)
    print(f"搜索结果: {len(results)} 个")
    
    for r in results:
        print(f"  [{r['language']}] {r['text'][:30]}... (score: {r['score']:.4f})")
    
    # 统计
    stats = searcher.get_stats()
    print(f"统计: {stats}")
