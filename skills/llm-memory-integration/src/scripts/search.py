#!/usr/bin/env python3
"""统一搜索入口 - 完整集成版"""
import sys
import os
import json
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])

from core import (
    EmbeddingEngine, LLMEngine, CacheManager, SearchEngine, QueryRouter,
    QueryRewriter, DynamicWeights, SemanticDeduplicator, QueryHistory,
    LanguageDetector, ResultExplainer, FeedbackLearner,
    RRFFusion, QueryUnderstanding, ResultSummarizer
)
import hashlib
import time
from datetime import datetime
from pathlib import Path

# 配置文件路径
CONFIG_PATH = Path.home() / ".openclaw" / "workspace" / "skills" / "llm-memory-integration" / "config" / "llm_config.json"
OPENCLAW_JSON = Path.home() / ".openclaw" / "openclaw.json"

def load_config():
    """加载配置（优先级：配置文件 > openclaw.json > 环境变量）"""
    config = {
        "embedding_api": os.environ.get("EMBEDDING_API", ""),
        "embedding_key": os.environ.get("EMBEDDING_API_KEY", ""),
        "llm_url": os.environ.get("LLM_BASE_URL", ""),
        "llm_key": os.environ.get("LLM_API_KEY", ""),
        "llm_uid": os.environ.get("LLM_UID", ""),
    }
    
    # 从配置文件加载
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                cfg = json.load(f)
            emb = cfg.get("embedding", {})
            llm = cfg.get("llm", {})
            config["embedding_api"] = emb.get("base_url", config["embedding_api"])
            config["embedding_key"] = emb.get("api_key", config["embedding_key"])
            config["llm_url"] = llm.get("base_url", config["llm_url"])
            config["llm_key"] = llm.get("api_key", config["llm_key"])
        except Exception as e:
            logger.error(f"操作失败: {e}")
    
    # 从 openclaw.json 加载
    if OPENCLAW_JSON.exists():
        try:
            with open(OPENCLAW_JSON) as f:
                cfg = json.load(f)
            emb = cfg.get("plugins", {}).get("entries", {}).get("memory-tencentdb", {}).get("config", {}).get("embedding", {})
            config["embedding_api"] = emb.get("baseUrl", config["embedding_api"])
            config["embedding_key"] = emb.get("apiKey", config["embedding_key"])
        except Exception as e:
            logger.error(f"操作失败: {e}")
    
    return config

# 加载配置
_config = load_config()

# 默认路径配置
DB_PATH = str(Path.home() / ".openclaw" / "memory-tdai" / "vectors.db")
VEC_EXT = str(Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0")
CACHE_DIR = str(Path.home() / ".openclaw" / "memory-tdai" / ".cache")

# 初始化引擎（使用配置）
embedding_engine = EmbeddingEngine(_config["embedding_api"], _config["embedding_key"])
llm_engine = LLMEngine(_config["llm_url"], _config["llm_key"], _config["llm_uid"])
cache_manager = CacheManager(CACHE_DIR)
search_engine = SearchEngine(DB_PATH, VEC_EXT)
query_history = QueryHistory(CACHE_DIR)
deduplicator = SemanticDeduplicator()
explainer = ResultExplainer(_config["llm_url"], _config["llm_key"], _config["llm_uid"])
feedback_learner = FeedbackLearner(CACHE_DIR)
rrf_fusion = RRFFusion(k=60)
summarizer = ResultSummarizer(_config["llm_url"], _config["llm_key"], _config["llm_uid"])

def search(query: str, use_llm: bool = True, explain: bool = False, summarize: bool = False) -> dict:
    """统一搜索"""
    start = time.time()
    
    # 1. 查询理解
    understanding = QueryUnderstanding.analyze(query)
    search_hints = QueryUnderstanding.get_search_hints(understanding)
    
    # 2. 查询改写
    rewritten_query, corrections = QueryRewriter.rewrite(query)
    synonym_expansions = QueryRewriter.get_synonym_expansions(rewritten_query)
    
    # 3. 语言检测
    lang_info = LanguageDetector.get_search_strategy(query)
    
    # 4. 智能路由
    base_mode = QueryRouter.select_mode(rewritten_query, use_llm)
    recommended_mode = query_history.get_recommended_mode(rewritten_query)
    mode = recommended_mode if recommended_mode else base_mode
    
    # 根据查询理解调整模式
    if understanding["intent"][0] == "explain":
        mode = "full"
        explain = True
    
    # 5. 检查缓存
    cache_key = hashlib.md5(f"{rewritten_query}_{mode}_{lang_info['language']}".encode()).hexdigest()
    cached = cache_manager.get(cache_key)
    if cached:
        query_history.record(query, mode, (time.time() - start) * 1000, len(cached.get("results", [])))
        return {
            "query": query,
            "rewritten": rewritten_query,
            "understanding": understanding,
            "mode": mode,
            "language": lang_info['language'],
            "cached": True,
            "elapsed_ms": (time.time() - start) * 1000,
            "results": cached["results"]
        }
    
    # 6. 动态权重
    vector_weight, fts_weight = DynamicWeights.calculate(rewritten_query)
    
    # 7. 执行搜索
    if mode == "fast":
        embedding = embedding_engine.get(rewritten_query)
        vec_results, fts_results = search_engine.parallel_search(embedding, rewritten_query)
        expanded = []
    else:
        expanded = llm_engine.expand_query(rewritten_query) if use_llm else [rewritten_query]
        all_queries = [rewritten_query] + expanded + synonym_expansions
        embeddings = embedding_engine.batch(all_queries)
        vec_results, fts_results = search_engine.parallel_search(embeddings[0], " ".join(all_queries))
    
    # 8. RRF 混合检索
    merged = rrf_fusion.fuse(vec_results, fts_results)
    
    # 9. 语义去重
    merged = deduplicator.deduplicate(merged)
    
    # 10. LLM 重排序
    if mode == "full" and merged:
        merged = llm_engine.rerank(rewritten_query, merged)
    
    # 11. 应用反馈学习
    merged = feedback_learner.apply_feedback(rewritten_query, merged)
    
    # 12. 结果解释
    explanation = None
    if explain and merged:
        explanation = explainer.explain(rewritten_query, merged)
    
    # 13. 结果摘要
    summary = None
    if summarize and merged:
        summary = summarizer.summarize(rewritten_query, merged)
    
    # 14. 缓存结果
    cache_manager.set(cache_key, {
        "results": merged[:10], 
        "time": datetime.now().isoformat()
    })
    
    # 15. 记录历史
    elapsed_ms = (time.time() - start) * 1000
    query_history.record(query, mode, elapsed_ms, len(merged))
    
    return {
        "query": query,
        "rewritten": rewritten_query,
        "understanding": understanding,
        "mode": mode,
        "language": lang_info['language'],
        "cached": False,
        "elapsed_ms": elapsed_ms,
        "corrections": corrections,
        "expanded": expanded,
        "weights": {"vector": vector_weight, "fts": fts_weight},
        "vector_count": len(vec_results),
        "fts_count": len(fts_results),
        "results": merged[:10],
        "explanation": explanation,
        "summary": summary
    }

def record_feedback(query: str, clicked_id: str, position: int):
    """记录点击反馈"""
    feedback_learner.record_click(query, clicked_id, position)

def main():
    use_llm = "--no-llm" not in sys.argv
    explain = "--explain" in sys.argv
    summarize = "--summarize" in sys.argv
    query = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else ""
    
    if not query:
        print("用法: search.py '查询' [--no-llm] [--explain] [--summarize]")
        sys.exit(1)
    
    result = search(query, use_llm, explain, summarize)
    
    print(f"查询: {result['query']}")
    if result.get('rewritten') != result['query']:
        print(f"改写: {result['rewritten']}")
    
    # 显示查询理解
    u = result.get('understanding', {})
    print(f"意图: {u.get('intent', ['unknown', 0])[0]}")
    print(f"实体: {', '.join([e['value'] for e in u.get('entities', [])]) or '无'}")
    print(f"语言: {result.get('language', 'unknown')}")
    print(f"模式: {result['mode']} (智能路由)")
    
    if result.get("cached"):
        print(f"缓存命中")
    if result.get("expanded"):
        print(f"扩展词: {', '.join(result['expanded'])}")
    print(f"耗时: {result['elapsed_ms']:.0f}ms")
    print(f"结果: {len(result.get('results', []))} 条\n")
    
    if result.get("summary"):
        print(f"📝 摘要: {result['summary']}\n")
    
    if result.get("explanation"):
        print(f"💡 {result['explanation']}\n")
    
    for i, r in enumerate(result["results"][:5], 1):
        rrf_info = ""
        if "rrf_score" in r:
            rrf_info = f"RRF: {r.get('rrf_score', 0):.4f}"
        print(f"{i}. [{r.get('type', '?')}] {rrf_info}")
        print(f"   场景: {r.get('scene', 'N/A')}")
        print(f"   内容: {r.get('content', '')[:100]}...")
        print(f"   来源: {r.get('source', 'N/A')}\n")

if __name__ == "__main__":
    main()
