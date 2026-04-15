#!/usr/bin/env python3
"""
规则生命周期管理 - V1.0.0

管理规则的创建、更新、废弃流程。
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
from pathlib import Path


class LifecycleStage(Enum):
    """生命周期阶段"""
    DRAFT = "draft"           # 草稿
    REVIEW = "review"         # 审核中
    ACTIVE = "active"         # 激活
    DEPRECATED = "deprecated" # 废弃
    ARCHIVED = "archived"     # 归档


@dataclass
class RuleVersion:
    """规则版本"""
    version: str
    content: Dict[str, Any]
    created_at: datetime
    created_by: str
    change_note: str


@dataclass
class LifecycleEvent:
    """生命周期事件"""
    rule_id: str
    from_stage: LifecycleStage
    to_stage: LifecycleStage
    timestamp: datetime
    actor: str
    reason: str


class RuleLifecycle:
    """规则生命周期管理器"""
    
    def __init__(self, storage_path: str = "archive/rules"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.versions: Dict[str, List[RuleVersion]] = {}
        self.events: List[LifecycleEvent] = []
        self.stage_rules: Dict[LifecycleStage, List[str]] = {
            stage: [] for stage in LifecycleStage
        }
    
    def create_rule(self,
                    rule_id: str,
                    content: Dict[str, Any],
                    created_by: str = "system") -> RuleVersion:
        """创建规则（草稿）"""
        version = RuleVersion(
            version="1.0.0",
            content=content,
            created_at=datetime.now(),
            created_by=created_by,
            change_note="初始创建"
        )
        
        self.versions[rule_id] = [version]
        self.stage_rules[LifecycleStage.DRAFT].append(rule_id)
        
        self._record_event(
            rule_id,
            None,
            LifecycleStage.DRAFT,
            created_by,
            "规则创建"
        )
        
        return version
    
    def update_rule(self,
                    rule_id: str,
                    content: Dict[str, Any],
                    updated_by: str = "system",
                    change_note: str = "") -> RuleVersion:
        """更新规则"""
        if rule_id not in self.versions:
            raise ValueError(f"规则不存在: {rule_id}")
        
        # 计算新版本号
        last_version = self.versions[rule_id][-1]
        major, minor, patch = map(int, last_version.version.split("."))
        
        # 根据变更类型决定版本号
        if change_note and "重大" in change_note:
            major += 1
            minor = 0
            patch = 0
        elif change_note and "功能" in change_note:
            minor += 1
            patch = 0
        else:
            patch += 1
        
        new_version = RuleVersion(
            version=f"{major}.{minor}.{patch}",
            content=content,
            created_at=datetime.now(),
            created_by=updated_by,
            change_note=change_note
        )
        
        self.versions[rule_id].append(new_version)
        
        return new_version
    
    def transition(self,
                   rule_id: str,
                   to_stage: LifecycleStage,
                   actor: str = "system",
                   reason: str = "") -> bool:
        """转换生命周期阶段"""
        # 找到当前阶段
        current_stage = None
        for stage, rules in self.stage_rules.items():
            if rule_id in rules:
                current_stage = stage
                break
        
        if current_stage is None:
            return False
        
        # 验证转换
        if not self._validate_transition(current_stage, to_stage):
            return False
        
        # 执行转换
        self.stage_rules[current_stage].remove(rule_id)
        self.stage_rules[to_stage].append(rule_id)
        
        self._record_event(rule_id, current_stage, to_stage, actor, reason)
        
        return True
    
    def _validate_transition(self, from_stage: LifecycleStage, to_stage: LifecycleStage) -> bool:
        """验证阶段转换"""
        valid_transitions = {
            LifecycleStage.DRAFT: [LifecycleStage.REVIEW, LifecycleStage.ARCHIVED],
            LifecycleStage.REVIEW: [LifecycleStage.ACTIVE, LifecycleStage.DRAFT],
            LifecycleStage.ACTIVE: [LifecycleStage.DEPRECATED],
            LifecycleStage.DEPRECATED: [LifecycleStage.ARCHIVED, LifecycleStage.ACTIVE],
            LifecycleStage.ARCHIVED: []
        }
        
        return to_stage in valid_transitions.get(from_stage, [])
    
    def _record_event(self,
                      rule_id: str,
                      from_stage: Optional[LifecycleStage],
                      to_stage: LifecycleStage,
                      actor: str,
                      reason: str):
        """记录事件"""
        event = LifecycleEvent(
            rule_id=rule_id,
            from_stage=from_stage or LifecycleStage.DRAFT,
            to_stage=to_stage,
            timestamp=datetime.now(),
            actor=actor,
            reason=reason
        )
        
        self.events.append(event)
    
    def get_rule_history(self, rule_id: str) -> List[RuleVersion]:
        """获取规则历史"""
        return self.versions.get(rule_id, [])
    
    def get_rules_by_stage(self, stage: LifecycleStage) -> List[str]:
        """获取指定阶段的规则"""
        return self.stage_rules.get(stage, [])
    
    def deprecate_rule(self,
                       rule_id: str,
                       reason: str,
                       actor: str = "system",
                       deprecation_period_days: int = 30) -> bool:
        """废弃规则"""
        # 设置废弃日期
        deprecation_date = datetime.now() + timedelta(days=deprecation_period_days)
        
        # 转换到废弃阶段
        success = self.transition(
            rule_id,
            LifecycleStage.DEPRECATED,
            actor,
            f"{reason} (将于 {deprecation_date.strftime('%Y-%m-%d')} 归档)"
        )
        
        return success
    
    def get_deprecated_rules(self) -> List[Dict]:
        """获取待归档的废弃规则"""
        deprecated = self.stage_rules.get(LifecycleStage.DEPRECATED, [])
        
        result = []
        for rule_id in deprecated:
            history = self.versions.get(rule_id, [])
            if history:
                last_event = next(
                    (e for e in reversed(self.events) if e.rule_id == rule_id),
                    None
                )
                
                result.append({
                    "rule_id": rule_id,
                    "deprecated_at": last_event.timestamp if last_event else None,
                    "reason": last_event.reason if last_event else None
                })
        
        return result
    
    def export_lifecycle(self) -> str:
        """导出生命周期数据"""
        data = {
            "versions": {
                rule_id: [
                    {
                        "version": v.version,
                        "content": v.content,
                        "created_at": v.created_at.isoformat(),
                        "created_by": v.created_by,
                        "change_note": v.change_note
                    }
                    for v in versions
                ]
                for rule_id, versions in self.versions.items()
            },
            "events": [
                {
                    "rule_id": e.rule_id,
                    "from_stage": e.from_stage.value,
                    "to_stage": e.to_stage.value,
                    "timestamp": e.timestamp.isoformat(),
                    "actor": e.actor,
                    "reason": e.reason
                }
                for e in self.events
            ]
        }
        
        return json.dumps(data, ensure_ascii=False, indent=2)


# 全局规则生命周期管理器
_rule_lifecycle: Optional[RuleLifecycle] = None


def get_rule_lifecycle() -> RuleLifecycle:
    """获取全局规则生命周期管理器"""
    global _rule_lifecycle
    if _rule_lifecycle is None:
        _rule_lifecycle = RuleLifecycle()
    return _rule_lifecycle
