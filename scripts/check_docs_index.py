#!/usr/bin/env python3
"""
文档索引检查器

检查新增文档是否进入 docs/README_RELEASE_INDEX.md 或对应总索引
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class DocsIndexChecker:
    """文档索引检查器"""
    
    def __init__(self, root: Path = None):
        self.root = root or PROJECT_ROOT
        self.inventory_dir = self.root / "infrastructure" / "inventory"
        self.reports_dir = self.root / "reports" / "integrity"
        
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "documents": {},
            "issues": [],
            "stats": {},
        }
    
    def scan_documents(self) -> Dict:
        """扫描文档文件"""
        documents = {}
        
        docs_dir = self.root / "docs"
        if not docs_dir.exists():
            return documents
        
        for doc_file in docs_dir.glob("*.md"):
            if doc_file.name.startswith("_"):
                continue
            
            doc_name = doc_file.stem
            
            documents[doc_name] = {
                "name": doc_name,
                "path": str(doc_file),
                "indexed": False,
                "index_sources": [],
            }
        
        return documents
    
    def scan_indexes(self) -> Dict[str, Set[str]]:
        """扫描索引文件"""
        indexes = {}
        
        # 主要索引文件
        index_files = [
            self.root / "docs" / "README.md",
            self.root / "docs" / "README_RELEASE_INDEX.md",
            self.root / "README.md",
        ]
        
        for index_file in index_files:
            if not index_file.exists():
                continue
            
            content = index_file.read_text(encoding='utf-8')
            
            # 提取所有 .md 文件引用
            matches = re.findall(r'\[([^\]]+)\]\(([^)]+\.md)\)', content)
            
            indexed_docs = set()
            for _, link in matches:
                # 提取文件名
                doc_name = Path(link).stem
                indexed_docs.add(doc_name)
            
            indexes[str(index_file.relative_to(self.root))] = indexed_docs
        
        return indexes
    
    def check_indexing(self) -> List[Dict]:
        """检查文档是否已索引"""
        issues = []
        
        documents = self.scan_documents()
        indexes = self.scan_indexes()
        
        # 合并所有索引
        all_indexed = set()
        for index_name, indexed_docs in indexes.items():
            all_indexed.update(indexed_docs)
        
        # 检查每个文档
        for doc_name, doc_info in documents.items():
            if doc_name in ["README", "README_RELEASE_INDEX"]:
                doc_info["indexed"] = True
                continue
            
            doc_info["indexed"] = doc_name in all_indexed
            
            # 记录索引来源
            for index_name, indexed_docs in indexes.items():
                if doc_name in indexed_docs:
                    doc_info["index_sources"].append(index_name)
            
            if not doc_info["indexed"]:
                issues.append({
                    "type": "document_not_indexed",
                    "name": doc_name,
                    "path": doc_info["path"],
                })
        
        self.results["documents"] = documents
        self.results["indexes"] = {k: list(v) for k, v in indexes.items()}
        self.results["issues"] = issues
        self.results["stats"] = {
            "total": len(documents),
            "indexed": sum(1 for d in documents.values() if d["indexed"]),
            "orphan": len(issues),
        }
        
        return issues
    
    def run_check(self) -> Dict:
        """运行检查"""
        print("=" * 60)
        print("  文档索引检查器 V1.0.0")
        print("=" * 60)
        
        print("\n🔍 扫描文档文件...")
        issues = self.check_indexing()
        
        print(f"\n文档总数: {self.results['stats']['total']}")
        print(f"已索引: {self.results['stats']['indexed']}")
        print(f"孤儿文档: {self.results['stats']['orphan']}")
        
        print("\n" + "=" * 60)
        if issues:
            print(f"  ❌ 发现 {len(issues)} 个孤儿文档")
            for issue in issues:
                print(f"    - {issue['name']}")
        else:
            print("  ✅ 所有文档已正确索引")
        print("=" * 60 + "\n")
        
        return self.results
    
    def save_report(self) -> Path:
        """保存报告"""
        report_path = self.reports_dir / f"docs_index_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 报告已保存: {report_path}")
        
        return report_path


def main():
    """主函数"""
    checker = DocsIndexChecker()
    checker.run_check()
    checker.save_report()
    
    return 0 if not checker.results["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
