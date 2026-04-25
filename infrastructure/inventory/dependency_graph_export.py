#!/usr/bin/env python3
"""
dependency_graph_export.py - 导出依赖关系图

最低职责:
- 导出依赖关系图
- 用于看冻结和删除影响
- 生成 JSON 和 DOT 格式

输出: reports/dependency_graph.json, reports/dependency_graph.dot
"""

import os
import json
from datetime import datetime
from pathlib import Path
import re
from infrastructure.path_resolver import get_project_root

def extract_dependencies(workspace_path: str) -> dict:
    """提取依赖关系"""
    workspace = Path(workspace_path)
    graph = {
        "export_time": datetime.now().isoformat(),
        "nodes": [],
        "edges": []
    }
    
    # 扫描所有 md 文件查找依赖引用
    for md_file in workspace.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找引用文件
            source = str(md_file.relative_to(workspace))
            
            # 匹配 markdown 链接和文件引用
            patterns = [
                r'\[([^\]]+)\]\(([^)]+\.md)\)',  # markdown 链接
                r'`([^`]+\.md)`',  # 代码块中的文件名
                r'引用文件|引用|参考|参见.*?[\n\-]((?:\s*[-*]\s*.+\.md\s*\n?)+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    if isinstance(match, tuple):
                        target = match[-1] if match[-1].endswith('.md') else match[0]
                    else:
                        target = match
                    
                    if target.endswith('.md') and not target.startswith('http'):
                        # 清理路径
                        target = target.strip('./')
                        graph["edges"].append({
                            "source": source,
                            "target": target,
                            "type": "reference"
                        })
        except Exception as e:
            continue
    
    # 去重
    seen = set()
    unique_edges = []
    for edge in graph["edges"]:
        key = (edge["source"], edge["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)
    graph["edges"] = unique_edges
    
    # 提取节点
    nodes = set()
    for edge in graph["edges"]:
        nodes.add(edge["source"])
        nodes.add(edge["target"])
    graph["nodes"] = list(nodes)
    
    return graph

def export_dot(graph: dict, output_path: str):
    """导出 DOT 格式"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("digraph dependencies {\n")
        f.write("  rankdir=LR;\n")
        f.write("  node [shape=box];\n\n")
        
        for node in graph["nodes"]:
            label = node.split('/')[-1]
            f.write(f'  "{node}" [label="{label}"];\n')
        
        f.write("\n")
        for edge in graph["edges"]:
            f.write(f'  "{edge["source"]}" -> "{edge["target"]}";\n')
        
        f.write("}\n")

def main():
    workspace = str(get_project_root())
    graph = extract_dependencies(workspace)
    
    output_dir = Path(workspace) / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存 JSON
    json_file = output_dir / "dependency_graph.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
    
    # 保存 DOT
    dot_file = output_dir / "dependency_graph.dot"
    export_dot(graph, str(dot_file))
    
    print(f"依赖图已导出:")
    print(f"  节点数: {len(graph['nodes'])}")
    print(f"  边数: {len(graph['edges'])}")
    print(f"  JSON: {json_file}")
    print(f"  DOT: {dot_file}")

if __name__ == "__main__":
    main()
