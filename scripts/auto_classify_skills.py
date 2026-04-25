#!/usr/bin/env python3
"""
技能自动分类脚本 - V1.0.0

根据技能描述和名称自动分类到标准分类。
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

# 分类关键词映射
CATEGORY_KEYWORDS = {
    "ai": [
        "llm", "gpt", "claude", "ai", "agent", "embedding", "model",
        "qwen", "openai", "anthropic", "智能", "ai-powered", "ai生成"
    ],
    "search": [
        "search", "查询", "检索", "fetch", "crawl", "scraper", "抓取",
        "arxiv", "google", "baidu", "web search", "搜索"
    ],
    "image": [
        "image", "图片", "图像", "photo", "picture", "art", "绘画",
        "生成图", "图片生成", "image generation", "portrait", "视觉"
    ],
    "document": [
        "pdf", "docx", "pptx", "excel", "document", "文档", "word",
        "powerpoint", "presentation", "表格", "markdown", "md"
    ],
    "video": [
        "video", "视频", "movie", "动画", "animation", "视频生成",
        "video generation", "clip", "影片"
    ],
    "audio": [
        "audio", "语音", "tts", "speech", "voice", "音乐", "music",
        "sound", "whisper", "录音"
    ],
    "code": [
        "git", "docker", "ansible", "kubernetes", "k8s", "terraform",
        "代码", "code", "deploy", "部署", "ci/cd", "vercel"
    ],
    "data": [
        "database", "mysql", "mongodb", "postgres", "redis", "数据",
        "data", "analytics", "分析", "excel", "chart", "图表"
    ],
    "finance": [
        "stock", "股票", "crypto", "加密", "finance", "金融", "交易",
        "trading", "market", "市场", "fund", "基金", "投资"
    ],
    "ecommerce": [
        "电商", "ecommerce", "shop", "店铺", "商品", "product",
        "订单", "order", "coupon", "优惠券", "amazon", "淘宝"
    ],
    "automation": [
        "cron", "schedule", "定时", "automation", "自动化", "workflow",
        "工作流", "task", "任务"
    ],
    "communication": [
        "email", "邮件", "message", "消息", "chat", "聊天", "通知",
        "notification", "telegram", "discord", "slack"
    ],
    "memory": [
        "memory", "记忆", "知识库", "knowledge", "brain", "日记",
        "journal", "chronicle", "笔记"
    ],
    "utility": [
        "file", "文件", "manager", "管理", "backup", "备份", "工具",
        "utility", "helper", "converter", "转换"
    ],
    "writing": [
        "writing", "写作", "文章", "article", "copy", "文案", "内容",
        "content", "blog", "博客", "新闻", "news"
    ],
    "design": [
        "design", "设计", "ui", "ux", "frontend", "前端", "界面",
        "diagram", "图表", "excalidraw", "canvas"
    ],
    "security": [
        "security", "安全", "audit", "审计", "vulnerability", "漏洞",
        "clawsec", "加密", "encryption"
    ],
}

# 技能名称到分类的直接映射
NAME_CATEGORY_MAP = {
    "pdf": "document",
    "docx": "document",
    "pptx": "document",
    "cron": "automation",
    "weather": "utility",
    "crypto": "finance",
    "git": "code",
    "docker": "code",
    "ansible": "code",
    "mysql": "data",
    "mongodb": "data",
    "elasticsearch": "data",
    "tts": "audio",
    "whisper": "audio",
    "arxiv-search": "search",
    "web-search": "search",
    "image-gen": "image",
    "video-gen": "video",
    # 新增直接映射
    "sqlite": "data",
    "ocr-local": "image",
    "paddleocr-doc-parsing": "document",
    "obsidian": "memory",
    "bilibili-all-in-one": "search",
    "xiaohongshu-all-in-one": "search",
    "linkedin-api": "search",
    "spotify-player": "audio",
    "camsnap": "video",
    "screenshot": "image",
    "huawei-drive": "utility",
    "fitness-coach": "utility",
    "fasting-tracker": "utility",
    "kids-book-writer": "writing",
    "lyrical-fable": "writing",
    "poetry": "writing",
    "ceo-advisor": "ai",
    "best-minds": "ai",
    "personas": "ai",
    "natural-language-planner": "ai",
    "architecture-inspector": "utility",
    "core": "utility",
    "engines": "utility",
    "utils": "utility",
    "api-gateway": "utility",
    "command-hook": "automation",
    "browser-control": "automation",
    "ab-test-setup": "data",
    "klaviyo": "ecommerce",
    "customer-service": "communication",
    "wecom-bot-setup": "communication",
    "qq-clawbot-setup": "communication",
    "weibo-clawbot-setup": "communication",
    "weixin-clawbot-setup": "communication",
    "feishu-channel-skill": "communication",
}


def classify_skill(name: str, description: str) -> Tuple[str, float]:
    """
    根据名称和描述分类技能
    
    Returns:
        (category, confidence)
    """
    # 1. 直接名称匹配
    if name in NAME_CATEGORY_MAP:
        return NAME_CATEGORY_MAP[name], 1.0
    
    # 2. 名称关键词匹配
    name_lower = name.lower().replace("-", "").replace("_", "")
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw.replace(" ", "").replace("-", "") in name_lower:
                return cat, 0.9
    
    # 3. 描述关键词匹配
    desc_lower = description.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in desc_lower)
        if score > 0:
            scores[cat] = score
    
    if scores:
        best_cat = max(scores, key=scores.get)
        confidence = min(scores[best_cat] / 3, 1.0)  # 归一化
        return best_cat, confidence
    
    # 4. 默认分类
    return "other", 0.0


def load_skill_descriptions() -> Dict[str, str]:
    """从 SKILL.md 文件加载技能描述"""
    descriptions = {}
    skills_dir = Path("skills")
    
    if not skills_dir.exists():
        return descriptions
    
    for skill_path in skills_dir.iterdir():
        if not skill_path.is_dir():
            continue
        skill_md = skill_path / "SKILL.md"
        if skill_md.exists():
            try:
                content = skill_md.read_text(encoding='utf-8', errors='ignore')
                for line in content.split('\n'):
                    if line.startswith('description:'):
                        desc = line.replace('description:', '').strip().strip('"').strip("'")
                        if desc and not desc.startswith('|') and len(desc) > 10:
                            descriptions[skill_path.name] = desc
                            break
            except:
                pass
    
    return descriptions


def update_registry(classifications: Dict[str, Tuple[str, float]], dry_run: bool = True):
    """更新技能注册表"""
    registry_path = Path("infrastructure/inventory/skill_registry.json")
    
    if not registry_path.exists():
        print("错误: 技能注册表不存在")
        return
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = 0
    for name, (category, confidence) in classifications.items():
        if name in data.get('skills', {}):
            skill = data['skills'][name]
            if isinstance(skill, dict):
                old_cat = skill.get('category', 'other')
                if old_cat == 'other' and category != 'other' and confidence >= 0.5:
                    if not dry_run:
                        skill['category'] = category
                        skill['category_confidence'] = confidence
                    updated += 1
                    print(f"  {name}: other -> {category} (置信度: {confidence:.2f})")
    
    if not dry_run and updated > 0:
        data['updated'] = "2026-04-15"
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n已更新 {updated} 个技能分类")
    elif dry_run:
        print(f"\n[预览模式] 将更新 {updated} 个技能分类")
    
    return updated


def main():
    print("╔══════════════════════════════════════════════════╗")
    print("║          技能自动分类 V1.0.0                    ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    
    # 加载描述
    print("【加载技能描述】")
    descriptions = load_skill_descriptions()
    print(f"  已加载 {len(descriptions)} 个技能描述")
    print()
    
    # 加载注册表
    registry_path = Path("infrastructure/inventory/skill_registry.json")
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # 分类
    print("【分类技能】")
    classifications = {}
    for name, skill in registry.get('skills', {}).items():
        if isinstance(skill, dict) and skill.get('category') == 'other':
            desc = descriptions.get(name, skill.get('description', ''))
            category, confidence = classify_skill(name, desc)
            if category != 'other':
                classifications[name] = (category, confidence)
    
    print(f"  找到 {len(classifications)} 个可分类技能")
    print()
    
    # 显示分类结果
    print("【分类结果】")
    update_registry(classifications, dry_run=True)
    print()
    
    # 询问是否应用
    import sys
    if '--apply' in sys.argv:
        print("【应用更改】")
        update_registry(classifications, dry_run=False)
    else:
        print("使用 --apply 参数应用更改")


if __name__ == "__main__":
    main()
