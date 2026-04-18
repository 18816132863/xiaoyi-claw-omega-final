#!/usr/bin/env python3
"""
Claw Art 技能执行脚本 V2.0
商业级别 - 支持中文提示词、风格预设、批量生成
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class ClawArt:
    """AI绘画生成器 - 商业级别"""

    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.templates_dir = Path(__file__).parent / "templates"
        self.output_dir.mkdir(exist_ok=True)

        # 风格预设
        self.styles = {
            "赛博朋克": {
                "keywords": ["霓虹灯", "未来城市", "机械改造", "全息投影", "黑暗雨夜"],
                "colors": ["紫色", "蓝色", "粉色", "黑色"],
                "mood": "科技感、未来感、反乌托邦",
                "artists": ["Simon Stålenhag", "Syd Mead"]
            },
            "国风": {
                "keywords": ["水墨", "山水", "古建筑", "仙鹤", "祥云"],
                "colors": ["青色", "金色", "红色", "白色"],
                "mood": "古典、优雅、意境深远",
                "artists": ["吴冠中", "张大千"]
            },
            "二次元": {
                "keywords": ["动漫", "萌系", "校园", "魔法少女", "机甲"],
                "colors": ["粉色", "蓝色", "黄色", "白色"],
                "mood": "可爱、青春、梦幻",
                "artists": ["新海诚", "京阿尼"]
            },
            "写实": {
                "keywords": ["照片级", "超高清", "细节丰富", "光影真实"],
                "colors": ["自然色调"],
                "mood": "真实、细腻、专业",
                "artists": ["Greg Rutkowski", "Artgerm"]
            },
            "油画": {
                "keywords": ["印象派", "笔触明显", "色彩浓郁", "艺术感"],
                "colors": ["暖色调", "冷色调"],
                "mood": "艺术、经典、厚重",
                "artists": ["梵高", "莫奈"]
            },
            "水彩": {
                "keywords": ["淡雅", "晕染", "透明感", "清新"],
                "colors": ["淡蓝", "淡粉", "淡绿", "白色"],
                "mood": "清新、文艺、温柔",
                "artists": ["水彩画家"]
            }
        }

    def help(self) -> str:
        """返回帮助信息"""
        return """
Claw Art 技能 - 商业级别AI绘画生成器

命令:
  help      显示帮助
  prompt    生成绘画提示词
  batch     批量生成提示词
  styles    列出所有风格预设
  version   显示版本

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
"""

    def prompt(self, **kwargs) -> Dict:
        """生成绘画提示词"""
        description = kwargs.get('description', '')
        style = kwargs.get('style', '写实')
        aspect_ratio = kwargs.get('aspect_ratio', '1:1')
        quality = kwargs.get('quality', 'high')
        count = int(kwargs.get('count', 1))

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
aspect ratio {aspect_ratio}, {quality} quality, highly detailed, masterpiece,
{', '.join(style_config['artists'])} style
"""

        # 负面提示词
        negative_prompt = """low quality, bad quality, blurry, pixelated, distorted,
ugly, deformed, disfigured, bad anatomy, bad proportions,
extra limbs, missing limbs, floating limbs, disconnected limbs,
mutation, mutated, gross, disgusting"""

        prompt_content = f"""# AI绘画提示词

## 基本信息
- 描述: {description}
- 风格: {style}
- 比例: {aspect_ratio}
- 质量: {quality}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 中文提示词

{cn_prompt}

---

## 英文提示词 (用于Stable Diffusion/Midjourney)

{en_prompt}

---

## 负面提示词

{negative_prompt}

---

## 风格说明

### 关键词
{', '.join(style_config['keywords'])}

### 色调
{', '.join(style_config['colors'])}

### 氛围
{style_config['mood']}

### 参考艺术家
{', '.join(style_config['artists'])}

---

## 使用建议

### Stable Diffusion
```
Prompt: {en_prompt}
Negative: {negative_prompt}
Steps: 30-50
Sampler: DPM++ 2M Karras
CFG Scale: 7-12
Size: {aspect_ratio.replace(':', 'x')}
```

### Midjourney
```
{en_prompt}
--ar {aspect_ratio}
--q {quality}
--v 5.2
```

---

## 商业价值评估

- **适用场景**: 商业插画、广告设计、游戏美术
- **质量等级**: 专业级
- **制作成本**: 低（AI生成）
- **商业价值**: ⭐⭐⭐⭐⭐
"""

        # 保存提示词
        filepath = self.save_output(prompt_content, "prompt")

        return {
            "status": "success",
            "style": style,
            "chinese_prompt": cn_prompt,
            "english_prompt": en_prompt,
            "negative_prompt": negative_prompt,
            "file": str(filepath),
            "commercial_value": "⭐⭐⭐⭐⭐"
        }

    def batch(self, **kwargs) -> Dict:
        """批量生成提示词"""
        descriptions = kwargs.get('descriptions', '').split(',')
        style = kwargs.get('style', '写实')
        aspect_ratio = kwargs.get('aspect_ratio', '1:1')

        results = []
        for desc in descriptions:
            if desc.strip():
                result = self.prompt(
                    description=desc.strip(),
                    style=style,
                    aspect_ratio=aspect_ratio
                )
                results.append(result)

        return {
            "status": "success",
            "count": len(results),
            "results": results
        }

    def styles(self) -> Dict:
        """列出所有风格预设"""
        styles_info = []
        for name, config in self.styles.items():
            styles_info.append({
                "name": name,
                "keywords": config['keywords'],
                "colors": config['colors'],
                "mood": config['mood'],
                "artists": config['artists']
            })

        return {
            "status": "success",
            "styles": styles_info
        }

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
    art = ClawArt()

    if command == "help":
        print(art.help())
    elif command == "prompt":
        args = parse_args(sys.argv[2:])
        result = art.prompt(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "batch":
        args = parse_args(sys.argv[2:])
        result = art.batch(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "styles":
        result = art.styles()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "version":
        print("claw-art v2.0.0 (商业级别)")
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
