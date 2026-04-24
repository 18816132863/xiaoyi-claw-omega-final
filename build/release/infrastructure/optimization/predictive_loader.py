"""预测性加载器 - V1.0.0"""

from typing import Dict, List, Optional
from collections import defaultdict
import json
from pathlib import Path
from infrastructure.path_resolver import get_project_root

class PredictiveLoader:
    """预测性加载器 - 根据历史预测下一步"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path or get_project_root())
        self.history_file = self.workspace / ".cache" / "prediction_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 转移矩阵: 当前技能 -> 下一个技能 -> 次数
        self.transitions: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.current_skill: Optional[str] = None
        
        self._load_history()
    
    def _load_history(self):
        """加载历史"""
        if self.history_file.exists():
            with open(self.history_file) as f:
                data = json.load(f)
            for curr, nexts in data.get("transitions", {}).items():
                for nxt, count in nexts.items():
                    self.transitions[curr][nxt] = count
    
    def _save_history(self):
        """保存历史"""
        data = {
            "transitions": {
                curr: dict(nexts) 
                for curr, nexts in self.transitions.items()
            }
        }
        with open(self.history_file, "w") as f:
            json.dump(data, f)
    
    def record_transition(self, from_skill: str, to_skill: str):
        """记录转移"""
        self.transitions[from_skill][to_skill] += 1
        self._save_history()
    
    def predict_next(self, current_skill: str, top_k: int = 3) -> List[str]:
        """预测下一个技能"""
        if current_skill not in self.transitions:
            return []
        
        nexts = self.transitions[current_skill]
        sorted_nexts = sorted(nexts.items(), key=lambda x: x[1], reverse=True)
        return [s[0] for s in sorted_nexts[:top_k]]
    
    def get_prediction_confidence(self, current_skill: str, predicted_skill: str) -> float:
        """获取预测置信度"""
        if current_skill not in self.transitions:
            return 0.0
        
        total = sum(self.transitions[current_skill].values())
        if total == 0:
            return 0.0
        
        return self.transitions[current_skill].get(predicted_skill, 0) / total
    
    def get_stats(self) -> Dict:
        """获取统计"""
        total_transitions = sum(
            sum(nexts.values()) 
            for nexts in self.transitions.values()
        )
        unique_skills = len(self.transitions)
        
        return {
            "total_transitions": total_transitions,
            "unique_skills": unique_skills,
            "avg_transitions_per_skill": total_transitions / max(1, unique_skills)
        }
