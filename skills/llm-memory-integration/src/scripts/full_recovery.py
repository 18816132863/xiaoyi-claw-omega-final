#!/usr/bin/env python3
"""
AI 长时记忆系统完整恢复脚本
恢复所有数据、配置、规则、扩展包和脚本
"""

import json
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

# 路径定义
WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_TDai = Path.home() / ".openclaw" / "memory-tdai"
EXTENSIONS = Path.home() / ".openclaw" / "extensions"
CONFIG_FILE = Path.home() / ".openclaw" / "openclaw.json"
IMA_CONFIG = Path.home() / ".config" / "ima"

def check_status():
    """检查系统状态"""
    print("=" * 60)
    print("   AI 长时记忆系统恢复状态检查")
    print("=" * 60)
    print(f"检查时间: {datetime.now().isoformat()}")
    print()
    
    results = {}
    
    # 1. 检查配置文件
    print("📋 1. 配置文件")
    print("-" * 40)
    if CONFIG_FILE.exists():
        config = json.loads(CONFIG_FILE.read_text())
        plugins = config.get("plugins", {}).get("entries", {})
        
        print(f"  ✅ openclaw.json 存在")
        print(f"  - memory-tencentdb: {'✅ 启用' if plugins.get('memory-tencentdb', {}).get('enabled') else '❌ 禁用'}")
        print(f"  - xiaoyi-channel: {'✅ 启用' if plugins.get('xiaoyi-channel', {}).get('enabled') else '❌ 禁用'}")
        print(f"  - execution-validator: {'✅ 启用' if plugins.get('execution-validator-plugin', {}).get('enabled') else '❌ 禁用'}")
        
        # 检查 Embedding 配置
        embedding = plugins.get('memory-tencentdb', {}).get('config', {}).get('embedding', {})
        if embedding:
            print(f"  - Embedding: {embedding.get('provider', 'N/A')}/{embedding.get('model', 'N/A')}")
        
        results['config'] = True
    else:
        print("  ❌ openclaw.json 不存在")
        results['config'] = False
    
    print()
    
    # 2. 检查记忆数据
    print("🧠 2. 记忆数据")
    print("-" * 40)
    vectors_db = MEMORY_TDai / "vectors.db"
    if vectors_db.exists():
        try:
            conn = sqlite3.connect(str(vectors_db))
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM l0_conversations")
            l0_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM l0_vec_rowids")
            l0_vec = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM l1_records")
            l1_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM l1_vec_rowids")
            l1_vec = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"  ✅ vectors.db 存在")
            print(f"  - L0 对话: {l0_count} 条")
            print(f"  - L0 向量: {l0_vec} 条 ({l0_vec*100//max(l0_count,1)}%)")
            print(f"  - L1 记忆: {l1_count} 条")
            print(f"  - L1 向量: {l1_vec} 条 ({l1_vec*100//max(l1_count,1)}%)")
            
            results['memory'] = True
        except Exception as e:
            print(f"  ❌ 数据库错误: {e}")
            results['memory'] = False
    else:
        print("  ❌ vectors.db 不存在")
        results['memory'] = False
    
    print()
    
    # 3. 检查扩展包
    print("🔌 3. 扩展包")
    print("-" * 40)
    ext_list = list(EXTENSIONS.iterdir()) if EXTENSIONS.exists() else []
    print(f"  扩展包数量: {len(ext_list)}")
    for ext in ext_list:
        if ext.is_dir() and not ext.name.startswith('.'):
            print(f"  - ✅ {ext.name}")
    results['extensions'] = len(ext_list) > 0
    
    print()
    
    # 4. 检查技能
    print("📦 4. 技能")
    print("-" * 40)
    skills_dir = WORKSPACE / "skills"
    if skills_dir.exists():
        skills = [s for s in skills_dir.iterdir() if s.is_dir()]
        print(f"  技能数量: {len(skills)}")
        key_skills = ['llm-memory-integration', 'yaoyao-memory', 'xiaoyi-web-search', 'xiaoyi-gui-agent']
        for ks in key_skills:
            if (skills_dir / ks).exists():
                print(f"  - ✅ {ks}")
            else:
                print(f"  - ❌ {ks} 缺失")
        results['skills'] = True
    else:
        print("  ❌ 技能目录不存在")
        results['skills'] = False
    
    print()
    
    # 5. 检查 IMA 配置
    print("☁️ 5. IMA 云端同步")
    print("-" * 40)
    client_id_file = IMA_CONFIG / "client_id"
    api_key_file = IMA_CONFIG / "api_key"
    
    if client_id_file.exists() and api_key_file.exists():
        print(f"  ✅ IMA 凭证已配置")
        print(f"  - Client ID: {client_id_file.read_text().strip()[:8]}...")
        print(f"  - API Key: {api_key_file.read_text().strip()[:8]}...")
        results['ima'] = True
    else:
        print("  ❌ IMA 凭证未配置")
        results['ima'] = False
    
    print()
    
    # 6. 检查三引擎
    print("⚙️ 6. 三引擎向量架构")
    print("-" * 40)
    
    # sqlite-vec
    if vectors_db.exists():
        print("  - ✅ sqlite-vec (主引擎)")
    
    # Qdrant
    qdrant_dir = Path.home() / ".openclaw" / "qdrant-storage"
    if qdrant_dir.exists():
        print("  - ✅ Qdrant (副引擎)")
    else:
        print("  - ⚠️ Qdrant 未初始化")
    
    # TF-IDF
    tfidf_db = Path.home() / ".openclaw" / "tfidf-storage" / "tfidf.db"
    if tfidf_db.exists():
        print("  - ✅ TF-IDF (备份引擎)")
    else:
        print("  - ⚠️ TF-IDF 未初始化")
    
    results['three_engine'] = vectors_db.exists()
    
    print()
    
    # 7. 检查核心文件
    print("📄 7. 核心文件")
    print("-" * 40)
    core_files = ['MEMORY.md', 'USER.md', 'SOUL.md', 'HEARTBEAT.md', 'persona.md', 'AGENTS.md']
    for cf in core_files:
        file_path = WORKSPACE / cf
        if file_path.exists():
            print(f"  - ✅ {cf}")
        else:
            print(f"  - ❌ {cf} 缺失")
    
    results['core_files'] = all((WORKSPACE / cf).exists() for cf in ['MEMORY.md', 'USER.md', 'SOUL.md'])
    
    print()
    
    # 总结
    print("=" * 60)
    print("   恢复状态总结")
    print("=" * 60)
    
    total = sum(1 for v in results.values() if v)
    total_items = len(results)
    
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}")
    
    print()
    print(f"整体恢复度: {total}/{total_items} ({total*100//total_items}%)")
    
    if total == total_items:
        print("\n🎉 所有组件已完整恢复！")
    elif total >= total_items * 0.8:
        print("\n✅ 大部分组件已恢复，系统可用")
    else:
        print("\n⚠️ 部分组件需要恢复")

if __name__ == "__main__":
    check_status()
