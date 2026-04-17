#!/usr/bin/env python3
"""
Claw Art 技能执行脚本
支持中文提示词、风格预设、批量生成
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class ClawArt:
    """AI绘画生成器"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # 风格预设
        self.styles = {
            "赛博朋克": {
                "keywords": ["霓虹灯", "未来城市", "机械改造", "全息投影", "黑暗雨夜"],
                "colors": ["紫色", "蓝色", "粉色", "黑色"],
                "mood": "科技感、未来感、反乌托邦"
            },
            "国风": {
                "keywords": ["水墨", "山水", "古建筑", "仙鹤", "祥云"],
                "colors": ["青色", "金色", "红色", "白色"],
                "mood": "古典、优雅、意境深远"
            },
            "二次元": {
                "keywords": ["动漫", "萌系", "校园", "魔法少女", "机甲"],
                "colors": ["粉色", "蓝色", "黄色", "白色"],
                "mood": "可爱、青春、梦幻"
            },
            "写实": {
                "keywords": ["照片级", "超高清", "细节丰富", "光影真实"],
                "colors": ["自然色调"],
                "mood": "真实、细腻、专业"
            },
            "油画": {
                "keywords": ["印象派", "笔触明显", "色彩浓郁", "艺术感"],
                "colors": ["暖色调", "冷色调"],
                "mood": "艺术、经典、厚重"
            },
            "水彩": {
                "keywords": ["淡雅", "晕染", "透明感", "清新"],
                "colors": ["淡蓝", "淡粉", "淡绿", "白色"],
                "mood": "清新、文艺、温柔"
            }
        }
    
    def generate_prompt(
        self,
        description: str,
        style: str = "写实",
        aspect_ratio: str = "1:1",
        quality: str = "high",
        count: int = 1
    ) -> Dict:
        """生成绘画提示词"""
        
        style_config = self.styles.get(style, self.styles["写实"])
        
        # 中文提示词
        cn_prompt = f"""{description}
风格: {style}
氛围: {style_config['mood']}
关键词: {', '.join(style_config['keywords'])}
色调: {', '.join(style_config['colors'])}
比例: {aspect_ratio}
质量: {quality}
"""
        
        # 英文提示词 (用于主流绘图API)
        en_prompt = f"""{description}, {style} style, {style_config['mood']} atmosphere,
{', '.join(style_config['keywords'])}, {', '.join(style_config['colors'])} color palette,
aspect ratio {aspect_ratio}, {quality} quality, highly detailed, masterpiece
"""
        
        # 保存提示词
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prompt_{timestamp}.json"
        filepath = self.output_dir / filename
        
        prompt_data = {
            "timestamp": timestamp,
            "description": description,
            "style": style,
            "chinese_prompt": cn_prompt,
            "english_prompt": en_prompt,
            "aspect_ratio": aspect_ratio,
            "quality": quality,
            "count": count
        }
        
        filepath.write_text(json.dumps(prompt_data, ensure_ascii=False, indent=2), encoding='utf-8')
        
        return {
            "status": "success",
            "style": style,
            "chinese_prompt": cn_prompt,
            "english_prompt": en_prompt,
            "file": str(filepath)
        }
    
    def batch_generate(
        self,
        descriptions: List[str],
        style: str = "写实",
        aspect_ratio: str = "1:1"
    ) -> Dict:
        """批量生成提示词"""
        
        results = []
        for desc in descriptions:
            result = self.generate_prompt(desc, style, aspect_ratio)
            results.append(result)
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
    
    def list_styles(self) -> Dict:
        """列出所有风格预设"""
        
        styles_info = []
        for name, config in self.styles.items():
            styles_info.append({
                "name": name,
                "keywords": config['keywords'],
                "colors": config['colors'],
                "mood": config['mood']
            })
        
        return {
            "status": "success",
            "styles": styles_info
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return 1
    
    command = sys.argv[1]
    art = ClawArt()
    
    if command == "help":
        print_help()
    elif command == "prompt":
        # python skill.py prompt --description "一个穿着汉服的少女站在桃花树下" --style 国风 --aspect-ratio 16:9
        args = parse_args(sys.argv[2:])
        result = art.generate_prompt(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "batch":
        # python skill.py batch --descriptions "少女,少年,老人" --style 二次元
        args = parse_args(sys.argv[2:])
        if 'descriptions' in args and isinstance(args['descriptions'], str):
            args['descriptions'] = args['descriptions'].split(',')
        result = art.batch_generate(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "styles":
        result = art.list_styles()
        print(json.dumps(result, ensure_ascii=False, indent=2))
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


def print_help():
    """打印帮助信息"""
    print("""Claw Art 技能 - AI绘画生成器

命令:
  help      显示帮助
  prompt    生成绘画提示词
  batch     批量生成提示词
  styles    列出所有风格预设

示例:
  # 生成国风绘画提示词
  python skill.py prompt --description "一个穿着汉服的少女站在桃花树下" --style 国风 --aspect-ratio 16:9

  # 批量生成二次元提示词
  python skill.py batch --descriptions "少女,少年,老人" --style 二次元

  # 查看所有风格
  python skill.py styles

支持的风格:
  - 赛博朋克: 霓虹灯、未来城市、机械改造
  - 国风: 水墨、山水、古建筑、仙鹤
  - 二次元: 动漫、萌系、校园、魔法少女
  - 写实: 照片级、超高清、细节丰富
  - 油画: 印象派、笔触明显、色彩浓郁
  - 水彩: 淡雅、晕染、透明感、清新

特性:
  ✅ 中文提示词支持
  ✅ 英文提示词自动生成
  ✅ 6种风格预设
  ✅ 批量生成
  ✅ 自定义比例和质量
""")


if __name__ == "__main__":
    sys.exit(main())
