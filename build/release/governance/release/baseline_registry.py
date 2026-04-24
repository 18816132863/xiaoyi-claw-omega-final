"""
Baseline Registry - 基线注册表
Phase3 Group6 核心模块
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import os


class BaselineStage(Enum):
    """基线阶段"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    STABLE = "stable"


@dataclass
class VerificationBundle:
    """验证包"""
    phase1_baseline_passed: bool = False
    benchmarks_passed: bool = False
    integration_tests_passed: bool = False
    metrics_healthy: bool = False
    regression_guard_passed: bool = False
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "phase1_baseline_passed": self.phase1_baseline_passed,
            "benchmarks_passed": self.benchmarks_passed,
            "integration_tests_passed": self.integration_tests_passed,
            "metrics_healthy": self.metrics_healthy,
            "regression_guard_passed": self.regression_guard_passed,
            "details": self.details
        }
    
    @property
    def all_passed(self) -> bool:
        return (
            self.phase1_baseline_passed and
            self.benchmarks_passed and
            self.integration_tests_passed and
            self.metrics_healthy and
            self.regression_guard_passed
        )


@dataclass
class Baseline:
    """基线"""
    baseline_id: str
    version: str
    stage: BaselineStage
    channel: str
    created_at: str
    compatible_profiles: List[str] = field(default_factory=list)
    verification_bundle: Optional[VerificationBundle] = None
    promoted_at: Optional[str] = None
    promotion_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_id": self.baseline_id,
            "version": self.version,
            "stage": self.stage.value,
            "channel": self.channel,
            "created_at": self.created_at,
            "compatible_profiles": self.compatible_profiles,
            "verification_bundle": self.verification_bundle.to_dict() if self.verification_bundle else None,
            "promoted_at": self.promoted_at,
            "promotion_history": self.promotion_history,
            "metadata": self.metadata
        }


class BaselineRegistry:
    """
    基线注册表
    
    职责：
    - 注册基线
    - 追踪基线状态
    - 管理基线晋升历史
    """
    
    def __init__(self, registry_path: str = "reports/release/baseline_registry.json"):
        self.registry_path = registry_path
        self._baselines: Dict[str, Baseline] = {}
        self._version_index: Dict[str, str] = {}  # version -> baseline_id
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        """确保目录存在"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
    
    def _load(self):
        """加载基线"""
        if not os.path.exists(self.registry_path):
            return
        
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for baseline_id, baseline_data in data.get("baselines", {}).items():
                verification_bundle = None
                if baseline_data.get("verification_bundle"):
                    vb_data = baseline_data["verification_bundle"]
                    verification_bundle = VerificationBundle(
                        phase1_baseline_passed=vb_data.get("phase1_baseline_passed", False),
                        benchmarks_passed=vb_data.get("benchmarks_passed", False),
                        integration_tests_passed=vb_data.get("integration_tests_passed", False),
                        metrics_healthy=vb_data.get("metrics_healthy", False),
                        regression_guard_passed=vb_data.get("regression_guard_passed", False),
                        details=vb_data.get("details", {})
                    )
                
                baseline = Baseline(
                    baseline_id=baseline_data.get("baseline_id", baseline_id),
                    version=baseline_data.get("version", ""),
                    stage=BaselineStage(baseline_data.get("stage", "development")),
                    channel=baseline_data.get("channel", "dev"),
                    created_at=baseline_data.get("created_at", ""),
                    compatible_profiles=baseline_data.get("compatible_profiles", []),
                    verification_bundle=verification_bundle,
                    promoted_at=baseline_data.get("promoted_at"),
                    promotion_history=baseline_data.get("promotion_history", []),
                    metadata=baseline_data.get("metadata", {})
                )
                
                self._baselines[baseline_id] = baseline
                self._version_index[baseline.version] = baseline_id
        except Exception:
            pass
    
    def _save(self):
        """保存基线"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "total_baselines": len(self._baselines),
            "baselines": {
                baseline_id: baseline.to_dict()
                for baseline_id, baseline in self._baselines.items()
            }
        }
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register(
        self,
        baseline_id: str,
        version: str,
        stage: BaselineStage = BaselineStage.DEVELOPMENT,
        channel: str = "dev",
        compatible_profiles: List[str] = None
    ) -> Baseline:
        """注册基线"""
        baseline = Baseline(
            baseline_id=baseline_id,
            version=version,
            stage=stage,
            channel=channel,
            created_at=datetime.now().isoformat(),
            compatible_profiles=compatible_profiles or ["default"]
        )
        
        self._baselines[baseline_id] = baseline
        self._version_index[version] = baseline_id
        self._save()
        
        return baseline
    
    def get(self, baseline_id: str) -> Optional[Baseline]:
        """获取基线"""
        return self._baselines.get(baseline_id)
    
    def get_by_version(self, version: str) -> Optional[Baseline]:
        """按版本获取基线"""
        baseline_id = self._version_index.get(version)
        return self._baselines.get(baseline_id) if baseline_id else None
    
    def update_verification(
        self,
        baseline_id: str,
        verification_bundle: VerificationBundle
    ):
        """更新验证包"""
        baseline = self._baselines.get(baseline_id)
        if baseline:
            baseline.verification_bundle = verification_bundle
            self._save()
    
    def record_promotion(
        self,
        baseline_id: str,
        from_channel: str,
        to_channel: str
    ):
        """记录晋升"""
        baseline = self._baselines.get(baseline_id)
        if baseline:
            baseline.promotion_history.append({
                "from_channel": from_channel,
                "to_channel": to_channel,
                "promoted_at": datetime.now().isoformat()
            })
            baseline.promoted_at = datetime.now().isoformat()
            baseline.channel = to_channel
            self._save()
    
    def get_current_stable(self) -> Optional[Baseline]:
        """获取当前 stable 基线"""
        for baseline in self._baselines.values():
            if baseline.channel == "stable":
                return baseline
        return None
    
    def list_by_channel(self, channel: str) -> List[Baseline]:
        """按通道列出基线"""
        return [b for b in self._baselines.values() if b.channel == channel]
    
    def list_all(self) -> List[Baseline]:
        """列出所有基线"""
        return list(self._baselines.values())


# 全局单例
_baseline_registry = None


def get_baseline_registry() -> BaselineRegistry:
    """获取基线注册表单例"""
    global _baseline_registry
    if _baseline_registry is None:
        _baseline_registry = BaselineRegistry()
    return _baseline_registry
