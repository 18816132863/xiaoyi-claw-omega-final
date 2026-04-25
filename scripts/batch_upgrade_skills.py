from pathlib import Path
#!/usr/bin/env python3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
"""
批量升级所有技能到专业文档水平
"""

import os
import subprocess

# 需要升级的技能列表
SKILLS = [
    {
        'name': 'copywriter',
        'title': '短视频脚本',
        'icon': '🎬',
        'color': 'FF6B6B'
    },
    {
        'name': 'novel-generator',
        'title': '小说创作',
        'icon': '📚',
        'color': '9B59B6'
    },
    {
        'name': 'fitness-coach',
        'title': '减脂食谱',
        'icon': '🥗',
        'color': '27AE60'
    },
    {
        'name': 'doc-autofill',
        'title': '周报生成',
        'icon': '📄',
        'color': '3498DB'
    },
    {
        'name': 'xiaoyi-health',
        'title': '健康评估',
        'icon': '🏥',
        'color': 'E74C3C'
    }
]

def create_skill_structure(skill):
    """创建技能目录结构"""
    skill_dir = f'str(PROJECT_ROOT)/skills/{skill["name"]}'
    
    # 创建必要的目录
    dirs = [
        'output',
        'templates',
        'assets',
        'scripts'
    ]
    
    for d in dirs:
        os.makedirs(os.path.join(skill_dir, d), exist_ok=True)
    
    print(f"✅ {skill['name']} 目录结构已创建")

def main():
    print("=" * 60)
    print("批量升级技能到专业文档水平")
    print("=" * 60)
    print()
    
    for skill in SKILLS:
        create_skill_structure(skill)
    
    print()
    print("=" * 60)
    print("✅ 所有技能目录结构已升级")
    print("=" * 60)
    print()
    print("接下来需要为每个技能创建专业的文档生成脚本")
    print("已完成的技能：")
    print("  ✅ copywriter - 短视频脚本")
    print("  ✅ data-tracker - 健康数据周报")
    print()
    print("待升级的技能：")
    print("  ⏳ novel-generator - 小说创作")
    print("  ⏳ fitness-coach - 减脂食谱")
    print("  ⏳ doc-autofill - 周报生成")
    print("  ⏳ xiaoyi-health - 健康评估")

if __name__ == '__main__':
    main()
