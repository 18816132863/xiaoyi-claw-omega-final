#!/usr/bin/env python3
"""
TDEE Calculator - 计算每日总能量消耗
Usage: python calculate_tdee.py --weight 75 --height 175 --age 30 --gender male --activity moderate
"""

import argparse

def calculate_bmr(weight, height, age, gender):
    """Mifflin-St Jeor 公式计算 BMR"""
    if gender.lower() in ['male', '男', 'm']:
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    return bmr

def get_activity_multiplier(activity_level):
    """获取活动系数"""
    multipliers = {
        'sedentary': 1.2,      # 久坐
        'light': 1.375,        # 轻度活动
        'moderate': 1.55,      # 中度活动
        'active': 1.725,       # 高度活动
        'very_active': 1.9     # 极高活动
    }
    return multipliers.get(activity_level.lower(), 1.55)

def calculate_tdee(weight, height, age, gender, activity_level):
    """计算 TDEE"""
    bmr = calculate_bmr(weight, height, age, gender)
    multiplier = get_activity_multiplier(activity_level)
    tdee = bmr * multiplier
    return bmr, tdee

def get_goal_calories(tdee, goal):
    """根据目标调整热量"""
    adjustments = {
        'lose_fast': -500,     # 快速减脂
        'lose_moderate': -250, # 温和减脂
        'maintain': 0,         # 维持
        'gain_slow': 250,      # 缓慢增肌
        'gain_fast': 500       # 快速增肌
    }
    return tdee + adjustments.get(goal.lower(), 0)

def get_macros(weight, goal, calories):
    """计算宏量营养素"""
    if 'lose' in goal.lower():
        protein_per_kg = 2.2
        fat_per_kg = 1.0
    elif 'gain' in goal.lower():
        protein_per_kg = 1.8
        fat_per_kg = 1.0
    else:
        protein_per_kg = 1.6
        fat_per_kg = 0.9
    
    protein = protein_per_kg * weight
    fat = fat_per_kg * weight
    protein_cal = protein * 4
    fat_cal = fat * 9
    carb_cal = calories - protein_cal - fat_cal
    carbs = carb_cal / 4
    
    return {
        'protein': round(protein),
        'carbs': round(max(carbs, 100)),  # 至少 100g 碳水
        'fat': round(fat)
    }

def main():
    parser = argparse.ArgumentParser(description='TDEE 计算器')
    parser.add_argument('--weight', type=float, required=True, help='体重 (kg)')
    parser.add_argument('--height', type=float, required=True, help='身高 (cm)')
    parser.add_argument('--age', type=int, required=True, help='年龄')
    parser.add_argument('--gender', type=str, required=True, help='性别 (male/female)')
    parser.add_argument('--activity', type=str, default='moderate', 
                        help='活动水平 (sedentary/light/moderate/active/very_active)')
    parser.add_argument('--goal', type=str, default='maintain',
                        help='目标 (lose_fast/lose_moderate/maintain/gain_slow/gain_fast)')
    
    args = parser.parse_args()
    
    bmr, tdee = calculate_tdee(args.weight, args.height, args.age, args.gender, args.activity)
    goal_calories = get_goal_calories(tdee, args.goal)
    macros = get_macros(args.weight, args.goal, goal_calories)
    
    print(f"\n{'='*50}")
    print(f"📊 TDEE 计算结果")
    print(f"{'='*50}")
    print(f"基础代谢 (BMR): {bmr:.0f} kcal/天")
    print(f"每日消耗 (TDEE): {tdee:.0f} kcal/天")
    print(f"目标热量 ({args.goal}): {goal_calories:.0f} kcal/天")
    print(f"\n🍽️  宏量营养素建议:")
    print(f"   蛋白质：{macros['protein']}g ({macros['protein']*4} kcal)")
    print(f"   碳水化合物：{macros['carbs']}g ({macros['carbs']*4} kcal)")
    print(f"   脂肪：{macros['fat']}g ({macros['fat']*9} kcal)")
    print(f"{'='*50}\n")

if __name__ == '__main__':
    main()
