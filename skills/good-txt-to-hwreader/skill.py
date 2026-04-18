#!/usr/bin/env python3
"""
good-txt-to-hwreader 技能执行脚本
清理和修复盗版 txt 电子书中的乱码、广告和排版问题。当用户需要处理 txt 格式电子书、修复乱码、去除广告水印、规范化章节排版时使用此 skill。触发词：txt清理、电子书修复、去广告、修乱码、排版修复、清理txt、修复电子书、txt乱码、txt广告。
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class GoodTxtToHwreader:
    """技能主类"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.templates_dir = Path(__file__).parent / "templates"
        self.output_dir.mkdir(exist_ok=True)
    
    def help(self) -> str:
        """返回帮助信息"""
        return """
good-txt-to-hwreader 技能

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
    skill = GoodTxtToHwreader()
    
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
        print("good-txt-to-hwreader v1.0.0")
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
