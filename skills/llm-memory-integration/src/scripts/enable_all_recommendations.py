#!/usr/bin/env python3
"""
一键启用所有优化建议（安全修复版）
使用 sqlite3 直接连接，避免 subprocess 调用
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

VECTORS_DB = Path.home() / ".openclaw" / "memory-tdai" / "vectors.db"
VEC_EXT = Path.home() / ".openclaw" / "extensions" / "memory-tencentdb" / "node_modules" / "sqlite-vec-linux-x64" / "vec0.so"
CONFIG_FILE = Path.home() / ".openclaw" / "memory-tencentdb.json"

def get_db_connection(load_ext: bool = False) -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(VECTORS_DB))
    
    if load_ext and VEC_EXT.exists():
        conn.enable_load_extension(True)
        conn.load_extension(str(VEC_EXT))
    
    return conn

def check_vector_model():
    """检查向量模型配置"""
    print("\n📊 向量模型配置:")
    
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        embedding = config.get("embedding", {})
        
        provider = embedding.get("provider", "N/A")
        model = embedding.get("model", "N/A")
        dimensions = embedding.get("dimensions", "N/A")
        enabled = embedding.get("enabled", False)
        
        print(f"  Provider: {provider} {'✅' if provider != 'N/A' else '⚠️'}")
        print(f"  Model: {model} {'✅' if model != 'N/A' else '⚠️'}")
        print(f"  Dimensions: {dimensions} {'✅' if dimensions != 'N/A' else '⚠️'}")
        print(f"  Enabled: {enabled} {'✅' if enabled else '⚠️'}")
        
        return provider != "N/A" and model != "N/A" and enabled
    
    print("  ⚠️ 配置文件不存在")
    return False

def check_pipeline():
    """检查 Pipeline 配置"""
    print("\n⚙️ Pipeline 配置:")
    
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        pipeline = config.get("pipeline", {})
        
        every_n = pipeline.get("everyNConversations", "N/A")
        l1_idle = pipeline.get("l1IdleTimeoutSeconds", "N/A")
        max_memories = pipeline.get("maxMemoriesPerSession", "N/A")
        warmup = pipeline.get("enableWarmup", False)
        
        print(f"  everyNConversations: {every_n} {'✅' if every_n != 'N/A' else '⚠️'}")
        print(f"  l1IdleTimeoutSeconds: {l1_idle} {'✅' if l1_idle != 'N/A' else '⚠️'}")
        print(f"  maxMemoriesPerSession: {max_memories} {'✅' if max_memories != 'N/A' else '⚠️'}")
        print(f"  enableWarmup: {warmup} {'✅' if warmup else '⚠️'}")
        
        return every_n != "N/A" and warmup
    
    print("  ⚠️ 配置文件不存在")
    return False

def check_scripts():
    """检查技能脚本"""
    print("\n📝 技能脚本:")
    
    scripts_dir = Path.home() / ".openclaw" / "workspace" / "skills" / "llm-memory-integration" / "scripts"
    
    required_scripts = {
        "vsearch": "混合记忆搜索",
        "llm-analyze": "LLM 记忆分析",
        "optimize_vector_system.py": "向量体系优化",
        "one_click_setup.py": "一键配置",
        "hybrid_memory_search.py": "混合搜索核心",
        "llm_client.py": "LLM 客户端",
        "smart_memory_update.py": "智能记忆更新"
    }
    
    all_ok = True
    for script, desc in required_scripts.items():
        script_path = scripts_dir / script
        exists = script_path.exists()
        print(f"  {script}: {'✅' if exists else '⚠️'} ({desc})")
        if not exists:
            all_ok = False
    
    return all_ok

def check_vector_coverage():
    """检查向量覆盖率"""
    print("\n📈 向量覆盖率:")
    
    try:
        # 查询普通表
        conn = get_db_connection(load_ext=False)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM l1_records")
        l1_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM l0_conversations")
        l0_conversations = cursor.fetchone()[0]
        
        conn.close()
        
        # 查询向量表
        conn = get_db_connection(load_ext=True)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM l1_vec")
        l1_vec = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM l0_vec")
        l0_vec = cursor.fetchone()[0]
        
        conn.close()
        
        l1_coverage = 100.0 * l1_vec / max(l1_records, 1)
        l0_coverage = 100.0 * l0_vec / max(l0_conversations, 1)
        
        l1_ok = l1_coverage >= 95
        l0_ok = l0_coverage >= 60
        
        print(f"  L1 覆盖率: {l1_coverage:.1f}% {'✅' if l1_ok else '⚠️'}")
        print(f"  L0 覆盖率: {l0_coverage:.1f}% {'✅' if l0_ok else '⚠️'}")
        
        return l1_ok and l0_ok
    
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        return False

def run_maintenance():
    """运行维护任务"""
    print("\n🔧 执行维护任务:")
    
    try:
        conn = get_db_connection(load_ext=False)
        
        # VACUUM
        print("  执行 VACUUM...")
        conn.execute("VACUUM")
        print("  ✅ VACUUM 完成")
        
        # 重建 FTS
        print("  重建 FTS 索引...")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS l1_fts")
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS l1_fts USING fts5(
                record_id, content, type, scene_name,
                content='', tokenize='unicode61'
            )
        """)
        cursor.execute("INSERT INTO l1_fts(rowid, record_id, content, type, scene_name) SELECT rowid, record_id, content, type, scene_name FROM l1_records")
        conn.commit()
        print("  ✅ FTS 索引重建完成")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"  ❌ 维护失败: {e}")
        return False

def main():
    print("=" * 60)
    print("一键启用所有优化建议")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        "向量模型配置": check_vector_model(),
        "Pipeline 配置": check_pipeline(),
        "技能脚本": check_scripts(),
        "向量覆盖率": check_vector_coverage(),
    }
    
    # 如果覆盖率不足，运行维护
    if not results["向量覆盖率"]:
        results["维护任务"] = run_maintenance()
    
    print("\n" + "=" * 60)
    print("📊 检查结果汇总")
    print("=" * 60)
    
    all_ok = True
    for name, ok in results.items():
        print(f"  {name}: {'✅' if ok else '⚠️'}")
        if not ok:
            all_ok = False
    
    if all_ok:
        print("\n✅ 所有优化已启用，系统状态良好")
    else:
        print("\n⚠️ 部分优化需要配置，请检查上述警告项")

if __name__ == "__main__":
    main()
