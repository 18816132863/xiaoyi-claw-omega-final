#!/usr/bin/env python3
"""
检查 AI 模型 API 配置状态
"""

import os
import sys

def check_xiaoyienv():
    """读取 .xiaoyienv 文件"""
    env_path = os.path.expanduser("~/.openclaw/.xiaoyienv")
    env_dict = {}
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_dict[key.strip()] = value.strip()
    except FileNotFoundError:
        pass
    
    return env_dict

def check_api_status():
    """检查所有 API 配置状态"""
    
    env = check_xiaoyienv()
    os.environ.update(env)
    
    results = []
    
    # 1. 即梦AI (小艺内置)
    seedream_keys = ['PERSONAL-API-KEY', 'PERSONAL-UID', 'SERVICE_URL']
    seedream_ok = all(os.environ.get(k) for k in seedream_keys)
    results.append({
        'name': '即梦AI (Seedream)',
        'status': '✅ 已配置' if seedream_ok else '❌ 未配置',
        'keys': seedream_keys,
        'note': '小艺内置，图像生成首选'
    })
    
    # 2. 阿里云 Wan
    wan_key = 'DASHSCOPE_API_KEY'
    wan_ok = bool(os.environ.get(wan_key))
    results.append({
        'name': 'Wan 万相 (阿里云)',
        'status': '✅ 已配置' if wan_ok else '❌ 未配置',
        'keys': [wan_key],
        'note': '视频生成首选，申请: https://dashscope.console.aliyun.com/'
    })
    
    # 3. PixVerse
    pixverse_key = 'PIXVERSE_API_KEY'
    pixverse_ok = bool(os.environ.get(pixverse_key))
    results.append({
        'name': 'PixVerse V6 (爱诗科技)',
        'status': '✅ 已配置' if pixverse_ok else '❌ 未配置',
        'keys': [pixverse_key],
        'note': '视频生成备选，申请: https://pixverse.ai'
    })
    
    # 4. 腾讯混元
    tencent_keys = ['TENCENT_SECRET_ID', 'TENCENT_SECRET_KEY']
    tencent_ok = all(os.environ.get(k) for k in tencent_keys)
    results.append({
        'name': '腾讯混元图像 3.0',
        'status': '✅ 已配置' if tencent_ok else '❌ 未配置',
        'keys': tencent_keys,
        'note': '图像编辑/超分，申请: https://console.cloud.tencent.com/cam/capi'
    })
    
    return results

def main():
    print("=" * 60)
    print("AI 模型 API 配置状态检查")
    print("=" * 60)
    print()
    
    results = check_api_status()
    
    configured = 0
    for r in results:
        print(f"【{r['name']}】")
        print(f"  状态: {r['status']}")
        print(f"  所需: {', '.join(r['keys'])}")
        print(f"  说明: {r['note']}")
        print()
        
        if '✅' in r['status']:
            configured += 1
    
    print("=" * 60)
    print(f"已配置: {configured}/{len(results)} 个模型")
    print("=" * 60)
    
    # 使用建议
    print("\n使用建议:")
    
    if configured == 0:
        print("  ⚠️ 未配置任何模型，请至少配置一个")
        print("  推荐: 即梦AI (小艺内置，无需额外申请)")
    elif configured < len(results):
        print("  💡 部分模型已配置，可正常使用")
        print("  💡 建议配置更多模型以获得降级保障")
    else:
        print("  ✅ 所有模型已配置，可自由选择使用")

if __name__ == "__main__":
    main()
