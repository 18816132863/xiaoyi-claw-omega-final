#!/usr/bin/env python3
"""
web-search-exa 技能执行脚本
Neural web search, content extraction, company and people research, code search, and deep research via the Exa MCP server. Use when you need to: (1) search the web with semantic understanding — not just keywords, (2) find research papers, news, tweets, companies, or people, (3) extract clean content from URLs, (4) find semantically similar pages to a known URL, (5) get code examples and documentation, (6) run deep multi-step research with a report, (7) get a quick synthesized answer with citations. NOT for: local file operations, non-web tasks, or anything that doesn't involve web search or content retrieval.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class WebSearchExa:
    """技能主类"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.templates_dir = Path(__file__).parent / "templates"
        self.output_dir.mkdir(exist_ok=True)
    
    def help(self) -> str:
        """返回帮助信息"""
        return """
web-search-exa 技能

命令:
  help      显示帮助
  run       执行技能
  list      列出可用模板
  version   显示版本

示例:
  python skill.py run --template default
  python skill.py list
"""
    
    def run(self, **kwargs) -> Dict:
        """执行技能主逻辑"""
        # 1. 参数验证
        template = kwargs.get('template', 'default')
        
        # 2. 加载模板
        template_content = self.load_template(template)
        
        # 3. 执行核心逻辑
        result = self.execute(template_content, kwargs)
        
        # 4. 保存结果
        if result.get('save', True):
            filepath = self.save_output(result['content'])
            result['file'] = str(filepath)
        
        # 5. 返回结果
        return result
    
    def execute(self, template: str, params: Dict) -> Dict:
        """执行核心逻辑 - 子类应重写此方法"""
        return {
            "status": "success",
            "content": template,
            "params": params,
            "timestamp": datetime.now().isoformat()
        }
    
    def load_template(self, name: str) -> str:
        """加载模板"""
        template_file = self.templates_dir / f"{name}.md"
        if template_file.exists():
            return template_file.read_text(encoding='utf-8')
        return "# 默认模板\\n\\n待完善..."
    
    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        if not self.templates_dir.exists():
            return []
        return [f.stem for f in self.templates_dir.glob("*.md")]
    
    def save_output(self, content: str, prefix: str = "output") -> Path:
        """保存输出文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.md"
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        return filepath


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python skill.py <command> [args]")
        print("运行 'python skill.py help' 查看帮助")
        return 1
    
    command = sys.argv[1]
    skill = WebSearchExa()
    
    if command == "help":
        print(skill.help())
    elif command == "run":
        args = parse_args(sys.argv[2:])
        result = skill.run(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "list":
        templates = skill.list_templates()
        print("可用模板:")
        for t in templates:
            print(f"  - {t}")
    elif command == "version":
        print("web-search-exa v1.0.0")
    else:
        print(f"未知命令: {command}")
        return 1
    
    return 0


def parse_args(args: List[str]) -> Dict:
    """解析命令行参数"""
    result = {}
    i = 0
    while i < len(args):
        if args[i].startswith('--'):
            key = args[i][2:].replace('-', '_')
            if i + 1 < len(args) and not args[i + 1].startswith('--'):
                result[key] = args[i + 1]
                i += 2
            else:
                result[key] = True
                i += 1
        else:
            i += 1
    return result


if __name__ == "__main__":
    sys.exit(main())
