#!/usr/bin/env python3
"""
安全数据导出模块 v2.0
限制导出范围，防止数据泄露
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# 安全导出白名单（仅允许导出这些文件）
EXPORT_WHITELIST = [
    "MEMORY.md",
    "persona.md",
]

# 禁止导出的敏感文件
EXPORT_BLACKLIST = [
    "openclaw.json",  # 可能包含 API 密钥
    "llm_config.json",  # 包含 API 配置
    "vectors.db",  # 完整数据库
    ".cache",  # 缓存数据
    "exports",  # 导出目录
]

WORKSPACE = Path.home() / ".openclaw" / "workspace"
MEMORY_TDDB = Path.home() / ".openclaw" / "memory-tdai"

def safe_export_config(export_dir: Optional[Path] = None, 
                       include_database: bool = False) -> dict:
    """
    安全导出配置（限制导出范围）
    
    Args:
        export_dir: 导出目录
        include_database: 是否包含数据库（需要用户明确确认）
    
    Returns:
        导出结果
    """
    result = {
        "success": False,
        "exported_files": [],
        "skipped_files": [],
        "errors": []
    }
    
    if export_dir is None:
        export_dir = WORKSPACE / "exports" / f"safe_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    export_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 仅导出白名单文件
    for filename in EXPORT_WHITELIST:
        src = WORKSPACE / filename
        if src.exists():
            try:
                # 检查文件大小（限制 1MB）
                if src.stat().st_size > 1024 * 1024:
                    result["skipped_files"].append(f"{filename} (超过大小限制)")
                    continue
                
                # 脱敏处理
                content = src.read_text(encoding='utf-8')
                content = _redact_sensitive_content(content)
                
                (export_dir / filename).write_text(content, encoding='utf-8')
                result["exported_files"].append(filename)
            except Exception as e:
                result["errors"].append(f"{filename}: {e}")
    
    # 2. 导出每日记录（仅最近7天）
    memory_dir = WORKSPACE / "memory"
    if memory_dir.exists():
        daily_dir = export_dir / "daily_notes"
        daily_dir.mkdir(exist_ok=True)
        
        cutoff = datetime.now().timestamp() - 7 * 24 * 3600
        for f in memory_dir.glob("*.md"):
            if f.stat().st_mtime > cutoff:
                try:
                    content = _redact_sensitive_content(f.read_text(encoding='utf-8'))
                    (daily_dir / f.name).write_text(content, encoding='utf-8')
                    result["exported_files"].append(f"daily/{f.name}")
                except Exception as e:
                    result["errors"].append(f"daily/{f.name}: {e}")
    
    # 3. 数据库导出（需要明确确认）
    if include_database:
        result["skipped_files"].append("vectors.db (需要明确确认)")
    
    # 4. 生成导出报告
    report = {
        "export_time": datetime.now().isoformat(),
        "export_dir": str(export_dir),
        "exported_count": len(result["exported_files"]),
        "skipped_count": len(result["skipped_files"]),
        "security_note": "仅导出白名单文件，敏感数据已脱敏"
    }
    
    (export_dir / "export_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding='utf-8'
    )
    
    result["success"] = len(result["errors"]) == 0
    return result

def _redact_sensitive_content(content: str) -> str:
    """脱敏敏感内容"""
    import re
    
    # 脱敏 API 密钥
    content = re.sub(
        r'(api_key|apiKey|api-key)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}["\']?',
        r'\1 = [REDACTED]',
        content,
        flags=re.IGNORECASE
    )
    
    # 脱敏密码
    content = re.sub(
        r'(password|passwd|pwd)\s*[=:]\s*["\']?[^\s"\']{8,}["\']?',
        r'\1 = [REDACTED]',
        content,
        flags=re.IGNORECASE
    )
    
    # 脱敏 token
    content = re.sub(
        r'(token|secret)\s*[=:]\s*["\']?[A-Za-z0-9_\-]{20,}["\']?',
        r'\1 = [REDACTED]',
        content,
        flags=re.IGNORECASE
    )
    
    return content

def get_export_whitelist() -> List[str]:
    """获取导出白名单"""
    return EXPORT_WHITELIST.copy()

def get_export_blacklist() -> List[str]:
    """获取导出黑名单"""
    return EXPORT_BLACKLIST.copy()

if __name__ == "__main__":
    print("=" * 60)
    print("安全数据导出模块")
    print("=" * 60)
    print("\n导出白名单:")
    for f in EXPORT_WHITELIST:
        print(f"  ✅ {f}")
    
    print("\n导出黑名单:")
    for f in EXPORT_BLACKLIST:
        print(f"  ❌ {f}")
    
    print("\n安全特性:")
    print("  ✅ 仅导出白名单文件")
    print("  ✅ 敏感内容自动脱敏")
    print("  ✅ 文件大小限制 1MB")
    print("  ✅ 每日记录仅保留 7 天")
    print("  ❌ 数据库导出需要明确确认")
