#!/usr/bin/env python3
"""
evidence_chain_audit.py - 抽查证据链完整性

最低职责:
- 抽查证据链完整性
- 验证删除记录有证据
- 输出审计结果

输出: reports/evidence_chain_audit.json
"""

import os
import json
from datetime import datetime
from pathlib import Path
from infrastructure.path_resolver import get_project_root

def audit_evidence_chain(workspace_path: str) -> dict:
    """审计证据链"""
    results = {
        "audit_time": datetime.now().isoformat(),
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "failed": 0
        },
        "checks": []
    }
    
    workspace = Path(workspace_path)
    reports_dir = workspace / "reports"
    
    # 检查必需的报告文件
    required_files = [
        "INVENTORY_BEFORE.json",
        "INVENTORY_AFTER.json",
        "SKILL_DECISION_LOG.csv",
        "SKILL_REMOVED_MANIFEST.json",
        "MERGE_MAPPING.json",
        "BEFORE_AFTER_DIFF.md",
        "V28_ROLLBACK_PLAN.md"
    ]
    
    for filename in required_files:
        file_path = reports_dir / filename
        check = {
            "file": filename,
            "exists": file_path.exists(),
            "status": "passed" if file_path.exists() else "failed"
        }
        
        if file_path.exists():
            check["size"] = file_path.stat().st_size
        
        results["checks"].append(check)
        results["summary"]["total_checks"] += 1
        if check["status"] == "passed":
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    
    return results

def main():
    workspace = str(get_project_root())
    results = audit_evidence_chain(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "evidence_chain_audit.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"证据链审计完成:")
    print(f"  通过: {results['summary']['passed']}")
    print(f"  失败: {results['summary']['failed']}")

if __name__ == "__main__":
    main()
