#!/usr/bin/env python3
"""
Novel Generator 技能执行脚本 V2.0
商业级别 - 支持爽文小说生成、多题材模板、长期记忆集成
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class NovelGenerator:
    """爽文小说生成器 - 商业级别"""

    def __init__(self):
        self.output_dir = Path(__file__).parent / "output"
        self.templates_dir = Path(__file__).parent / "templates"
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

    def help(self) -> str:
        """返回帮助信息"""
        return """
Novel Generator 技能 - 商业级别爽文生成器

命令:
  help      显示帮助
  prompt    生成创作提示词
  chapter   生成单章节
  outline   生成大纲
  list      列出可用模板
  version   显示版本

示例:
  # 生成都市题材提示词
  python skill.py prompt --theme 都市 --protagonist 落魄富二代 --golden-finger 重生系统

  # 生成第一章
  python skill.py chapter --num 1 --title 逆袭开始 --outline "主角被退婚，觉醒系统"

  # 生成大纲
  python skill.py outline --theme 都市 --chapters 100

支持的题材:
  - 都市: 商业/科技/医术/武道
  - 修仙: 练气-筑基-金丹-元婴-化神-渡劫-大乘
  - 玄幻: 斗者-斗师-大斗师-斗灵-斗王-斗皇-斗宗-斗尊-斗圣-斗帝
  - 重生: 商业/科技/娱乐/体育
  - 系统流: 签到/抽奖/商城/任务系统
"""

    def prompt(self, **kwargs) -> Dict:
        """生成完善的创作提示词"""
        theme = kwargs.get('theme', '都市')
        protagonist = kwargs.get('protagonist', '')
        golden_finger = kwargs.get('golden_finger', '')
        conflict = kwargs.get('conflict', '')
        keywords = kwargs.get('keywords', '').split(',') if kwargs.get('keywords') else []

        template = self.templates.get(theme, self.templates["都市"])

        prompt_content = f"""# 小说创作提示词

## 基本信息
- 题材: {theme}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 世界观设定

### 力量体系
{template['power_system']}

### 社会规则
强者为尊，实力说话

### 时代背景
{'现代都市' if theme == '都市' else '架空世界'}

---

## 主角人设

### 初始身份
{protagonist or template['protagonist']}

### 性格特点
- 坚韧不拔，永不放弃
- 有仇必报，快意恩仇
- 智勇双全，善于谋略
- 重情重义，护短护犊

### 金手指
{golden_finger or template['golden_finger']}

### 成长路线
1. 开局低谷，被人看不起
2. 获得金手指，开始崛起
3. 小有成就，打脸反派
4. 遭遇挫折，突破瓶颈
5. 最终成功，登临巅峰

---

## 核心冲突

### 主线矛盾
{conflict or template['conflict']}

### 前3章即时冲突
- 第1章: 被人看不起，遭受羞辱
- 第2章: 觉醒金手指，初露锋芒
- 第3章: 小试牛刀，打脸反派

### 中期冲突
- 遭遇强敌，陷入危机
- 突破瓶颈，实力大增
- 反败为胜，震惊四座

### 后期冲突
- 终极对决，生死之战
- 揭开真相，反转剧情
- 大结局，圆满收官

---

## 爽点设计

### 打脸节奏
- 每3章一次小打脸
- 每10章一次大打脸
- 每30章一次超级打脸

### 升级频率
- 每5章一个小突破
- 每20章一个大境界
- 每50章一次质的飞跃

### 装逼方式
- 扮猪吃虎，实力碾压
- 众人震惊，反派后悔
- 美女倾心，兄弟佩服

---

## 节奏规划

### 第1-10章: 开篇崛起
- 第1章: 开局低谷，遭受羞辱
- 第2章: 觉醒金手指，开始逆袭
- 第3章: 小试牛刀，初露锋芒
- 第4-5章: 打脸反派，震惊众人
- 第6-10章: 建立人设，小高潮

### 第11-30章: 中期发展
- 遭遇强敌，陷入危机
- 突破瓶颈，实力大增
- 反败为胜，名声大噪

### 第31-50章: 后期高潮
- 终极对决，生死之战
- 揭开真相，反转剧情
- 大结局，圆满收官

---

## 配角框架

### 对手
- 嚣张跋扈的富二代/天才弟子
- 阴险狡诈的幕后黑手
- 实力强大的终极BOSS

### 盟友
- 忠诚的小弟/师弟
- 神秘的长者/前辈
- 实力相当的挚友

### 红颜
- 冰山美人: 高冷女神，外冷内热
- 活泼少女: 古灵精怪，天真烂漫
- 温柔师姐: 知性优雅，体贴入微

---

## 开篇钩子

### 第一章结构
1. **开场**: 主角被人看不起，遭受羞辱
2. **转折**: 觉醒金手指，获得力量
3. **高潮**: 小试牛刀，震惊众人
4. **结尾**: 留下悬念，吸引读者

### 开篇技巧
- 用强烈的冲突抓住读者
- 用金手指吸引读者
- 用打脸情节爽到读者

---

## 关键词

{', '.join(keywords) if keywords else '逆袭, 打脸, 爽文, 系统, 重生'}

---

## 商业价值评估

- **目标读者**: 18-35岁男性
- **阅读场景**: 碎片化阅读，地铁通勤
- **付费意愿**: 高（爽文读者付费意愿强）
- **商业价值**: ⭐⭐⭐⭐⭐

---

## 写作建议

1. **节奏要快**: 每2-3章一个小高潮
2. **爽点要足**: 打脸、升级、装逼不断
3. **人物要立**: 主角性格鲜明，配角有特点
4. **剧情要顺**: 逻辑自洽，不强行降智
5. **更新要稳**: 每日更新，保持热度
"""

        # 保存文件
        filepath = self.save_output(prompt_content, "prompt")

        # 记录到学习记忆
        self._write_learning("PROMPTS.md", f"\n## {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n- 题材: {theme}\n- 主角: {protagonist}\n- 金手指: {golden_finger}\n")

        return {
            "status": "success",
            "theme": theme,
            "prompt": prompt_content,
            "file": str(filepath),
            "commercial_value": "⭐⭐⭐⭐⭐"
        }

    def chapter(self, **kwargs) -> Dict:
        """生成单章节"""
        chapter_num = int(kwargs.get('num', 1))
        title = kwargs.get('title', f'第{chapter_num}章')
        outline = kwargs.get('outline', '')

        # 读取角色和地点记忆
        characters = self._read_learning("CHARACTERS.md")
        locations = self._read_learning("LOCATIONS.md")

        chapter_content = f"""# 第{chapter_num}章 {title}

## 基本信息
- 章节号: {chapter_num}
- 标题: {title}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 章节大纲

{outline or "待完善"}

---

## 前情提要

{'开篇章节' if chapter_num == 1 else "待补充"}

---

## 角色信息

{characters}

---

## 地点信息

{locations}

---

## 章节正文

[此处将由AI根据上述信息生成正文内容]

### 开场
- 场景描述
- 人物出场
- 氛围营造

### 发展
- 冲突展开
- 情节推进
- 人物互动

### 高潮
- 矛盾激化
- 关键转折
- 爽点呈现

### 结尾
- 悬念设置
- 伏笔埋设
- 引出下章

---

## 章节要点

- **情节推进**: 
- **角色互动**: 
- **爽点设计**: 
- **伏笔埋设**: 

---

## 下章预告

[待生成]

---

## 商业价值评估

- **字数**: 2000-3000字
- **爽点**: 1-2个
- **悬念**: 1个
- **商业价值**: ⭐⭐⭐⭐⭐
"""

        # 保存章节
        filename = f"第{chapter_num:03d}章_{title}.md"
        filepath = self.output_dir / filename
        filepath.write_text(chapter_content, encoding='utf-8')

        # 记录到情节记忆
        self._write_learning("PLOT_POINTS.md", f"\n## 第{chapter_num}章\n- 标题: {title}\n- 大纲: {outline}\n")

        return {
            "status": "success",
            "chapter": chapter_num,
            "title": title,
            "file": str(filepath),
            "commercial_value": "⭐⭐⭐⭐⭐"
        }

    def outline(self, **kwargs) -> Dict:
        """生成大纲"""
        theme = kwargs.get('theme', '都市')
        chapters = int(kwargs.get('chapters', 100))

        template = self.templates.get(theme, self.templates["都市"])

        outline_content = f"""# 小说大纲

## 基本信息
- 题材: {theme}
- 总章节: {chapters}
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 整体架构

### 第一卷: 崛起篇 (第1-30章)
- 主角低谷，遭受羞辱
- 觉醒金手指，开始逆袭
- 小试牛刀，打脸反派
- 建立人设，名声初显

### 第二卷: 发展篇 (第31-60章)
- 遭遇强敌，陷入危机
- 突破瓶颈，实力大增
- 反败为胜，名声大噪
- 收服小弟，建立势力

### 第三卷: 高潮篇 (第61-90章)
- 终极对决，生死之战
- 揭开真相，反转剧情
- 大战反派，拯救世界
- 登临巅峰，万人敬仰

### 第四卷: 结局篇 (第91-100章)
- 收尾剧情，圆满结局
- 感情线收束
- 伏笔揭晓
- 大结局

---

## 详细章节规划

### 第1-10章: 开篇崛起

**第1章**: 开局低谷
- 主角被人看不起
- 遭受羞辱和打击
- 觉醒金手指

**第2章**: 初露锋芒
- 小试牛刀
- 震惊众人
- 打脸反派

**第3章**: 名声初显
- 众人议论
- 反派后悔
- 美女关注

**第4-10章**: 建立人设
- 连续打脸
- 收服小弟
- 小高潮

---

## 商业价值评估

- **目标读者**: 18-35岁男性
- **付费章节**: 第30章开始
- **预计收入**: 高（爽文付费意愿强）
- **商业价值**: ⭐⭐⭐⭐⭐
"""

        # 保存大纲
        filepath = self.save_output(outline_content, "outline")

        return {
            "status": "success",
            "theme": theme,
            "chapters": chapters,
            "outline": outline_content,
            "file": str(filepath),
            "commercial_value": "⭐⭐⭐⭐⭐"
        }

    def list_templates(self) -> List[str]:
        """列出所有可用模板"""
        return list(self.templates.keys())

    def _read_learning(self, filename: str) -> str:
        """读取学习记忆"""
        filepath = self.learnings_dir / filename
        if filepath.exists():
            return filepath.read_text(encoding='utf-8')
        return "暂无记录"

    def _write_learning(self, filename: str, content: str):
        """写入学习记忆"""
        filepath = self.learnings_dir / filename
        if filepath.exists():
            existing = filepath.read_text(encoding='utf-8')
            filepath.write_text(existing + content, encoding='utf-8')
        else:
            filepath.write_text(content, encoding='utf-8')

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
    generator = NovelGenerator()

    if command == "help":
        print(generator.help())
    elif command == "prompt":
        args = parse_args(sys.argv[2:])
        result = generator.prompt(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "chapter":
        args = parse_args(sys.argv[2:])
        result = generator.chapter(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "outline":
        args = parse_args(sys.argv[2:])
        result = generator.outline(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "list":
        templates = generator.list_templates()
        print("可用模板:")
        for t in templates:
            print(f"  - {t}")
    elif command == "version":
        print("novel-generator v2.0.0 (商业级别)")
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
