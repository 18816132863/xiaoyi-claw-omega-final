#!/usr/bin/env python3
"""
Copywriter 技能执行脚本
支持中文文案生成、短视频脚本、营销文案、多平台适配
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class Copywriter:
    """文案生成器"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_short_video(
        self,
        type: str,
        product: str = "",
        pain_point: str = "",
        effect: str = "",
        theme: str = "",
        points: List[str] = None,
        resonance: str = "",
        emotion: str = "",
        insight: str = ""
    ) -> Dict:
        """生成短视频脚本"""
        
        if type == "产品种草":
            script = f"""【开场】(3秒)
- 画面: {product}特写
- 文案: "这个{product}真的绝了！"

【痛点】(5秒)
- 画面: 使用前对比
- 文案: "你是不是也遇到过{pain_point}？"

【解决方案】(10秒)
- 画面: 产品使用过程
- 文案: "用了这个之后，{effect}"

【信任背书】(5秒)
- 画面: 用户评价/数据
- 文案: "已经有数万人都在用"

【行动号召】(3秒)
- 画面: 购买链接/优惠信息
- 文案: "现在下单还有限时优惠，点击下方链接"
"""
        elif type == "知识科普":
            points_str = "\n".join([f"- 要点{i+1}: {p}" for i, p in enumerate(points or [])])
            script = f"""【悬念开场】(3秒)
- 文案: "你知道吗？{theme}"

【引入主题】(5秒)
- 文案: "今天我们来聊聊{theme}"

【核心内容】(15秒)
{points_str}

【总结升华】(5秒)
- 文案: "所以记住，{insight}"

【互动引导】(3秒)
- 文案: "你还有什么想了解的？评论区告诉我"
"""
        elif type == "情感共鸣":
            script = f"""【场景切入】(5秒)
- 画面: 生活场景
- 文案: "有没有人和我一样，{resonance}"

【情感铺垫】(10秒)
- 画面: 情感画面
- 文案: "{emotion}"

【转折升华】(5秒)
- 画面: 正能量画面
- 文案: "但是后来我发现，{insight}"

【行动号召】(3秒)
- 文案: "如果你也有同感，点个赞吧"
"""
        else:
            script = "未知类型，请选择: 产品种草、知识科普、情感共鸣"
        
        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"short_video_{timestamp}.md"
        filepath = self.output_dir / filename
        filepath.write_text(script, encoding='utf-8')
        
        return {
            "status": "success",
            "type": type,
            "script": script,
            "file": str(filepath)
        }
    
    def generate_marketing(
        self,
        platform: str,
        product: str,
        target: str = "",
        selling_points: List[str] = None,
        price: str = "",
        discount: str = "",
        activity: str = "",
        date: str = "",
        location: str = "",
        gift: str = ""
    ) -> Dict:
        """生成营销文案"""
        
        if platform == "小红书":
            points_str = "\n".join([f"✨ {p}" for p in (selling_points or [])])
            copy = f"""{product}真的太好用了！
用了几天，效果肉眼可见：
{points_str}
推荐给{target}～

#好物推荐 #{product}
"""
        elif platform == "朋友圈":
            copy = f"""🎉 {activity}来啦！
📅 时间: {date}
📍 地点: {location}
🎁 福利: {discount}
名额有限，先到先得！

#活动 #{product}
"""
        elif platform == "电商详情页":
            points_str = "\n".join([f"- {p}" for p in (selling_points or [])])
            copy = f"""【标题】
{product} - {selling_points[0] if selling_points else ''} | {target}

【产品介绍】
{product} 专为{target}设计：
{points_str}

【限时优惠】
🔥 原价 {price}
⚡ 现价 {discount}
🎁 赠送 {gift}
"""
        else:
            copy = f"平台 {platform} 暂不支持，请选择: 小红书、朋友圈、电商详情页"
        
        # 保存到文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"marketing_{platform}_{timestamp}.md"
        filepath = self.output_dir / filename
        filepath.write_text(copy, encoding='utf-8')
        
        return {
            "status": "success",
            "platform": platform,
            "copy": copy,
            "file": str(filepath)
        }
    
    def generate_ab_variants(
        self,
        original: str,
        type: str = "标题",
        count: int = 3
    ) -> Dict:
        """生成A/B测试变体"""
        
        variants = []
        
        if type == "标题":
            # 基于原标题生成变体
            variants = [
                f"3个方法，帮你解决{original.replace('如何', '').replace('？', '')}",
                f"{original.replace('如何', '').replace('？', '')}？试试这个方法",
                f"别再纠结了！{original.replace('如何', '').replace('？', '')}这样做就够了"
            ][:count]
        elif type == "开场":
            variants = [
                f"说实话，我也曾经{original}",
                f"今天要分享一个秘密：{original}",
                f"很多人不知道的是，{original}"
            ][:count]
        elif type == "CTA":
            variants = [
                f"现在下单，立享8折",
                f"限时优惠，手慢无",
                f"扫码领取专属优惠"
            ][:count]
        
        return {
            "status": "success",
            "type": type,
            "original": original,
            "variants": variants,
            "count": len(variants)
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return 1
    
    command = sys.argv[1]
    copywriter = Copywriter()
    
    if command == "help":
        print_help()
    elif command == "short-video":
        # python skill.py short-video --type 产品种草 --product 智能水杯 --pain-point 总是忘记喝水 --effect 每天自动提醒
        args = parse_args(sys.argv[2:])
        result = copywriter.generate_short_video(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "marketing":
        # python skill.py marketing --platform 小红书 --product 护肤精华 --target 25-35岁女性 --selling-points 补水,抗衰,提亮
        args = parse_args(sys.argv[2:])
        if 'selling_points' in args and isinstance(args['selling_points'], str):
            args['selling_points'] = args['selling_points'].split(',')
        result = copywriter.generate_marketing(**args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif command == "ab-test":
        # python skill.py ab-test --original "如何提高工作效率？" --type 标题 --count 3
        args = parse_args(sys.argv[2:])
        result = copywriter.generate_ab_variants(**args)
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
    print("""Copywriter 技能 - 中文文案生成器

命令:
  help          显示帮助
  short-video   生成短视频脚本
  marketing     生成营销文案
  ab-test       生成A/B测试变体

示例:
  # 生成产品种草短视频
  python skill.py short-video --type 产品种草 --product 智能水杯 --pain-point 总是忘记喝水 --effect 每天自动提醒

  # 生成小红书文案
  python skill.py marketing --platform 小红书 --product 护肤精华 --target 25-35岁女性 --selling-points 补水,抗衰,提亮

  # 生成标题变体
  python skill.py ab-test --original "如何提高工作效率？" --type 标题 --count 3

支持的平台:
  - 小红书
  - 朋友圈
  - 电商详情页
  - 抖音
  - B站
  - 公众号

支持的短视频类型:
  - 产品种草
  - 知识科普
  - 情感共鸣
""")


if __name__ == "__main__":
    sys.exit(main())
