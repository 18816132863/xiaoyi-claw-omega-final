#!/usr/bin/env python3
"""
BMI Calculator - 计算 BMI 和体重分类
Usage: python calculate_bmi.py --weight 75 --height 175
"""

import argparse

def calculate_bmi(weight, height):
    """计算 BMI"""
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return bmi

def get_bmi_category(bmi):
    """获取 BMI 分类"""
    if bmi < 18.5:
        return '偏瘦', '建议增加热量摄入，结合力量训练增重'
    elif bmi < 24:
        return '正常', '保持当前生活方式，继续规律运动'
    elif bmi < 28:
        return '超重', '建议适度减少热量摄入，增加有氧运动'
    else:
        return '肥胖', '建议咨询医生，制定科学减重计划'

def get_healthy_weight_range(height):
    """计算健康体重范围"""
    height_m = height / 100
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24 * (height_m ** 2)
    return min_weight, max_weight

def main():
    parser = argparse.ArgumentParser(description='BMI 计算器')
    parser.add_argument('--weight', type=float, required=True, help='体重 (kg)')
    parser.add_argument('--height', type=float, required=True, help='身高 (cm)')
    
    args = parser.parse_args()
    
    bmi = calculate_bmi(args.weight, args.height)
    category, advice = get_bmi_category(bmi)
    min_weight, max_weight = get_healthy_weight_range(args.height)
    
    print(f"\n{'='*50}")
    print(f"📊 BMI 计算结果")
    print(f"{'='*50}")
    print(f"身高：{args.height} cm")
    print(f"体重：{args.weight} kg")
    print(f"BMI: {bmi:.1f}")
    print(f"分类：{category}")
    print(f"\n💡 建议：{advice}")
    print(f"\n📏 健康体重范围：{min_weight:.1f} - {max_weight:.1f} kg")
    print(f"{'='*50}\n")
    
    # BMI 分类表
    print(f"\n📋 BMI 分类参考:")
    print(f"   < 18.5 : 偏瘦")
    print(f"   18.5-24 : 正常")
    print(f"   24-28 : 超重")
    print(f"   > 28 : 肥胖")
    print(f"\n⚠️  注意：BMI 不适用于肌肉量高的人群（如健身者、运动员）\n")

if __name__ == '__main__':
    main()
