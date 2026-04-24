#!/usr/bin/env python3
"""持续改进脚本 V1.0.0

自动执行改进任务：
1. 激活更多技能
2. 压缩索引
3. 运行测试
4. 生成报告
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def activate_skills():
    """激活技能"""
    reg_path = Path('infrastructure/inventory/skill_registry.json')
    with open(reg_path) as f:
        reg = json.load(f)
    
    skills = reg.get('skills', {})
    
    # 按优先级激活技能
    priority_skills = [
        # P0 - 核心必需
        'docx', 'pdf', 'cron', 'file-manager', 'git',
        # P1 - 高频使用
        'xiaoyi-web-search', 'xiaoyi-image-understanding', 'find-skills',
        'memory-setup', 'llm-memory-integration',
        # P2 - 专业领域
        'article-writer', 'copywriter', 'ceo-advisor', 'brainstorming',
        # P3 - 工具类
        'pptx', 'xlsx', 'markitdown', 'canvas-design',
    ]
    
    activated = 0
    for skill_name in priority_skills:
        if skill_name in skills and not skills[skill_name].get('callable'):
            skills[skill_name]['callable'] = True
            skills[skill_name]['routable'] = True
            activated += 1
    
    with open(reg_path, 'w') as f:
        json.dump(reg, f, indent=2)
    
    total = len(skills)
    active = sum(1 for s in skills.values() if s.get('callable', False))
    
    return {
        'newly_activated': activated,
        'total_active': active,
        'total_skills': total,
        'activation_rate': round(active / total * 100, 1)
    }

def compress_index():
    """压缩索引"""
    kw_path = Path('memory_context/index/keyword_index.json')
    if not kw_path.exists():
        return {'error': '索引文件不存在'}
    
    with open(kw_path) as f:
        kw = json.load(f)
    
    original_size = kw_path.stat().st_size
    
    # 只保留高频关键词
    filtered = {k: v for k, v in kw.items() if isinstance(v, list) and len(v) > 100}
    
    with open(kw_path, 'w') as f:
        json.dump(filtered, f, separators=(',', ':'))
    
    new_size = kw_path.stat().st_size
    
    return {
        'original_keywords': len(kw),
        'filtered_keywords': len(filtered),
        'original_size_kb': round(original_size / 1024, 1),
        'new_size_kb': round(new_size / 1024, 1),
        'reduction': round((1 - new_size / original_size) * 100, 1)
    }

def run_tests():
    """运行测试"""
    test_path = Path('tests/test_architecture.py')
    if not test_path.exists():
        return {'error': '测试文件不存在'}
    
    result = subprocess.run(
        ['python', str(test_path)],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    return {
        'passed': 'OK' in result.stdout,
        'output': result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
    }

def generate_report(results: dict):
    """生成报告"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'results': results
    }
    
    report_path = Path('reports/improvement_report.json')
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return str(report_path)

def main():
    print("=" * 50)
    print("持续改进脚本 V1.0.0")
    print("=" * 50)
    
    results = {}
    
    # 1. 激活技能
    print("\n1. 激活技能...")
    results['skills'] = activate_skills()
    print(f"   活跃技能: {results['skills']['total_active']}/{results['skills']['total_skills']} ({results['skills']['activation_rate']}%)")
    
    # 2. 压缩索引
    print("\n2. 压缩索引...")
    results['index'] = compress_index()
    if 'error' not in results['index']:
        print(f"   索引大小: {results['index']['original_size_kb']}KB -> {results['index']['new_size_kb']}KB ({results['index']['reduction']}% 减少)")
    
    # 3. 运行测试
    print("\n3. 运行测试...")
    results['tests'] = run_tests()
    print(f"   测试结果: {'✅ 通过' if results['tests'].get('passed') else '❌ 失败'}")
    
    # 4. 生成报告
    print("\n4. 生成报告...")
    report_path = generate_report(results)
    print(f"   报告路径: {report_path}")
    
    print("\n" + "=" * 50)
    print("改进完成！")

if __name__ == '__main__':
    main()
