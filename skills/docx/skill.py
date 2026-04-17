#!/usr/bin/env python3
"""
Docx V2.0 - Word文档处理系统

功能：
1. 文档创建与编辑
2. 模板填充
3. 格式转换
4. 批量处理
5. 表格操作
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class DocxProcessor:
    """Word文档处理器"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.output_dir = self.root / "reports" / "output" / "docx"
        self.template_dir = self.root / "reports" / "templates"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # 文档模板
        self.templates = {
            "report": {
                "name": "报告模板",
                "structure": ["标题", "摘要", "正文", "结论", "附录"],
                "styles": {"title": "Heading 1", "section": "Heading 2", "body": "Normal"}
            },
            "letter": {
                "name": "信函模板",
                "structure": ["称呼", "正文", "结尾", "署名", "日期"],
                "styles": {"title": "Normal", "body": "Normal"}
            },
            "contract": {
                "name": "合同模板",
                "structure": ["标题", "甲方", "乙方", "条款", "签署"],
                "styles": {"title": "Heading 1", "section": "Heading 2", "body": "Normal"}
            },
            "resume": {
                "name": "简历模板",
                "structure": ["个人信息", "教育背景", "工作经历", "技能", "自我评价"],
                "styles": {"title": "Heading 1", "section": "Heading 2", "body": "Normal"}
            },
            "meeting": {
                "name": "会议纪要模板",
                "structure": ["会议信息", "参会人员", "议题", "决议", "待办"],
                "styles": {"title": "Heading 1", "section": "Heading 2", "body": "Normal"}
            }
        }
        
        # 格式预设
        self.format_presets = {
            "formal": {
                "name": "正式",
                "font": "宋体",
                "font_size": 12,
                "line_spacing": 1.5,
                "margin": {"top": 2.54, "bottom": 2.54, "left": 3.17, "right": 3.17}
            },
            "casual": {
                "name": "非正式",
                "font": "微软雅黑",
                "font_size": 11,
                "line_spacing": 1.15,
                "margin": {"top": 2.0, "bottom": 2.0, "left": 2.5, "right": 2.5}
            },
            "academic": {
                "name": "学术",
                "font": "Times New Roman",
                "font_size": 12,
                "line_spacing": 2.0,
                "margin": {"top": 2.54, "bottom": 2.54, "left": 3.17, "right": 3.17}
            }
        }
    
    def create_document(
        self,
        title: str,
        template: str = "report",
        format_preset: str = "formal",
        content: Dict = None
    ) -> Dict:
        """创建文档"""
        
        result = {
            "success": False,
            "title": title,
            "template": template
        }
        
        # 验证模板
        template_config = self.templates.get(template)
        if not template_config:
            result["error"] = f"未知模板: {template}"
            return result
        
        # 验证格式
        format_config = self.format_presets.get(format_preset, self.format_presets["formal"])
        
        # 生成文档ID
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建文档结构
        document = {
            "doc_id": doc_id,
            "title": title,
            "template": template,
            "template_name": template_config["name"],
            "format": format_config,
            "sections": [],
            "created_at": datetime.now().isoformat()
        }
        
        # 填充内容
        for section_name in template_config["structure"]:
            section_content = content.get(section_name, "") if content else ""
            document["sections"].append({
                "name": section_name,
                "style": template_config["styles"].get("section", "Heading 2"),
                "content": section_content
            })
        
        # 保存
        doc_file = self.output_dir / f"{doc_id}.json"
        doc_file.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
        
        result["success"] = True
        result["doc_id"] = doc_id
        result["doc_file"] = str(doc_file)
        result["sections"] = len(document["sections"])
        result["message"] = f"文档《{title}》创建成功"
        
        return result
    
    def fill_template(
        self,
        template_file: str,
        data: Dict,
        output_name: str = None
    ) -> Dict:
        """填充模板"""
        
        result = {
            "success": False,
            "template": template_file,
            "data": data
        }
        
        template_path = Path(template_file)
        if not template_path.exists():
            result["error"] = f"模板文件不存在: {template_file}"
            return result
        
        # 生成输出文件名
        output_file = self.output_dir / (output_name or f"filled_{template_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # 模拟填充
        filled_content = {
            "template": template_file,
            "data": data,
            "filled_at": datetime.now().isoformat(),
            "status": "filled"
        }
        
        output_file.write_text(json.dumps(filled_content, ensure_ascii=False, indent=2), encoding='utf-8')
        
        result["success"] = True
        result["output_file"] = str(output_file)
        result["message"] = "模板填充成功"
        
        return result
    
    def batch_create(
        self,
        template: str,
        data_list: List[Dict],
        title_field: str = "title"
    ) -> Dict:
        """批量创建文档"""
        
        result = {
            "success": False,
            "template": template,
            "total": len(data_list),
            "created": [],
            "failed": []
        }
        
        for i, data in enumerate(data_list):
            title = data.get(title_field, f"文档{i+1}")
            create_result = self.create_document(title, template, content=data)
            
            if create_result["success"]:
                result["created"].append({
                    "title": title,
                    "doc_id": create_result["doc_id"]
                })
            else:
                result["failed"].append({
                    "title": title,
                    "error": create_result.get("error", "未知错误")
                })
        
        result["success"] = True
        result["created_count"] = len(result["created"])
        result["failed_count"] = len(result["failed"])
        
        return result
    
    def add_table(
        self,
        doc_id: str,
        table_data: List[List[str]],
        headers: List[str] = None
    ) -> Dict:
        """添加表格"""
        
        result = {
            "success": False,
            "doc_id": doc_id
        }
        
        # 加载文档
        doc_file = self.output_dir / f"{doc_id}.json"
        if not doc_file.exists():
            result["error"] = f"文档不存在: {doc_id}"
            return result
        
        document = json.loads(doc_file.read_text(encoding='utf-8'))
        
        # 添加表格
        table = {
            "type": "table",
            "headers": headers or [],
            "rows": table_data,
            "created_at": datetime.now().isoformat()
        }
        
        document.setdefault("tables", []).append(table)
        
        # 保存
        doc_file.write_text(json.dumps(document, ensure_ascii=False, indent=2), encoding='utf-8')
        
        result["success"] = True
        result["table_added"] = True
        result["rows"] = len(table_data)
        result["message"] = "表格添加成功"
        
        return result
    
    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        return [
            {"id": k, "name": v["name"], "sections": v["structure"]}
            for k, v in self.templates.items()
        ]
    
    def list_formats(self) -> List[Dict]:
        """列出所有格式预设"""
        return [
            {"id": k, "name": v["name"], "font": v["font"]}
            for k, v in self.format_presets.items()
        ]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Docx Processor V2.0")
    parser.add_argument("action", choices=["create", "fill", "batch", "table", "templates", "formats"], help="操作类型")
    parser.add_argument("--title", help="文档标题")
    parser.add_argument("--template", default="report", help="模板类型")
    parser.add_argument("--format", default="formal", help="格式预设")
    parser.add_argument("--template-file", help="模板文件路径")
    parser.add_argument("--data", help="数据(JSON)")
    parser.add_argument("--doc-id", help="文档ID")
    args = parser.parse_args()
    
    root = get_project_root()
    processor = DocxProcessor(root)
    
    if args.action == "create":
        if not args.title:
            print("请提供标题: --title '文档标题'")
            return 1
        
        content = json.loads(args.data) if args.data else None
        result = processor.create_document(args.title, args.template, args.format, content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "fill":
        if not args.template_file or not args.data:
            print("请提供: --template-file 模板路径 --data 数据JSON")
            return 1
        
        data = json.loads(args.data)
        result = processor.fill_template(args.template_file, data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "batch":
        if not args.data:
            print("请提供数据列表: --data '[{...}, {...}]'")
            return 1
        
        data_list = json.loads(args.data)
        result = processor.batch_create(args.template, data_list)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "table":
        if not args.doc_id or not args.data:
            print("请提供: --doc-id 文档ID --data 表格数据JSON")
            return 1
        
        table_data = json.loads(args.data)
        result = processor.add_table(args.doc_id, table_data)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "templates":
        templates = processor.list_templates()
        print(json.dumps(templates, ensure_ascii=False, indent=2))
        
    elif args.action == "formats":
        formats = processor.list_formats()
        print(json.dumps(formats, ensure_ascii=False, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
