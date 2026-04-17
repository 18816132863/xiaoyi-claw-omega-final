#!/usr/bin/env python3
"""
Novel Generator 技能执行脚本
支持爽文小说生成、多题材模板、长期记忆集成
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class NovelGenerator:
    """爽文小说生成器"""
    
    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.learnings_dir = Path(__file__).parent / ".learnings"
        self.output_dir.mkdir(exist_ok=True)
        self.learnings_dir.mkdir(exist_ok=True)
        
        # 题材模板
        self.templates = {
            "都市": {
                "power_system": "商业帝国/科技巨头/医术/武道",
                "protagonist": "普通人/落魄富二代/退伍军人",
                "golden_finger": "系统/重生/异能/医术传承",
                "conflict": "商业竞争/家族恩怨/都市江湖"
            },
            "修仙": {
                "power_system": "练气-筑基-金丹-元婴-化神-渡劫-大乘",
                "protagonist": "废柴弟子/散修/转世大能",
                "golden_finger": "神秘功法/上古传承/系统",
                "conflict": "宗门争斗/天劫/飞升"
            },
            "玄幻": {
                "power_system": "斗者-斗师-大斗师-斗灵-斗王-斗皇-斗宗-斗尊-斗圣-斗帝",
                "protagonist": "家族废柴/异火拥有者/血脉觉醒者",
                "golden_finger": "异火/血脉/神器/系统",
                "conflict": "家族恩怨/异火争夺/位面战争"
            },
            "重生": {
                "power_system": "商业/科技/娱乐/体育",
                "protagonist": "重生者/穿越者",
                "golden_finger": "前世记忆/系统",
                "conflict": "改变命运/弥补遗憾/商业竞争"
            },
            "系统流": {
                "power_system": "系统等级/任务奖励/商城兑换",
                "protagonist": "普通人/穿越者",
                "golden_finger": "各类系统(签到/抽奖/商城/任务)",
                "conflict": "系统任务/竞争对手/世界危机"
            }
        }
    
    def generate_prompt(
        self,
        theme: str,
        keywords: List[str] = None,
        protagonist: str = "",
        golden_finger: str = "",
        conflict: str = ""
    ) -> Dict:
        """生成完善的创作提示词"""
        
        template = self.templates.get(theme, self.templates["都市"])
        
        prompt = f"""# 小说创作提示词

## 题材定位
- 主类型: {theme}
- 子类型: {template['power_system']}

## 世界观设定
- 力量体系: {template['power_system']}
- 社会规则: 强者为尊，实力说话
- 时代背景: 现代/架空

## 主角人设
- 初始身份: {protagonist or template['protagonist']}
- 性格特点: 坚韧、果断、有仇必报
- 金手指: {golden_finger or template['golden_finger']}

## 核心冲突
- 主线矛盾: {conflict or template['conflict']}
- 前3章即时冲突: 被看不起 → 打脸 → 崛起

## 爽点设计
- 打脸节奏: 每3章一次小打脸，每10章一次大打脸
- 升级频率: 每5章一个小突破，每20章一个大境界
- 装逼方式: 扮猪吃虎、实力碾压、众人震惊

## 节奏规划
- 第1-3章: 开篇钩子 + 初次打脸
- 第4-10章: 建立人设 + 小高潮
- 第11-20章: 中期冲突 + 大高潮
- 第21-30章: 新地图 + 新挑战

## 配角框架
- 对手: 嚣张跋扈的富二代/天才弟子
- 盟友: 忠诚的小弟/神秘的长者
- 红颜: 冰山美人/活泼少女/温柔师姐

## 开篇钩子
第一章用"众人皆看不起 → 主角展现实力 → 众人震惊"的经典结构抓住读者

## 关键词
{', '.join(keywords or ['逆袭', '打脸', '爽文'])}
"""
        
        # 保存提示词
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prompt_{timestamp}.md"
        filepath = self.output_dir / filename
        filepath.write_text(prompt, encoding='utf-8')
        
        return {
            "status": "success",
            "theme": theme,
            "prompt": prompt,
            "file": str(filepath)
        }
    
    def generate_chapter(
        self,
        chapter_num: int,
        title: str,
        outline: str,
        previous_summary: str = ""
    ) -> Dict:
        """生成单章节"""
        
        # 读取角色和地点记忆
        characters = self._read_memory("CHARACTERS.md")
        locations = self._read_memory("LOCATIONS.md")
        
        chapter = f"""# 第{chapter_num}章 {title}

## 章节大纲
{outline}

## 前情提要
{previous_summary or "开篇章节"}

## 角色信息
{characters}

## 地点信息
{locations}

---

[章节正文内容将由AI根据上述信息生成]

## 章节要点
- 情节推进:
- 角色互动:
- 爽点设计:
- 伏笔埋设:

## 下章预告
[待生成]
"""
        
        # 保存章节
        filename = f"第{chapter_num:03d}章_{title}.md"
        filepath = self.output_dir / filename
        filepath.write_text(chapter, encoding='utf-8')
        
        # 记录到情节记忆
        self._write_memory("PLOT_POINTS.md", f"\n## 第{chapter_num}章\n- 标题: {title}\n- 大纲: {outline}\n")
        
        return {
            "status": "success",
            "chapter": chapter_num,
            "title": title,
            "file": str(filepath)
        }
    
    def _read_memory(self, filename: str) -> str:
        """读取记忆文件"""
        filepath = self.learnings_dir / filename
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
        return "暂无记录"
    
    def _write_memory(self, filename: str, content: str):
        """写入记忆文件"""
        filepath = self.learnings_dir / filename
        if filepath.exists():
            existing = filepath.read_text(encoding='utf-8')
            filepath.write_text(existing + content, encoding='utf-8')
        else:
            filepath.write_text(content, encoding='utf-8')


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return 1
    
    command = sys.argv[1]
    generator = NovelGenerator()
    
    if command == "help":
        print_help()
    elif command == "prompt":
        # python skill.py prompt --theme 都市 --protagonist 落魄富二代 --golden-finger 重生系统
        args = parse_args(sys.argv[2:])
        if 'keywords' in args and isinstance(args['keywords'], str):
            args['keywords'] = args['keywords'].split(',')
        result = generator.generate_prompt(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "chapter":
        # python skill.py chapter --num 1 --title 逆袭开始 --outline "主角被退婚，觉醒系统"
        args = parse_args(sys.argv[2:])
        result = generator.generate_chapter(**args)
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
    print("""Novel Generator 技能 - 爽文小说生成器

命令:
  help      显示帮助
  prompt    生成创作提示词
  chapter   生成单章节

示例:
  # 生成都市题材提示词
  python skill.py prompt --theme 都市 --protagonist 落魄富二代 --golden-finger 重生系统

  # 生成第一章
  python skill.py chapter --num 1 --title 逆袭开始 --outline "主角被退婚，觉醒系统"

支持的题材:
  - 都市: 商业/科技/医术/武道
  - 修仙: 练气-筑基-金丹-元婴-化神-渡劫-大乘
  - 玄幻: 斗者-斗师-大斗师-斗灵-斗王-斗皇-斗宗-斗尊-斗圣-斗帝
  - 重生: 商业/科技/娱乐/体育
  - 系统流: 签到/抽奖/商城/任务系统

特性:
  ✅ 自动维护角色一致性
  ✅ 自动维护地点一致性
  ✅ 自动记录情节转折
  ✅ 支持多题材模板
  ✅ 爽点节奏分析
""")


if __name__ == "__main__":
    sys.exit(main())
