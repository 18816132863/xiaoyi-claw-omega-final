from typing import Optional, List
"""Embedding 引擎 - 支持预计算和批量"""
import json
import hashlib
import urllib.request
from pathlib import Path
from typing import List, Optional

class EmbeddingEngine:
    def __init__(self, api_url: str, api_key: str, model: str = "Qwen3-Embedding-8B", dimensions: int = 4096):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self.cache = {}
        self.precomputed = {}
        self.cache_dir = Path.home() / ".openclaw" / "memory-tdai" / ".cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._load_precomputed()
    
    def _load_precomputed(self):
        """加载预计算向量"""
        file = self.cache_dir / "precomputed.json"
        if file.exists():
            try:
                self.precomputed = json.loads(file.read_text())
            except:
                pass
    
    def _save_precomputed(self):
        """保存预计算向量"""
        file = self.cache_dir / "precomputed.json"
        file.write_text(json.dumps(self.precomputed))
    
    def _hash(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[List[float]]:
        """获取单个向量"""
        # 检查预计算
        h = self._hash(text)
        if h in self.precomputed:
            return self.precomputed[h]
        
        # 检查缓存
        if text in self.cache:
            return self.cache[text]
        
        # 调用 API
        result = self.batch([text])
        return result[0] if result else None
    
    def batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """批量获取向量"""
        results = [None] * len(texts)
        uncached = []
        indices = []
        
        for i, text in enumerate(texts):
            h = self._hash(text)
            if h in self.precomputed:
                results[i] = self.precomputed[h]
            elif text in self.cache:
                results[i] = self.cache[text]
            else:
                uncached.append(text)
                indices.append(i)
        
        if uncached:
            data = json.dumps({
                "input": uncached,
                "model": self.model,
                "dimensions": self.dimensions
            }).encode('utf-8')
            
            req = urllib.request.Request(
                self.api_url, data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
            )
            
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    result = json.loads(resp.read().decode('utf-8'))
                    for j, item in enumerate(result['data']):
                        emb = item['embedding']
                        self.cache[uncached[j]] = emb
                        self.precomputed[self._hash(uncached[j])] = emb
                        results[indices[j]] = emb
                    self._save_precomputed()
            except:
                pass
        
        return results
