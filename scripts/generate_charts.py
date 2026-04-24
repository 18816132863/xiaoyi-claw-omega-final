from pathlib import Path
import os
#!/usr/bin/env python3

PROJECT_ROOT = Path(__file__).resolve().parents[1]
"""
生成专业图表
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配色方案
COLORS = {
    'primary': '#0078D4',
    'success': '#107C10',
    'warning': '#FF8C00',
    'danger': '#D13438',
    'gray': '#605E5C',
    'lightGray': '#D2D0CE',
    'chart1': '#0078D4',
    'chart2': '#107C10',
    'chart3': '#FF8C00',
    'chart4': '#8764B8',
    'chart5': '#E74856'
}

def create_sleep_trend_chart():
    """睡眠趋势图"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    sleep_data = [7.5, 6.8, 7.2, 7.0, 7.8, 7.5, 6.5]
    
    # 绘制折线图
    ax.plot(days, sleep_data, marker='o', linewidth=3, markersize=10, 
            color=COLORS['primary'], label='Sleep Duration')
    ax.fill_between(days, sleep_data, alpha=0.2, color=COLORS['primary'])
    
    # 目标线
    ax.axhline(y=7.5, color=COLORS['success'], linestyle='--', linewidth=2, 
               label='Target: 7.5h')
    
    # 设置样式
    ax.set_ylabel('Hours', fontsize=12, fontweight='bold')
    ax.set_title('Weekly Sleep Trend', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(5, 9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='upper right', fontsize=10)
    
    # 添加数值标签
    for i, (day, val) in enumerate(zip(days, sleep_data)):
        ax.annotate(f'{val}h', (day, val), textcoords="offset points", 
                   xytext=(0, 10), ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('str(PROJECT_ROOT)/skills/data-tracker/output/sleep_trend.png', 
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ 睡眠趋势图已生成")

def create_steps_bar_chart():
    """步数柱状图"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    steps_data = [8500, 7200, 12300, 9100, 8800, 5200, 7800]
    
    # 根据是否达标设置颜色
    colors = [COLORS['primary'] if x >= 8000 else COLORS['warning'] for x in steps_data]
    
    # 绘制柱状图
    bars = ax.bar(days, steps_data, color=colors, alpha=0.8, width=0.6)
    
    # 目标线
    ax.axhline(y=8000, color=COLORS['success'], linestyle='--', linewidth=2, 
               label='Target: 8,000 steps')
    
    # 设置样式
    ax.set_ylabel('Steps', fontsize=12, fontweight='bold')
    ax.set_title('Weekly Steps Statistics', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylim(0, 14000)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='upper right', fontsize=10)
    
    # 添加数值标签
    for bar, val in zip(bars, steps_data):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200, 
                f'{val:,}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('str(PROJECT_ROOT)/skills/data-tracker/output/steps_bar.png', 
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ 步数柱状图已生成")

def create_exercise_pie_chart():
    """运动类型饼图"""
    fig, ax = plt.subplots(figsize=(8, 8))
    
    labels = ['Running', 'Swimming', 'Strength', 'Yoga']
    sizes = [60, 45, 40, 30]
    colors = [COLORS['chart1'], COLORS['chart2'], COLORS['chart3'], COLORS['chart4']]
    explode = (0.05, 0.05, 0.05, 0.05)
    
    # 绘制饼图
    wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, 
                                       colors=colors, autopct='%1.0f%%',
                                       shadow=True, startangle=90,
                                       textprops={'fontsize': 12, 'fontweight': 'bold'})
    
    # 设置样式
    ax.set_title('Exercise Type Distribution (minutes)', fontsize=16, fontweight='bold', pad=20)
    ax.axis('equal')
    
    plt.tight_layout()
    plt.savefig('str(PROJECT_ROOT)/skills/data-tracker/output/exercise_pie.png', 
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ 运动饼图已生成")

def create_health_radar_chart():
    """健康维度雷达图"""
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    categories = ['Sleep\nQuality', 'Exercise\nPerformance', 'Daily\nActivity', 
                  'Nutrition', 'Stress\nManagement']
    this_week = [85, 90, 75, 80, 70]
    last_week = [78, 75, 65, 75, 68]
    
    # 计算角度
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    this_week += this_week[:1]
    last_week += last_week[:1]
    angles += angles[:1]
    
    # 绘制雷达图
    ax.plot(angles, this_week, 'o-', linewidth=2, label='This Week', color=COLORS['primary'])
    ax.fill(angles, this_week, alpha=0.25, color=COLORS['primary'])
    ax.plot(angles, last_week, 'o-', linewidth=2, label='Last Week', color=COLORS['gray'])
    ax.fill(angles, last_week, alpha=0.1, color=COLORS['gray'])
    
    # 设置样式
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9, color=COLORS['gray'])
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    
    plt.title('Health Dimension Comparison', fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('str(PROJECT_ROOT)/skills/data-tracker/output/health_radar.png', 
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("✅ 健康雷达图已生成")

if __name__ == '__main__':
    create_sleep_trend_chart()
    create_steps_bar_chart()
    create_exercise_pie_chart()
    create_health_radar_chart()
    print("\n✅ 所有图表已生成完成！")
