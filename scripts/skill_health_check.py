#!/usr/bin/env python3
"""技能健康检查 V1.0.0"""

import json
from pathlib import Path

def check_skill_health():
    """检查技能健康状态"""
    reg_path = Path('infrastructure/inventory/skill_registry.json')
    with open(reg_path) as f:
        reg = json.load(f)
    
    skills = reg.get('skills', {})
    
    results = {
        'total': len(skills),
        'active': 0,
        'inactive': 0,
        'missing_skill_md': 0,
        'missing_config': 0,
        'issues': []
    }
    
    for skill_name, skill_data in skills.items():
        if skill_data.get('callable'):
            results['active'] += 1
        else:
            results['inactive'] += 1
        
        # 检查 SKILL.md
        skill_path = Path('skills') / skill_name
        if skill_path.exists():
            if not (skill_path / 'SKILL.md').exists():
                results['missing_skill_md'] += 1
                results['issues'].append(f"{skill_name}: 缺少 SKILL.md")
            
            # 检查 config.json
            if not (skill_path / 'config.json').exists():
                results['missing_config'] += 1
    
    return results

def main():
    print("=" * 50)
    print("技能健康检查 V1.0.0")
    print("=" * 50)
    
    results = check_skill_health()
    
    print(f"\n总技能: {results['total']}")
    print(f"活跃技能: {results['active']} ({results['active']/results['total']*100:.1f}%)")
    print(f"非活跃技能: {results['inactive']}")
    print(f"缺少 SKILL.md: {results['missing_skill_md']}")
    print(f"缺少 config.json: {results['missing_config']}")
    
    if results['issues']:
        print(f"\n问题列表 (前 10 个):")
        for issue in results['issues'][:10]:
            print(f"  - {issue}")
    
    # 健康评分
    health = results['active'] / results['total']
    if health >= 0.3:
        status = "✅ 良好"
    elif health >= 0.1:
        status = "⚠️ 一般"
    else:
        status = "❌ 需改进"
    
    print(f"\n健康状态: {status}")

if __name__ == '__main__':
    main()
