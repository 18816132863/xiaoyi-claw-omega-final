"""
Promotion Manager - 晋升管理器
Phase3 Group6 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os


class PromotionStatus(Enum):
    """晋升状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class PromotionStep:
    """晋升步骤"""
    step_name: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_name": self.step_name,
            "status": self.status,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error
        }


@dataclass
class PromotionRecord:
    """晋升记录"""
    promotion_id: str
    baseline_id: str
    version: str
    from_channel: str
    to_channel: str
    status: PromotionStatus
    steps: List[PromotionStep] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    canary_percentage: int = 0
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "promotion_id": self.promotion_id,
            "baseline_id": self.baseline_id,
            "version": self.version,
            "from_channel": self.from_channel,
            "to_channel": self.to_channel,
            "status": self.status.value,
            "steps": [s.to_dict() for s in self.steps],
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "canary_percentage": self.canary_percentage,
            "metrics_before": self.metrics_before,
            "metrics_after": self.metrics_after
        }


class PromotionManager:
    """
    晋升管理器
    
    职责：
    - 管理基线晋升流程
    - 支持 canary 发布
    - 追踪晋升状态
    - 支持回滚
    """
    
    def __init__(self, promotions_path: str = "reports/release/promotion_history.json"):
        self.promotions_path = promotions_path
        self._promotions: Dict[str, PromotionRecord] = {}
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.promotions_path), exist_ok=True)
    
    def _load(self):
        """加载晋升记录"""
        if not os.path.exists(self.promotions_path):
            return
        
        try:
            with open(self.promotions_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for promo_id, promo_data in data.get("promotions", {}).items():
                steps = [
                    PromotionStep(**s) for s in promo_data.get("steps", [])
                ]
                
                self._promotions[promo_id] = PromotionRecord(
                    promotion_id=promo_data.get("promotion_id", promo_id),
                    baseline_id=promo_data.get("baseline_id", ""),
                    version=promo_data.get("version", ""),
                    from_channel=promo_data.get("from_channel", ""),
                    to_channel=promo_data.get("to_channel", ""),
                    status=PromotionStatus(promo_data.get("status", "pending")),
                    steps=steps,
                    started_at=promo_data.get("started_at", ""),
                    completed_at=promo_data.get("completed_at"),
                    canary_percentage=promo_data.get("canary_percentage", 0),
                    metrics_before=promo_data.get("metrics_before", {}),
                    metrics_after=promo_data.get("metrics_after", {})
                )
        except Exception:
            pass
    
    def _save(self):
        """保存晋升记录"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "total_promotions": len(self._promotions),
            "promotions": {
                promo_id: promo.to_dict()
                for promo_id, promo in self._promotions.items()
            }
        }
        
        with open(self.promotions_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def start_promotion(
        self,
        baseline_id: str,
        version: str,
        from_channel: str,
        to_channel: str,
        canary: bool = False
    ) -> PromotionRecord:
        """开始晋升"""
        import uuid
        
        promo_id = f"promo_{uuid.uuid4().hex[:8]}"
        
        steps = [
            PromotionStep(step_name="verify_baseline", status="pending"),
            PromotionStep(step_name="run_tests", status="pending"),
            PromotionStep(step_name="update_channel", status="pending"),
            PromotionStep(step_name="verify_health", status="pending"),
        ]
        
        if canary:
            steps.insert(2, PromotionStep(step_name="canary_deploy", status="pending"))
            steps.insert(3, PromotionStep(step_name="monitor_canary", status="pending"))
        
        record = PromotionRecord(
            promotion_id=promo_id,
            baseline_id=baseline_id,
            version=version,
            from_channel=from_channel,
            to_channel=to_channel,
            status=PromotionStatus.IN_PROGRESS,
            steps=steps,
            canary_percentage=10 if canary else 100
        )
        
        self._promotions[promo_id] = record
        self._save()
        
        return record
    
    def complete_step(
        self,
        promotion_id: str,
        step_name: str,
        success: bool,
        error: str = None
    ):
        """完成步骤"""
        record = self._promotions.get(promotion_id)
        if not record:
            return
        
        for step in record.steps:
            if step.step_name == step_name:
                step.status = "completed" if success else "failed"
                step.completed_at = datetime.now().isoformat()
                step.error = error
                break
        
        self._save()
    
    def complete_promotion(self, promotion_id: str, success: bool):
        """完成晋升"""
        record = self._promotions.get(promotion_id)
        if not record:
            return
        
        record.status = PromotionStatus.COMPLETED if success else PromotionStatus.FAILED
        record.completed_at = datetime.now().isoformat()
        self._save()
    
    def rollback(self, promotion_id: str):
        """回滚晋升"""
        record = self._promotions.get(promotion_id)
        if not record:
            return
        
        record.status = PromotionStatus.ROLLED_BACK
        record.completed_at = datetime.now().isoformat()
        self._save()
    
    def get_promotion(self, promotion_id: str) -> Optional[PromotionRecord]:
        """获取晋升记录"""
        return self._promotions.get(promotion_id)
    
    def get_recent_promotions(self, limit: int = 10) -> List[PromotionRecord]:
        """获取最近的晋升记录"""
        promos = list(self._promotions.values())
        promos.sort(key=lambda p: p.started_at, reverse=True)
        return promos[:limit]


# 全局单例
_promotion_manager = None


def get_promotion_manager() -> PromotionManager:
    """获取晋升管理器单例"""
    global _promotion_manager
    if _promotion_manager is None:
        _promotion_manager = PromotionManager()
    return _promotion_manager
