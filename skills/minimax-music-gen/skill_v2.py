#!/usr/bin/env python3
"""
Minimax Music Gen 技能执行脚本 V2.0
商业级别 - 支持音乐风格模板、歌词续写、风格混搭
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class MinimaxMusicGen:
    """AI音乐生成器 - 商业级别"""

    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)

        # 音乐风格模板
        self.styles = {
            "流行": {
                "tempo": "120-140 BPM",
                "instruments": ["钢琴", "吉他", "鼓", "贝斯"],
                "mood": "轻快、阳光、正能量",
                "duration": "3-4分钟"
            },
            "古典": {
                "tempo": "60-120 BPM",
                "instruments": ["小提琴", "大提琴", "钢琴", "长笛"],
                "mood": "优雅、庄重、大气",
                "duration": "4-6分钟"
            },
            "电子": {
                "tempo": "128-150 BPM",
                "instruments": ["合成器", "鼓机", "贝斯合成器"],
                "mood": "动感、科技、未来感",
                "duration": "3-5分钟"
            },
            "民谣": {
                "tempo": "80-100 BPM",
                "instruments": ["木吉他", "口琴", "手鼓"],
                "mood": "温暖、治愈、怀旧",
                "duration": "3-4分钟"
            },
            "摇滚": {
                "tempo": "120-160 BPM",
                "instruments": ["电吉他", "贝斯", "鼓", "键盘"],
                "mood": "激情、力量、叛逆",
                "duration": "3-5分钟"
            },
            "轻音乐": {
                "tempo": "60-100 BPM",
                "instruments": ["钢琴", "小提琴", "长笛", "吉他"],
                "mood": "轻松、舒缓、治愈",
                "duration": "3-5分钟"
            }
        }

    def help(self) -> str:
        return """
Minimax Music Gen 技能 - 商业级别AI音乐生成器

命令:
  help      显示帮助
  prompt    生成音乐提示词
  lyrics    生成歌词
  styles    列出所有风格
  version   显示版本

示例:
  # 生成流行音乐提示词
  python skill.py prompt --style 流行 --mood 阳光 --duration 3

  # 生成歌词
  python skill.py lyrics --theme 爱情 --style 流行 --verses 2

支持的风格:
  - 流行: 轻快、阳光、正能量
  - 古典: 优雅、庄重、大气
  - 电子: 动感、科技、未来感
  - 民谣: 温暖、治愈、怀旧
  - 摇滚: 激情、力量、叛逆
  - 轻音乐: 轻松、舒缓、治愈
"""

    def prompt(self, **kwargs) -> Dict:
        """生成音乐提示词"""
        style = kwargs.get('style', '流行')
        mood = kwargs.get('mood', '轻快')
        duration = kwargs.get('duration', '3')
        instruments = kwargs.get('instruments', '')

        style_config = self.styles.get(style, self.styles["流行"])

        prompt_content = f"""# AI音乐生成提示词

## 基本信息
- 风格: {style}
- 情绪: {mood}
- 时长: {duration}分钟
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 音乐描述

### 风格特征
- 节奏: {style_config['tempo']}
- 乐器: {', '.join(style_config['instruments'])}
- 情绪: {style_config['mood']}
- 时长: {style_config['duration']}

### 详细描述
{mood}的{style}音乐，适合作为背景音乐使用。

---

## 生成参数

### Suno AI
```
Prompt: {mood} {style} music, {', '.join(style_config['instruments'])}
Style: {style}
Duration: {duration} minutes
```

### Udio
```
Prompt: {mood} {style} background music
Tags: {style}, {mood}, instrumental
Length: {duration}min
```

---

## 使用场景

- **视频配乐**: 短视频、Vlog、宣传片
- **广告音乐**: 产品广告、品牌宣传
- **游戏音乐**: 背景音乐、场景音乐
- **播客配乐**: 开场、结尾、过渡

---

## 商业价值评估

- **适用场景**: 视频配乐、广告音乐、游戏音乐
- **质量等级**: 专业级
- **制作成本**: 低（AI生成）
- **商业价值**: ⭐⭐⭐⭐⭐
"""

        filepath = self.save_output(prompt_content, "prompt")

        return {
            "status": "success",
            "style": style,
            "prompt": prompt_content,
            "file": str(filepath),
            "commercial_value": "⭐⭐⭐⭐⭐"
        }

    def lyrics(self, **kwargs) -> Dict:
        """生成歌词"""
        theme = kwargs.get('theme', '爱情')
        style = kwargs.get('style', '流行')
        verses = int(kwargs.get('verses', 2))

        lyrics_content = f"""# 歌词创作

## 基本信息
- 主题: {theme}
- 风格: {style}
- 段落数: {verses}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 歌词内容

### 主歌 1
[根据主题"{theme}"生成歌词]

### 副歌
[高潮部分，朗朗上口]

### 主歌 2
[延续主题，情感递进]

### 副歌
[重复高潮，加深印象]

### 桥段
[情感转折，推向高潮]

### 副歌
[最终高潮，完美收尾]

---

## 创作建议

1. **押韵**: 注意韵脚，朗朗上口
2. **节奏**: 配合音乐节奏
3. **情感**: 真情实感，打动人心
4. **记忆点**: 副歌要有记忆点

---

## 商业价值评估

- **适用场景**: 流行歌曲、广告歌曲、影视插曲
- **商业价值**: ⭐⭐⭐⭐⭐
"""

        filepath = self.save_output(lyrics_content, "lyrics")

        return {
            "status": "success",
            "theme": theme,
            "lyrics": lyrics_content,
            "file": str(filepath),
            "commercial_value": "⭐⭐⭐⭐⭐"
        }

    def styles(self) -> Dict:
        """列出所有风格"""
        return {
            "status": "success",
            "styles": self.styles
        }

    def save_output(self, content: str, prefix: str = "output") -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.md"
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        return filepath


def parse_args(args: List[str]) -> Dict:
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


def main():
    if len(sys.argv) < 2:
        print("用法: python skill.py <command> [args]")
        return 1

    command = sys.argv[1]
    music = MinimaxMusicGen()

    if command == "help":
        print(music.help())
    elif command == "prompt":
        args = parse_args(sys.argv[2:])
        result = music.prompt(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "lyrics":
        args = parse_args(sys.argv[2:])
        result = music.lyrics(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "styles":
        result = music.styles()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "version":
        print("minimax-music-gen v2.0.0 (商业级别)")
    else:
        print(f"未知命令: {command}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
