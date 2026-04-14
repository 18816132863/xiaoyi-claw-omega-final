#!/usr/bin/env python3
"""
依赖管理器 V1.0.0

功能：
- 自动检测缺失依赖
- 按需安装依赖
- 依赖状态检查
- 依赖清单管理
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

def get_project_root() -> Path:
    current = Path(__file__).resolve().parent.parent
    while current != current.parent:
        if (current / 'core' / 'ARCHITECTURE.md').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


# 依赖清单 - 定义所有需要的依赖及其用途
DEPENDENCY_MANIFEST = {
    "core": {
        "description": "核心依赖 - 必须安装",
        "packages": {
            "numpy": "数值计算",
            "scipy": "科学计算",
            "scikit-learn": "机器学习",
            "requests": "HTTP 请求",
            "aiosqlite": "异步 SQLite",
            "cryptography": "加密",
            "pycryptodome": "加密",
        }
    },
    "llm": {
        "description": "LLM 集成依赖",
        "packages": {
            "openai": "OpenAI API",
            "anthropic": "Claude API",
            "langchain": "LLM 框架",
            "tiktoken": "Token 计数",
        }
    },
    "embedding": {
        "description": "Embedding 依赖",
        "packages": {
            "sentence-transformers": "句子嵌入",
            "transformers": "Transformer 模型",
        }
    },
    "vector": {
        "description": "向量存储依赖",
        "packages": {
            "qdrant-client": "Qdrant 向量数据库",
            "chromadb": "ChromaDB 向量存储",
            "faiss-cpu": "FAISS 相似度搜索",
        }
    },
    "ml": {
        "description": "机器学习依赖",
        "packages": {
            "torch": "PyTorch 深度学习",
            "numba": "JIT 编译加速",
            "llvmlite": "LLVM 绑定",
        }
    },
    "performance": {
        "description": "性能优化依赖",
        "packages": {
            "numexpr": "表达式加速",
            "bottleneck": "瓶颈优化",
        }
    },
    "document": {
        "description": "文档处理依赖",
        "packages": {
            "reportlab": "PDF 生成",
            "weasyprint": "HTML 转 PDF",
            "pdfkit": "PDF 工具",
        }
    }
}


def check_package_installed(package: str) -> bool:
    """检查包是否已安装"""
    try:
        # 特殊处理包名映射
        name_map = {
            "scikit-learn": "sklearn",
            "pycryptodome": "Crypto",
            "sentence-transformers": "sentence_transformers",
            "faiss-cpu": "faiss",
        }
        import_name = name_map.get(package, package.replace("-", "_").replace(".", "_"))
        __import__(import_name)
        return True
    except ImportError:
        return False


def install_package(package: str) -> bool:
    """安装包"""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            timeout=300
        )
        return check_package_installed(package)
    except:
        return False


def check_all_dependencies() -> Dict:
    """检查所有依赖状态"""
    result = {
        "categories": {},
        "missing": [],
        "installed": [],
        "total": 0,
        "missing_count": 0
    }
    
    for category, info in DEPENDENCY_MANIFEST.items():
        cat_result = {
            "description": info["description"],
            "packages": {}
        }
        
        for package, desc in info["packages"].items():
            result["total"] += 1
            installed = check_package_installed(package)
            cat_result["packages"][package] = {
                "description": desc,
                "installed": installed
            }
            
            if installed:
                result["installed"].append(package)
            else:
                result["missing"].append(package)
                result["missing_count"] += 1
        
        result["categories"][category] = cat_result
    
    return result


def install_missing_dependencies(categories: List[str] = None) -> Dict:
    """安装缺失的依赖"""
    result = {
        "installed": [],
        "failed": [],
        "skipped": []
    }
    
    for category, info in DEPENDENCY_MANIFEST.items():
        if categories and category not in categories:
            continue
        
        for package in info["packages"]:
            if not check_package_installed(package):
                print(f"安装 {package}...")
                if install_package(package):
                    result["installed"].append(package)
                    print(f"  ✅ {package} 安装成功")
                else:
                    result["failed"].append(package)
                    print(f"  ❌ {package} 安装失败")
            else:
                result["skipped"].append(package)
    
    return result


def save_dependency_status(status: Dict):
    """保存依赖状态"""
    root = get_project_root()
    status_path = root / "reports/ops/dependency_status.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(status_path, 'w') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def print_dependency_report(status: Dict):
    """打印依赖报告"""
    print("╔══════════════════════════════════════════════════╗")
    print("║          依赖状态报告                           ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    for category, info in status["categories"].items():
        print(f"【{category}】{info['description']}")
        for package, pkg_info in info["packages"].items():
            marker = "✅" if pkg_info["installed"] else "❌"
            print(f"  {marker} {package}: {pkg_info['description']}")
        print()
    
    print("=" * 50)
    print(f"总计: {status['total']} | 已安装: {len(status['installed'])} | 缺失: {status['missing_count']}")
    
    if status["missing"]:
        print(f"\n缺失依赖: {', '.join(status['missing'])}")
        print("\n运行以下命令安装缺失依赖:")
        print(f"  python scripts/dependency_manager.py --install")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="依赖管理器 V1.0.0")
    parser.add_argument("--check", action="store_true", help="检查依赖状态")
    parser.add_argument("--install", action="store_true", help="安装缺失依赖")
    parser.add_argument("--category", help="指定安装的类别")
    parser.add_argument("--save", action="store_true", help="保存状态报告")
    args = parser.parse_args()
    
    if args.install:
        categories = [args.category] if args.category else None
        result = install_missing_dependencies(categories)
        print(f"\n安装完成: {len(result['installed'])} 个")
        print(f"安装失败: {len(result['failed'])} 个")
    else:
        status = check_all_dependencies()
        print_dependency_report(status)
        
        if args.save:
            save_dependency_status(status)
            print(f"\n状态报告已保存")


if __name__ == "__main__":
    main()
