from pathlib import Path
#!/usr/bin/env python3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
"""
批量升级技能到专业文档水平
"""

import os
import shutil

# 需要升级的技能列表
SKILLS_TO_UPGRADE = [
    'copywriter',
    'novel-generator',
    'fitness-coach',
    'doc-autofill',
    'data-tracker',
    'xiaoyi-health'
]

def upgrade_skill(skill_name):
    """升级单个技能"""
    skill_dir = f'str(PROJECT_ROOT)/skills/{skill_name}'
    
    if not os.path.exists(skill_dir):
        print(f"⚠️  技能目录不存在: {skill_name}")
        return
    
    # 创建输出目录
    output_dir = os.path.join(skill_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建模板目录
    templates_dir = os.path.join(skill_dir, 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # 创建资源目录
    assets_dir = os.path.join(skill_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    print(f"✅ {skill_name} 目录结构已创建")

def main():
    print("=" * 60)
    print("批量升级技能到专业文档水平")
    print("=" * 60)
    print()
    
    for skill in SKILLS_TO_UPGRADE:
        upgrade_skill(skill)
    
    print()
    print("=" * 60)
    print("✅ 所有技能目录结构已升级")
    print("=" * 60)

if __name__ == '__main__':
    main()
