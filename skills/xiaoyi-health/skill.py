#!/usr/bin/env python3
"""
Xiaoyi Health V2.0 - AI健康监控与诊断系统

功能：
1. 症状分析
2. 健康风险评估
3. 中医体质辨识
4. 用药提醒
5. 健康趋势分析
6. 算命娱乐功能
"""

import json
import sys
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional
import random


def get_project_root() -> Path:
    """获取项目根目录"""
    current = Path(__file__).resolve().parent.parent.parent
    if (current / 'core' / 'ARCHITECTURE.md').exists():
        return current
    return Path(__file__).resolve().parent.parent.parent


class HealthAdvisor:
    """健康顾问"""
    
    def __init__(self, root: Path = None):
        self.root = root or get_project_root()
        self.output_dir = self.root / "reports" / "output" / "health"
        self.data_dir = self.root / "reports" / "health_data"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 症状库
        self.symptoms = {
            "headache": {
                "name": "头痛",
                "possible_causes": ["睡眠不足", "压力过大", "用眼过度", "颈椎问题", "血压异常"],
                "severity_levels": ["轻微", "中度", "严重"],
                "suggestions": ["保证充足睡眠", "减少屏幕时间", "适当休息", "如持续请就医"]
            },
            "fatigue": {
                "name": "疲劳",
                "possible_causes": ["睡眠质量差", "营养不均衡", "缺乏运动", "心理压力", "潜在疾病"],
                "severity_levels": ["轻微", "中度", "严重"],
                "suggestions": ["规律作息", "均衡饮食", "适度运动", "如持续请就医"]
            },
            "insomnia": {
                "name": "失眠",
                "possible_causes": ["焦虑", "咖啡因", "作息不规律", "环境因素", "心理问题"],
                "severity_levels": ["偶尔", "经常", "长期"],
                "suggestions": ["睡前放松", "减少咖啡因", "规律作息", "如严重请就医"]
            },
            "digestive": {
                "name": "消化不良",
                "possible_causes": ["饮食不当", "压力", "食物不耐受", "胃部疾病"],
                "severity_levels": ["轻微", "中度", "严重"],
                "suggestions": ["清淡饮食", "细嚼慢咽", "规律进餐", "如持续请就医"]
            }
        }
        
        # 中医体质
        self.constitution_types = {
            "balanced": {
                "name": "平和质",
                "description": "阴阳气血调和，体态适中、面色红润",
                "characteristics": ["精力充沛", "睡眠良好", "适应力强"],
                "percentage": 30
            },
            "qi_deficiency": {
                "name": "气虚质",
                "description": "元气不足，容易疲乏、气短",
                "characteristics": ["易疲劳", "声音低弱", "易出汗"],
                "percentage": 15
            },
            "yang_deficiency": {
                "name": "阳虚质",
                "description": "阳气不足，怕冷、手足不温",
                "characteristics": ["怕冷", "喜热饮", "精神不振"],
                "percentage": 10
            },
            "yin_deficiency": {
                "name": "阴虚质",
                "description": "阴液亏少，口燥咽干、手足心热",
                "characteristics": ["口干", "手足心热", "大便干燥"],
                "percentage": 10
            },
            "phlegm_dampness": {
                "name": "痰湿质",
                "description": "痰湿凝聚，体形肥胖、腹部肥满",
                "characteristics": ["体形肥胖", "腹部肥满", "口黏"],
                "percentage": 10
            },
            "damp_heat": {
                "name": "湿热质",
                "description": "湿热内蕴，面垢油光、易生痤疮",
                "characteristics": ["面油", "易长痘", "口苦"],
                "percentage": 10
            },
            "blood_stasis": {
                "name": "血瘀质",
                "description": "血行不畅，肤色晦暗、易有瘀斑",
                "characteristics": ["肤色暗", "易瘀青", "疼痛固定"],
                "percentage": 5
            },
            "qi_stagnation": {
                "name": "气郁质",
                "description": "气机郁滞，情绪低落、易焦虑",
                "characteristics": ["情绪波动", "胸闷", "叹气"],
                "percentage": 5
            },
            "special": {
                "name": "特禀质",
                "description": "先天失常，过敏体质",
                "characteristics": ["易过敏", "喷嚏", "皮肤敏感"],
                "percentage": 5
            }
        }
        
        # 健康指标范围
        self.health_ranges = {
            "blood_pressure": {
                "name": "血压",
                "normal": {"systolic": (90, 120), "diastolic": (60, 80)},
                "warning": {"systolic": (120, 140), "diastolic": (80, 90)},
                "danger": {"systolic": (140, 200), "diastolic": (90, 120)}
            },
            "heart_rate": {
                "name": "心率",
                "normal": (60, 100),
                "warning": (100, 120),
                "danger": (120, 200)
            },
            "blood_sugar": {
                "name": "血糖",
                "normal": (3.9, 6.1),
                "warning": (6.1, 7.0),
                "danger": (7.0, 20.0)
            },
            "bmi": {
                "name": "BMI",
                "normal": (18.5, 24),
                "warning": (24, 28),
                "danger": (28, 40)
            }
        }
    
    def analyze_symptoms(
        self,
        symptoms: List[str],
        duration: str = "recent",
        severity: str = "moderate"
    ) -> Dict:
        """分析症状"""
        
        result = {
            "success": False,
            "symptoms": symptoms,
            "analysis": []
        }
        
        for symptom_key in symptoms:
            symptom_info = self.symptoms.get(symptom_key)
            if symptom_info:
                analysis = {
                    "symptom": symptom_info["name"],
                    "possible_causes": symptom_info["possible_causes"],
                    "severity": severity,
                    "suggestions": symptom_info["suggestions"],
                    "disclaimer": "此分析仅供参考，如有不适请及时就医"
                }
                result["analysis"].append(analysis)
        
        result["success"] = True
        result["duration"] = duration
        result["created_at"] = datetime.now().isoformat()
        
        # 保存
        self._save_analysis(result)
        
        return result
    
    def assess_constitution(
        self,
        answers: Dict[str, int]
    ) -> Dict:
        """中医体质辨识"""
        
        result = {
            "success": False,
            "answers": answers
        }
        
        # 简化计算：根据答案分数判断体质
        total_score = sum(answers.values())
        
        # 匹配体质
        if total_score <= 10:
            constitution = self.constitution_types["balanced"]
        elif total_score <= 20:
            constitution = self.constitution_types["qi_deficiency"]
        elif total_score <= 30:
            constitution = self.constitution_types["yang_deficiency"]
        else:
            constitution = self.constitution_types["yin_deficiency"]
        
        result["success"] = True
        result["constitution"] = {
            "type": constitution["name"],
            "description": constitution["description"],
            "characteristics": constitution["characteristics"],
            "population_percentage": f"约{constitution['percentage']}%人群"
        }
        result["suggestions"] = self._get_constitution_suggestions(constitution)
        result["disclaimer"] = "此辨识仅供参考，具体请咨询中医师"
        
        return result
    
    def _get_constitution_suggestions(self, constitution: Dict) -> List[str]:
        """获取体质调理建议"""
        
        suggestions_map = {
            "平和质": ["保持现有良好习惯", "均衡饮食", "适度运动"],
            "气虚质": ["多吃益气食物（山药、红枣）", "避免过度劳累", "适度运动"],
            "阳虚质": ["多吃温热食物（羊肉、生姜）", "注意保暖", "避免寒凉"],
            "阴虚质": ["多吃滋阴食物（银耳、百合）", "避免辛辣", "保持心情平和"],
            "痰湿质": ["清淡饮食", "加强运动", "控制体重"],
            "湿热质": ["清热祛湿食物（绿豆、薏米）", "少油腻", "保持大便通畅"],
            "血瘀质": ["活血化瘀食物（山楂、桃仁）", "适度运动", "保持心情舒畅"],
            "气郁质": ["疏肝解郁食物（玫瑰花、柑橘）", "多户外活动", "调节情绪"],
            "特禀质": ["避免过敏原", "增强体质", "注意饮食"]
        }
        
        return suggestions_map.get(constitution["name"], ["请咨询专业医师"])
    
    def analyze_health_metrics(
        self,
        metrics: Dict[str, float]
    ) -> Dict:
        """分析健康指标"""
        
        result = {
            "success": False,
            "metrics": metrics,
            "analysis": []
        }
        
        for metric_key, value in metrics.items():
            range_info = self.health_ranges.get(metric_key)
            if range_info:
                if metric_key == "blood_pressure":
                    # 血压特殊处理
                    systolic = value.get("systolic", 120)
                    diastolic = value.get("diastolic", 80)
                    
                    if range_info["normal"]["systolic"][0] <= systolic <= range_info["normal"]["systolic"][1]:
                        status = "正常"
                    elif range_info["warning"]["systolic"][0] <= systolic <= range_info["warning"]["systolic"][1]:
                        status = "偏高"
                    else:
                        status = "异常"
                    
                    analysis = {
                        "metric": range_info["name"],
                        "value": f"{systolic}/{diastolic} mmHg",
                        "status": status,
                        "normal_range": f"{range_info['normal']['systolic'][0]}-{range_info['normal']['systolic'][1]}/{range_info['normal']['diastolic'][0]}-{range_info['normal']['diastolic'][1]}"
                    }
                else:
                    # 其他指标
                    normal_range = range_info["normal"]
                    warning_range = range_info["warning"]
                    
                    if normal_range[0] <= value <= normal_range[1]:
                        status = "正常"
                    elif warning_range[0] <= value <= warning_range[1]:
                        status = "偏高" if value > normal_range[1] else "偏低"
                    else:
                        status = "异常"
                    
                    analysis = {
                        "metric": range_info["name"],
                        "value": value,
                        "status": status,
                        "normal_range": f"{normal_range[0]}-{normal_range[1]}"
                    }
                
                result["analysis"].append(analysis)
        
        result["success"] = True
        result["overall_status"] = self._calculate_overall_status(result["analysis"])
        result["created_at"] = datetime.now().isoformat()
        
        return result
    
    def _calculate_overall_status(self, analysis: List[Dict]) -> str:
        """计算整体状态"""
        abnormal_count = sum(1 for a in analysis if a["status"] != "正常")
        
        if abnormal_count == 0:
            return "健康"
        elif abnormal_count <= 2:
            return "需关注"
        else:
            return "建议就医"
    
    def fortune_telling(
        self,
        birth_date: str,
        question: str = "general"
    ) -> Dict:
        """算命娱乐功能"""
        
        result = {
            "success": True,
            "disclaimer": "仅供娱乐，请勿当真",
            "birth_date": birth_date,
            "question_type": question
        }
        
        # 生成随机运势
        fortunes = [
            "大吉大利，今日宜行动",
            "平稳发展，保持现状",
            "小有波折，谨慎行事",
            "贵人相助，把握机会",
            "静待时机，不宜冒进"
        ]
        
        lucky_items = [
            "红色", "东方", "数字3", "水", "木"
        ]
        
        result["fortune"] = random.choice(fortunes)
        result["lucky"] = {
            "color": random.choice(lucky_items),
            "direction": random.choice(["东", "南", "西", "北"]),
            "number": random.randint(1, 9)
        }
        result["advice"] = "保持积极心态，好运自然来"
        
        return result
    
    def _save_analysis(self, analysis: Dict):
        """保存分析结果"""
        filename = f"health_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.output_dir / filename
        filepath.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding='utf-8')
        analysis["saved_to"] = str(filepath)
    
    def list_symptoms(self) -> List[Dict]:
        """列出所有症状"""
        return [
            {"id": k, "name": v["name"], "causes": v["possible_causes"]}
            for k, v in self.symptoms.items()
        ]
    
    def list_constitutions(self) -> List[Dict]:
        """列出所有体质类型"""
        return [
            {"id": k, "name": v["name"], "description": v["description"]}
            for k, v in self.constitution_types.items()
        ]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Health Advisor V2.0")
    parser.add_argument("action", choices=["symptoms", "constitution", "metrics", "fortune", "list-symptoms", "list-constitutions"], help="操作类型")
    parser.add_argument("--symptoms", nargs="+", help="症状列表")
    parser.add_argument("--severity", default="moderate", help="严重程度")
    parser.add_argument("--answers", help="体质问卷答案(JSON)")
    parser.add_argument("--metrics", help="健康指标(JSON)")
    parser.add_argument("--birth-date", help="出生日期")
    args = parser.parse_args()
    
    root = get_project_root()
    advisor = HealthAdvisor(root)
    
    if args.action == "symptoms":
        if not args.symptoms:
            print("请提供症状: --symptoms headache fatigue")
            return 1
        
        result = advisor.analyze_symptoms(args.symptoms, severity=args.severity)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "constitution":
        if not args.answers:
            # 默认答案
            answers = {"q1": 3, "q2": 2, "q3": 3}
        else:
            answers = json.loads(args.answers)
        
        result = advisor.assess_constitution(answers)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "metrics":
        if not args.metrics:
            metrics = {"heart_rate": 75, "bmi": 22.5}
        else:
            metrics = json.loads(args.metrics)
        
        result = advisor.analyze_health_metrics(metrics)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "fortune":
        if not args.birth_date:
            birth_date = "1990-01-01"
        else:
            birth_date = args.birth_date
        
        result = advisor.fortune_telling(birth_date)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "list-symptoms":
        symptoms = advisor.list_symptoms()
        print(json.dumps(symptoms, ensure_ascii=False, indent=2))
        
    elif args.action == "list-constitutions":
        constitutions = advisor.list_constitutions()
        print(json.dumps(constitutions, ensure_ascii=False, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
