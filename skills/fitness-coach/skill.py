#!/usr/bin/env python3
"""
Fitness Coach V2.0 - 营养与食谱定制系统

功能：
1. 食谱生成
2. 营养计算
3. 购物清单
4. 饮食记录
5. 体重管理
"""

import json
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional
import math


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class FitnessCoach:
    """健身与营养教练"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.output_dir = self.root / "reports" / "output" / "fitness"
        self.data_dir = self.root / "reports" / "fitness_data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 食材库
        self.ingredients = {
            "protein": {
                "鸡胸肉": {"protein": 31, "carbs": 0, "fat": 3.6, "calories": 165},
                "牛肉": {"protein": 26, "carbs": 0, "fat": 15, "calories": 250},
                "鸡蛋": {"protein": 13, "carbs": 1.1, "fat": 11, "calories": 155},
                "三文鱼": {"protein": 25, "carbs": 0, "fat": 13, "calories": 208},
                "豆腐": {"protein": 8, "carbs": 1.9, "fat": 4.8, "calories": 76}
            },
            "carbs": {
                "米饭": {"protein": 2.7, "carbs": 28, "fat": 0.3, "calories": 130},
                "面条": {"protein": 5, "carbs": 25, "fat": 2, "calories": 138},
                "燕麦": {"protein": 13, "carbs": 66, "fat": 7, "calories": 389},
                "红薯": {"protein": 1.6, "carbs": 20, "fat": 0.1, "calories": 86},
                "土豆": {"protein": 2, "carbs": 17, "fat": 0.1, "calories": 77}
            },
            "vegetables": {
                "西兰花": {"protein": 2.8, "carbs": 7, "fat": 0.4, "calories": 34},
                "菠菜": {"protein": 2.9, "carbs": 3.6, "fat": 0.4, "calories": 23},
                "胡萝卜": {"protein": 0.9, "carbs": 10, "fat": 0.2, "calories": 41},
                "番茄": {"protein": 0.9, "carbs": 3.9, "fat": 0.2, "calories": 18},
                "黄瓜": {"protein": 0.7, "carbs": 3.6, "fat": 0.1, "calories": 16}
            },
            "fruits": {
                "苹果": {"protein": 0.3, "carbs": 14, "fat": 0.2, "calories": 52},
                "香蕉": {"protein": 1.1, "carbs": 23, "fat": 0.3, "calories": 89},
                "橙子": {"protein": 0.9, "carbs": 12, "fat": 0.1, "calories": 47},
                "蓝莓": {"protein": 0.7, "carbs": 14, "fat": 0.3, "calories": 57}
            }
        }
        
        # 食谱模板
        self.meal_templates = {
            "breakfast": {
                "name": "早餐",
                "target_ratio": {"protein": 0.25, "carbs": 0.5, "fat": 0.25},
                "examples": [
                    "燕麦+鸡蛋+牛奶",
                    "全麦面包+鸡蛋+水果",
                    "杂粮粥+鸡蛋+蔬菜"
                ]
            },
            "lunch": {
                "name": "午餐",
                "target_ratio": {"protein": 0.35, "carbs": 0.45, "fat": 0.20},
                "examples": [
                    "鸡胸肉+米饭+西兰花",
                    "牛肉+面条+蔬菜",
                    "三文鱼+红薯+沙拉"
                ]
            },
            "dinner": {
                "name": "晚餐",
                "target_ratio": {"protein": 0.40, "carbs": 0.35, "fat": 0.25},
                "examples": [
                    "清蒸鱼+蔬菜+少量米饭",
                    "鸡胸肉沙拉",
                    "豆腐+蔬菜汤"
                ]
            }
        }
        
        # 饮食目标
        self.diet_goals = {
            "lose": {"name": "减脂", "calorie_deficit": 500, "protein_ratio": 0.35},
            "maintain": {"name": "维持", "calorie_deficit": 0, "protein_ratio": 0.25},
            "gain": {"name": "增肌", "calorie_deficit": -300, "protein_ratio": 0.30}
        }
    
    def calculate_tdee(
        self,
        weight: float,
        height: float,
        age: int,
        gender: str,
        activity_level: str = "moderate"
    ) -> Dict:
        """计算每日总能量消耗"""
        
        # BMR 计算 (Mifflin-St Jeor 公式)
        if gender.lower() == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # 活动系数
        activity_factors = {
            "sedentary": 1.2,      # 久坐
            "light": 1.375,        # 轻度活动
            "moderate": 1.55,      # 中度活动
            "active": 1.725,       # 高度活动
            "very_active": 1.9     # 非常活跃
        }
        
        factor = activity_factors.get(activity_level, 1.55)
        tdee = bmr * factor
        
        return {
            "success": True,
            "bmr": round(bmr, 0),
            "tdee": round(tdee, 0),
            "activity_level": activity_level,
            "activity_factor": factor
        }
    
    def generate_meal_plan(
        self,
        target_calories: int,
        goal: str = "maintain",
        meals_per_day: int = 3,
        preferences: List[str] = None
    ) -> Dict:
        """生成饮食计划"""
        
        result = {
            "success": False,
            "target_calories": target_calories,
            "goal": goal
        }
        
        # 获取目标配置
        goal_config = self.diet_goals.get(goal, self.diet_goals["maintain"])
        adjusted_calories = target_calories - goal_config["calorie_deficit"]
        
        # 分配每餐热量
        meal_calories = adjusted_calories // meals_per_day
        
        # 生成每餐
        meals = []
        meal_types = ["breakfast", "lunch", "dinner"][:meals_per_day]
        
        for meal_type in meal_types:
            template = self.meal_templates.get(meal_type, self.meal_templates["lunch"])
            
            meal = {
                "type": meal_type,
                "name": template["name"],
                "target_calories": meal_calories,
                "suggestions": template["examples"],
                "ingredients": self._suggest_ingredients(meal_calories, goal_config["protein_ratio"])
            }
            meals.append(meal)
        
        result["success"] = True
        result["adjusted_calories"] = adjusted_calories
        result["meals"] = meals
        result["macros"] = self._calculate_macros(adjusted_calories, goal_config["protein_ratio"])
        result["created_at"] = datetime.now().isoformat()
        
        # 保存
        self._save_plan(result)
        
        return result
    
    def _suggest_ingredients(self, calories: int, protein_ratio: float) -> List[Dict]:
        """建议食材"""
        
        suggestions = []
        
        # 蛋白质来源
        protein_calories = calories * protein_ratio
        for name, nutrition in list(self.ingredients["protein"].items())[:2]:
            suggestions.append({
                "name": name,
                "type": "蛋白质",
                "serving": f"{int(protein_calories / nutrition['calories'] * 100)}g",
                "nutrition": nutrition
            })
        
        # 碳水来源
        carbs_calories = calories * 0.4
        for name, nutrition in list(self.ingredients["carbs"].items())[:1]:
            suggestions.append({
                "name": name,
                "type": "碳水",
                "serving": f"{int(carbs_calories / nutrition['calories'] * 100)}g",
                "nutrition": nutrition
            })
        
        # 蔬菜
        for name, nutrition in list(self.ingredients["vegetables"].items())[:2]:
            suggestions.append({
                "name": name,
                "type": "蔬菜",
                "serving": "100g",
                "nutrition": nutrition
            })
        
        return suggestions
    
    def _calculate_macros(self, calories: int, protein_ratio: float) -> Dict:
        """计算宏量营养素"""
        
        protein_calories = calories * protein_ratio
        fat_calories = calories * 0.25
        carbs_calories = calories - protein_calories - fat_calories
        
        return {
            "protein": {
                "calories": int(protein_calories),
                "grams": int(protein_calories / 4)  # 1g蛋白质=4kcal
            },
            "carbs": {
                "calories": int(carbs_calories),
                "grams": int(carbs_calories / 4)  # 1g碳水=4kcal
            },
            "fat": {
                "calories": int(fat_calories),
                "grams": int(fat_calories / 9)  # 1g脂肪=9kcal
            }
        }
    
    def generate_shopping_list(self, meal_plan: Dict) -> Dict:
        """生成购物清单"""
        
        result = {
            "success": False,
            "items": []
        }
        
        # 汇总所有食材
        ingredient_totals = {}
        
        for meal in meal_plan.get("meals", []):
            for ingredient in meal.get("ingredients", []):
                name = ingredient["name"]
                if name not in ingredient_totals:
                    ingredient_totals[name] = {
                        "name": name,
                        "type": ingredient["type"],
                        "total_serving": 0,
                        "unit": "g"
                    }
                
                # 解析份量
                serving_str = ingredient.get("serving", "100g")
                serving_num = int(''.join(filter(str.isdigit, serving_str)) or 100)
                ingredient_totals[name]["total_serving"] += serving_num
        
        result["items"] = list(ingredient_totals.values())
        result["success"] = True
        result["total_items"] = len(result["items"])
        
        return result
    
    def record_meal(
        self,
        meal_type: str,
        foods: List[Dict],
        date_str: str = None
    ) -> Dict:
        """记录饮食"""
        
        result = {"success": False}
        
        # 计算总营养
        total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        
        for food in foods:
            total["calories"] += food.get("calories", 0)
            total["protein"] += food.get("protein", 0)
            total["carbs"] += food.get("carbs", 0)
            total["fat"] += food.get("fat", 0)
        
        # 记录
        record = {
            "date": date_str or str(date.today()),
            "meal_type": meal_type,
            "foods": foods,
            "total": total,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存
        record_file = self.data_dir / f"meal_record_{date.today().isoformat()}.jsonl"
        with open(record_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        result["success"] = True
        result["record"] = record
        result["message"] = f"{meal_type}记录成功"
        
        return result
    
    def _save_plan(self, plan: Dict):
        """保存计划"""
        filename = f"meal_plan_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = self.output_dir / filename
        filepath.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding='utf-8')
        plan["saved_to"] = str(filepath)
    
    def list_ingredients(self) -> Dict:
        """列出所有食材"""
        return self.ingredients
    
    def list_goals(self) -> List[Dict]:
        """列出所有目标"""
        return [
            {"id": k, "name": v["name"], "description": f"{'减少' if v['calorie_deficit'] > 0 else '增加'}{abs(v['calorie_deficit'])}kcal"}
            for k, v in self.diet_goals.items()
        ]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Fitness Coach V2.0")
    parser.add_argument("action", choices=["tdee", "plan", "shopping", "record", "ingredients", "goals"], help="操作类型")
    parser.add_argument("--weight", type=float, help="体重(kg)")
    parser.add_argument("--height", type=float, help="身高(cm)")
    parser.add_argument("--age", type=int, help="年龄")
    parser.add_argument("--gender", help="性别(male/female)")
    parser.add_argument("--calories", type=int, help="目标热量")
    parser.add_argument("--goal", default="maintain", help="目标(lose/maintain/gain)")
    args = parser.parse_args()
    
    root = get_project_root()
    coach = FitnessCoach(root)
    
    if args.action == "tdee":
        if not all([args.weight, args.height, args.age, args.gender]):
            print("请提供: --weight 体重 --height 身高 --age 年龄 --gender 性别")
            return 1
        
        result = coach.calculate_tdee(args.weight, args.height, args.age, args.gender)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "plan":
        if not args.calories:
            print("请提供: --calories 目标热量")
            return 1
        
        result = coach.generate_meal_plan(args.calories, args.goal)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "shopping":
        # 从最近的计划生成购物清单
        plan_files = list(root.glob("reports/output/fitness/meal_plan_*.json"))
        if not plan_files:
            print("请先生成饮食计划")
            return 1
        
        latest_plan = json.loads(plan_files[-1].read_text(encoding='utf-8'))
        result = coach.generate_shopping_list(latest_plan)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "ingredients":
        ingredients = coach.list_ingredients()
        print(json.dumps(ingredients, ensure_ascii=False, indent=2))
        
    elif args.action == "goals":
        goals = coach.list_goals()
        print(json.dumps(goals, ensure_ascii=False, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
