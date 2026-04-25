#!/usr/bin/env python3
"""
Ultimate Search - 终极优化搜索
包含：向量预计算 + 增量缓存 + LLM响应缓存 + 智能路由 + 结果压缩
"""
import subprocess
import sys
import json
import hashlib
import struct
import urllib.request
import threading
import time
import gzip
import base64
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# 配置
VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
from paths import VEC_EXT
GITEE_API = None  # 从配置文件读取
GITEE_KEY = os.environ.get("EMBEDDING_API_KEY", "")
GLM5_URL = "YOUR_LLM_API_ENDPOINT  # SECURITY FIX: hardcoded endpoint removed"
GLM5_KEY = os.environ.get("LLM_API_KEY", "")
GLM5_UID = os.environ.get("LLM_UID", "")
CACHE_DIR = Path.home() / ".openclaw" / "memory-tdai" / ".cache"
CACHE_TTL = 3600

CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 全局缓存（线程安全）
_cache_lock = threading.Lock()  # 缓存锁
embedding_cache = {}  # 向量缓存
llm_expand_cache = {}  # LLM扩展词缓存
llm_rerank_cache = {}  # LLM重排序缓存
precomputed_vectors = {}  # 预计算向量

results = {"vector": [], "fts": [], "expanded": []}

# ============ 1. 向量预计算 ============

def load_precomputed_vectors():
    """加载预计算的常用向量"""
    global precomputed_vectors
    precompute_file = CACHE_DIR / "precomputed_vectors.json"
    if precompute_file.exists():
        try:
            data = json.loads(precompute_file.read_text())
            with _cache_lock:
                for k, v in data.items():
                    precomputed_vectors[k] = v
        except Exception as e:
            logger.error(f"操作失败: {e}")

def save_precomputed_vectors():
    """保存预计算向量"""
    with _cache_lock:
        data = dict(precomputed_vectors)
    precompute_file = CACHE_DIR / "precomputed_vectors.json"
    precompute_file.write_text(json.dumps(data, ensure_ascii=False))

def get_precomputed_vector(query):
    """获取预计算向量"""
    key = hashlib.md5(query.encode()).hexdigest()
    if key in precomputed_vectors:
        return precomputed_vectors[key]
    return None

def set_precomputed_vector(query, embedding):
    """保存预计算向量"""
    key = hashlib.md5(query.encode()).hexdigest()
    precomputed_vectors[key] = embedding
    # 异步保存
    threading.Thread(target=save_precomputed_vectors, daemon=True).start()

# ============ 2. 增量缓存 ============

class IncrementalCache:
    """增量缓存管理器"""
    def __init__(self, cache_dir, ttl=3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl
        self.index_file = self.cache_dir / "cache_index.json"
        self.index = self._load_index()
    
    def _load_index(self):
        if self.index_file.exists():
            try:
                return json.loads(self.index_file.read_text())
            except Exception as e:
                return {}
        return {}
    
    def _save_index(self):
        self.index_file.write_text(json.dumps(self.index, ensure_ascii=False))
    
    def get(self, key):
        if key not in self.index:
            return None
        
        entry = self.index[key]
        cached_time = datetime.fromisoformat(entry["time"])
        
        # 检查过期
        if datetime.now() - cached_time > timedelta(seconds=self.ttl):
            self.delete(key)
            return None
        
        # 读取压缩数据
        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            try:
                compressed = cache_file.read_bytes()
                return self._decompress(compressed)
            except Exception as e:
                return None
        return None
    
    def set(self, key, data):
        # 压缩数据
        compressed = self._compress(data)
        
        # 写入文件
        cache_file = self.cache_dir / f"{key}.cache"
        cache_file.write_bytes(compressed)
        
        # 更新索引
        self.index[key] = {
            "time": datetime.now().isoformat(),
            "size": len(compressed),
            "hits": 0
        }
        self._save_index()
    
    def delete(self, key):
        cache_file = self.cache_dir / f"{key}.cache"
        if cache_file.exists():
            cache_file.unlink()
        if key in self.index:
            del self.index[key]
            self._save_index()
    
    def _compress(self, data):
        """压缩数据"""
        json_str = json.dumps(data, ensure_ascii=False)
        compressed = gzip.compress(json_str.encode())
        return compressed
    
    def _decompress(self, compressed):
        """解压数据"""
        json_str = gzip.decompress(compressed).decode()
        return json.loads(json_str)
    
    def cleanup_expired(self):
        """清理过期缓存"""
        expired_keys = []
        for key, entry in self.index.items():
            cached_time = datetime.fromisoformat(entry["time"])
            if datetime.now() - cached_time > timedelta(seconds=self.ttl):
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        return len(expired_keys)

# ============ 3. LLM 响应缓存 ============

def get_llm_expand_cache(query):
    """获取 LLM 扩展词缓存"""
    key = hashlib.md5(f"expand_{query}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"llm_expand_{key}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text())
            cached_time = datetime.fromisoformat(data["time"])
            if datetime.now() - cached_time < timedelta(seconds=CACHE_TTL * 24):  # 24小时
                return data["terms"]
        except Exception as e:
            logger.error(f"操作失败: {e}")
    return None

def set_llm_expand_cache(query, terms):
    """保存 LLM 扩展词缓存"""
    key = hashlib.md5(f"expand_{query}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"llm_expand_{key}.json"
    cache_file.write_text(json.dumps({
        "time": datetime.now().isoformat(),
        "query": query,
        "terms": terms
    }, ensure_ascii=False))

def get_llm_rerank_cache(query, results_hash):
    """获取 LLM 重排序缓存"""
    key = hashlib.md5(f"rerank_{query}_{results_hash}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"llm_rerank_{key}.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text())
            cached_time = datetime.fromisoformat(data["time"])
            if datetime.now() - cached_time < timedelta(seconds=CACHE_TTL * 24):
                return data["order"]
        except Exception as e:
            logger.error(f"操作失败: {e}")
    return None

def set_llm_rerank_cache(query, results_hash, order):
    """保存 LLM 重排序缓存"""
    key = hashlib.md5(f"rerank_{query}_{results_hash}".encode()).hexdigest()
    cache_file = CACHE_DIR / f"llm_rerank_{key}.json"
    cache_file.write_text(json.dumps({
        "time": datetime.now().isoformat(),
        "query": query,
        "order": order
    }, ensure_ascii=False))

# ============ 4. 智能路由 ============

def analyze_query_complexity(query):
    """分析查询复杂度"""
    # 简单查询特征
    simple_patterns = [
        len(query) < 10,  # 短查询
        len(query.split()) <= 2,  # 词数少
        any(kw in query for kw in ["推送", "配置", "设置", "状态"]),  # 常见关键词
    ]
    
    # 复杂查询特征
    complex_patterns = [
        len(query) > 30,  # 长查询
        "或者" in query or "和" in query,  # 多条件
        "?" in query or "？" in query,  # 疑问句
        any(kw in query for kw in ["比较", "分析", "为什么", "如何"]),  # 分析类
    ]
    
    simple_score = sum(simple_patterns)
    complex_score = sum(complex_patterns)
    
    if complex_score > simple_score:
        return "complex"  # 复杂查询，使用完整模式
    elif simple_score >= 2:
        return "simple"  # 简单查询，使用快速模式
    else:
        return "medium"  # 中等复杂度

def select_search_mode(query, use_llm):
    """智能选择搜索模式"""
    if not use_llm:
        return "fast"
    
    complexity = analyze_query_complexity(query)
    
    if complexity == "simple":
        return "fast"  # 简单查询走快速模式
    elif complexity == "complex":
        return "full"  # 复杂查询走完整模式
    else:
        return "balanced"  # 平衡模式

# ============ 5. 结果压缩 ============

def compress_results(results):
    """压缩结果"""
    compressed = []
    for r in results:
        compressed.append({
            "id": r["record_id"][:20],  # 截断ID
            "t": r["type"][0],  # 类型缩写
            "s": r.get("score", 0),
            "c": r["content"][:100]  # 截断内容
        })
    return compressed

def decompress_results(compressed, full_results):
    """解压结果"""
    results = []
    for c in compressed:
        # 从完整结果中找回
        for r in full_results:
            if r["record_id"].startswith(c["id"]):
                results.append(r)
                break
    return results

# ============ 核心功能 ============

def get_embedding_batch(texts):
    """批量获取向量"""
    results = []
    uncached = []
    uncached_indices = []
    
    for i, text in enumerate(texts):
        # 检查预计算
        precomputed = get_precomputed_vector(text)
        if precomputed:
            results.append(precomputed)
            continue
        
        # 检查缓存
        if text in embedding_cache:
            results.append(embedding_cache[text])
        else:
            results.append(None)
            uncached.append(text)
            uncached_indices.append(i)
    
    if uncached:
        data = json.dumps({
            "input": uncached,
            "model": "Qwen3-Embedding-8B",
            "dimensions": 4096
        }).encode('utf-8')
        
        req = urllib.request.Request(
            GITEE_API, data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {GITEE_KEY}"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                for j, item in enumerate(result['data']):
                    embedding = item['embedding']
                    embedding_cache[uncached[j]] = embedding
                    results[uncached_indices[j]] = embedding
                    # 保存到预计算
                    set_precomputed_vector(uncached[j], embedding)
        except Exception as e:
            logger.error(f"操作失败: {e}")
    
    return results

def llm_expand_query(query):
    """LLM 查询扩展（带缓存）"""
    # 检查缓存
    cached = get_llm_expand_cache(query)
    if cached:
        return cached
    
    data = {
        "model": "LLM_GLM5",
        "messages": [{"role": "user", "content": f"将以下查询扩展为3个相关搜索词，每行一个，不要编号：\n{query}"}],
        "max_tokens": 100,
        "temperature": 0.3,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "x-request-from": "openclaw",
        "x-uid": GLM5_UID,
        "x-api-key": GLM5_KEY
    }
    
    try:
        req = urllib.request.Request(
            GLM5_URL, data=json.dumps(data).encode('utf-8'),
            headers=headers, method='POST'
        )
        
        full_content = ""
        with urllib.request.urlopen(req, timeout=30) as resp:
            for line in resp:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        chunk = json.loads(line[6:])
                        if 'choices' in chunk:
                            delta = chunk['choices'][0].get('delta', {})
                            full_content += delta.get('content', '')
                    except Exception as e:
                        pass
            logger.error(f"操作失败: {e}")
        
        terms = [l.strip() for l in full_content.strip().split('\n') if l.strip()][:3]
        # 缓存结果
        set_llm_expand_cache(query, terms)
        return terms
    except Exception as e:
        return [query]

def llm_rerank(query, results):
    """LLM 重排序（带缓存）"""
    if not results or len(results) <= 1:
        return results
    
    # 计算结果哈希
    results_hash = hashlib.md5(
        "".join([r["record_id"] for r in results[:8]]).encode()
    ).hexdigest()[:8]
    
    # 检查缓存
    cached_order = get_llm_rerank_cache(query, results_hash)
    if cached_order:
        return [results[i] for i in cached_order if i < len(results)]
    
    results_text = "\n".join([
        f"{i+1}. [{r['type']}] {r['content'][:60]}..."
        for i, r in enumerate(results[:8])
    ])
    
    data = {
        "model": "LLM_GLM5",
        "messages": [{"role": "user", "content": f"根据查询'{query}'对以下结果排序，返回编号列表（逗号分隔）：\n{results_text}"}],
        "max_tokens": 50,
        "temperature": 0.1,
        "stream": True
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "x-request-from": "openclaw",
        "x-uid": GLM5_UID,
        "x-api-key": GLM5_KEY
    }
    
    try:
        req = urllib.request.Request(
            GLM5_URL, data=json.dumps(data).encode('utf-8'),
            headers=headers, method='POST'
        )
        
        full_content = ""
        with urllib.request.urlopen(req, timeout=20) as resp:
            for line in resp:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    try:
                        chunk = json.loads(line[6:])
                        if 'choices' in chunk:
                            delta = chunk['choices'][0].get('delta', {})
                            full_content += delta.get('content', '')
                    except Exception as e:
                        pass
            logger.error(f"操作失败: {e}")
        
        order = [int(x.strip()) - 1 for x in full_content.split(',') if x.strip().isdigit()]
        if order and max(order) < len(results):
            # 缓存结果
            set_llm_rerank_cache(query, results_hash, order)
            return [results[i] for i in order if i < len(results)]
    except Exception as e:
        logger.error(f"操作失败: {e}")
    
    return results

def search_vector(query, embedding):
    """向量搜索"""
    if not embedding:
        results["vector"] = []
        return
    
    # vec_hex 是向量数据的十六进制表示，来自内部计算，安全
    vec_hex = struct.pack(f'{len(embedding)}f', *embedding).hex()
    
    # 安全修复：使用 sqlite3 连接而不是 subprocess
    try:
        import sqlite3
        conn = sqlite3.connect(str(VECTORS_DB))
        conn.enable_load_extension(True)
        conn.load_extension(str(VEC_EXT))
        cursor = conn.cursor()
        
        sql = "SELECT v.record_id, r.content, r.type, r.scene_name, v.distance FROM l1_vec v JOIN l1_records r ON v.record_id = r.record_id WHERE v.embedding MATCH X? AND k = 10 ORDER BY v.distance ASC;"
        cursor.execute(sql, (vec_hex,))
        rows = cursor.fetchall()
        conn.close()
        
        results["vector"] = []
        for row in rows:
            if len(row) >= 5:
                dist = float(row[4])
                if dist > 0:
                    results["vector"].append({
                        "record_id": row[0],
                        "content": row[1],
                        "type": row[2],
                        "scene": row[3],
                        "distance": dist,
                        "score": 1.0 - dist
                    })
    except Exception as e:
        results["vector"] = []

def search_fts(query):
    """FTS 搜索（安全版本）"""
    tokens = query.replace('，', ' ').replace('、', ' ').split()
    
    # 安全修复：转义 FTS 特殊字符
    import re
    safe_tokens = []
    for token in tokens:
        token = re.sub(r"['\";\\-]", '', token)
        if token:
            safe_tokens.append(token)
    
    if not safe_tokens:
        results["fts"] = []
        return
    
    fts_query = " OR ".join(safe_tokens)
    
    try:
        import sqlite3
        conn = sqlite3.connect(str(VECTORS_DB))
        cursor = conn.cursor()
        sql = "SELECT record_id, content, type, scene_name FROM l1_fts WHERE l1_fts MATCH ? ORDER BY rank LIMIT 10;"
        cursor.execute(sql, (fts_query,))
        rows = cursor.fetchall()
        conn.close()
        
        results["fts"] = []
        for row in rows:
            if len(row) >= 4:
                    results["fts"].append({
                        "record_id": parts[0],
                        "content": parts[1],
                        "type": parts[2],
                        "scene": parts[3],
                        "source": "fts"
                    })
    except Exception as e:
        results["fts"] = []

def merge_results():
    """合并去重"""
    seen = set()
    merged = []
    
    for r in results["vector"]:
        if r["record_id"] not in seen:
            r["source"] = "vector"
            merged.append(r)
            seen.add(r["record_id"])
    
    for r in results["fts"]:
        if r["record_id"] not in seen:
            merged.append(r)
            seen.add(r["record_id"])
    
    merged.sort(key=lambda x: (x.get("score", 0)), reverse=True)
    return merged

# ============ 主函数 ============

# 初始化
load_precomputed_vectors()
inc_cache = IncrementalCache(CACHE_DIR)

def main():
    use_llm = "--no-llm" not in sys.argv
    query = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ""
    
    if not query:
        print("用法: ultimate_search.py '查询' [--no-llm]")
        sys.exit(1)
    
    start = time.time()
    
    # 智能路由
    mode = select_search_mode(query, use_llm)
    
    # 检查增量缓存
    cache_key = hashlib.md5(f"{query}_{mode}".encode()).hexdigest()
    cached = inc_cache.get(cache_key)
    if cached:
        elapsed = (time.time() - start) * 1000
        print(f"查询: {query} (缓存命中)")
        print(f"模式: {mode}")
        print(f"耗时: {elapsed:.0f}ms\n")
        for i, r in enumerate(cached[:5], 1):
            print(f"{i}. [{r.get('t', '?')}] {r.get('c', '')[:80]}...")
        return
    
    # 根据模式执行
    if mode == "fast":
        # 快速模式：仅向量+FTS
        embedding = get_embedding_batch([query])[0]
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(search_vector, query, embedding)
            executor.submit(search_fts, query)
        merged = merge_results()
    else:
        # 完整模式：LLM扩展+并行+重排序
        expanded_terms = llm_expand_query(query) if use_llm else [query]
        all_queries = [query] + (expanded_terms if use_llm else [])
        all_embeddings = get_embedding_batch(all_queries)
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.submit(search_vector, query, all_embeddings[0])
            executor.submit(search_fts, " ".join(all_queries))
        
        merged = merge_results()
        
        if use_llm and merged:
            merged = llm_rerank(query, merged)
    
    # 压缩并缓存结果
    compressed = compress_results(merged)
    inc_cache.set(cache_key, compressed)
    
    elapsed = (time.time() - start) * 1000
    
    print(f"查询: {query}")
    print(f"模式: {mode} (智能路由)")
    if use_llm and mode != "fast":
        print(f"扩展词: {', '.join(results.get('expanded', []))}")
    print(f"耗时: {elapsed:.0f}ms")
    print(f"向量结果: {len(results['vector'])} 条")
    print(f"FTS结果: {len(results['fts'])} 条\n")
    
    for i, r in enumerate(merged[:5], 1):
        score = f"相似度: {r.get('score', 0):.2f}" if 'score' in r else ""
        print(f"{i}. [{r.get('type', '?')}] {score}")
        print(f"   场景: {r.get('scene', 'N/A')}")
        print(f"   内容: {r.get('content', '')[:100]}...")
        print(f"   来源: {r.get('source', 'N/A')}\n")

if __name__ == "__main__":
    main()
