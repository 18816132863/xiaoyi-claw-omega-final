#!/usr/bin/env python3
"""快速搜索 - 禁用 LLM 增强"""
import subprocess
import sys

query = sys.argv[1] if len(sys.argv) > 1 else ""
if not query:
    print("用法: fast_search.py '查询'")
    sys.exit(1)

# 直接调用混合搜索，禁用 LLM
subprocess.run([
    "python3", 
    str(Path.home() / ".openclaw" / "workspace" / "skills" / "llm-memory-integration" / "scripts" / "hybrid_memory_search.py"),
    query, "--no-llm"
], timeout=60)
