#!/usr/bin/env python3
"""
规则引擎 - V1.0.0

执行和管理业务规则。
"""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import json


class RulePriority(Enum):
    """规则优先级"""
    CRITICAL = 0   # 最高优先级
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKGROUND = 4


class RuleAction(Enum):
    """规则动作"""
    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    TRANSFORM = "transform"
    LOG = "log"


class RuleStatus(Enum):
    """规则状态"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    TESTING = "testing"


@dataclass
class Rule:
    """规则定义"""
    id: str
    name: str
    description: str
    condition: str  # 条件表达式
    action: RuleAction
    priority: RulePriority = RulePriority.MEDIUM
    status: RuleStatus = RuleStatus.ACTIVE
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    hit_count: int = 0


@dataclass
class RuleResult:
    """规则执行结果"""
    rule_id: str
    matched: bool
    action: RuleAction
    message: str
    transformed_data: Optional[Any] = None
    timestamp: datetime = field(default_factory=datetime.now)


class RuleEngine:
    """规则引擎"""
    
    def __init__(self):
        self.rules: Dict[str, Rule] = {}
        self.execution_history: List[RuleResult] = []
        self._register_default_rules()
    
    def _register_default_rules(self):
        """注册默认规则"""
        # 文件保护规则
        self.register_rule(Rule(
            id="protect_core_files",
            name="保护核心文件",
            description="禁止删除或修改核心配置文件",
            condition="operation in ['delete', 'modify'] and target in PROTECTED_FILES",
            action=RuleAction.DENY,
            priority=RulePriority.CRITICAL,
            tags=["security", "file"]
        ))
        
        # 敏感数据规则
        self.register_rule(Rule(
            id="sensitive_data_check",
            name="敏感数据检查",
            description="检查操作是否涉及敏感数据",
            condition="contains_sensitive_data(data)",
            action=RuleAction.WARN,
            priority=RulePriority.HIGH,
            tags=["security", "data"]
        ))
        
        # 速率限制规则
        self.register_rule(Rule(
            id="rate_limit",
            name="速率限制",
            description="限制操作频率",
            condition="operation_count > RATE_LIMIT",
            action=RuleAction.DENY,
            priority=RulePriority.HIGH,
            tags=["performance"]
        ))
    
    def register_rule(self, rule: Rule):
        """注册规则"""
        self.rules[rule.id] = rule
    
    def unregister_rule(self, rule_id: str) -> bool:
        """注销规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False
    
    def evaluate(self,
                 operation: str,
                 target: str = None,
                 data: Any = None,
                 context: Dict = None) -> List[RuleResult]:
        """
        评估规则
        
        Args:
            operation: 操作类型
            target: 目标对象
            data: 操作数据
            context: 上下文
        
        Returns:
            规则执行结果列表
        """
        results = []
        context = context or {}
        
        # 按优先级排序规则
        active_rules = [
            r for r in self.rules.values()
            if r.status == RuleStatus.ACTIVE
        ]
        active_rules.sort(key=lambda r: r.priority.value)
        
        # 评估每个规则
        for rule in active_rules:
            result = self._evaluate_rule(rule, operation, target, data, context)
            results.append(result)
            
            # 更新命中计数
            if result.matched:
                rule.hit_count += 1
            
            # DENY 动作立即返回
            if result.matched and result.action == RuleAction.DENY:
                break
        
        self.execution_history.extend(results)
        return results
    
    def _evaluate_rule(self,
                       rule: Rule,
                       operation: str,
                       target: str,
                       data: Any,
                       context: Dict) -> RuleResult:
        """评估单个规则"""
        try:
            # 构建评估上下文
            eval_context = {
                "operation": operation,
                "target": target,
                "data": data,
                "PROTECTED_FILES": [
                    "AGENTS.md", "MEMORY.md", "TOOLS.md", "SOUL.md",
                    "core/ARCHITECTURE.md", "infrastructure/inventory/skill_registry.json"
                ],
                "RATE_LIMIT": 100,
                "operation_count": context.get("operation_count", 0),
                "contains_sensitive_data": self._contains_sensitive_data,
            }
            
            # 评估条件
            matched = self._safe_eval(rule.condition, eval_context)
            
            if matched:
                return RuleResult(
                    rule_id=rule.id,
                    matched=True,
                    action=rule.action,
                    message=f"规则 {rule.name} 匹配"
                )
            else:
                return RuleResult(
                    rule_id=rule.id,
                    matched=False,
                    action=RuleAction.ALLOW,
                    message=f"规则 {rule.name} 不匹配"
                )
                
        except Exception as e:
            return RuleResult(
                rule_id=rule.id,
                matched=False,
                action=RuleAction.ALLOW,
                message=f"规则评估错误: {str(e)}"
            )
    
    def _safe_eval(self, condition: str, context: Dict) -> bool:
        """安全评估条件"""
        # 简化实现：支持基本条件
        try:
            # 替换上下文变量
            for key, value in context.items():
                if callable(value):
                    continue
                condition = condition.replace(key, repr(value))
            
            # 处理特殊函数
            if "contains_sensitive_data" in condition:
                # 简化处理
                data = context.get("data", "")
                if self._contains_sensitive_data(data):
                    condition = condition.replace("contains_sensitive_data(data)", "True")
                else:
                    condition = condition.replace("contains_sensitive_data(data)", "False")
            
            # 评估
            return eval(condition, {"__builtins__": {}}, context)
        except:
            return False
    
    def _contains_sensitive_data(self, data: Any) -> bool:
        """检查是否包含敏感数据"""
        sensitive_patterns = ["password", "secret", "token", "key"]
        data_str = str(data).lower()
        return any(p in data_str for p in sensitive_patterns)
    
    def get_rules_by_tag(self, tag: str) -> List[Rule]:
        """按标签获取规则"""
        return [r for r in self.rules.values() if tag in r.tags]
    
    def get_rules_by_priority(self, priority: RulePriority) -> List[Rule]:
        """按优先级获取规则"""
        return [r for r in self.rules.values() if r.priority == priority]
    
    def get_statistics(self) -> Dict:
        """获取规则统计"""
        return {
            "total_rules": len(self.rules),
            "active_rules": sum(1 for r in self.rules.values() if r.status == RuleStatus.ACTIVE),
            "total_executions": len(self.execution_history),
            "top_hit_rules": sorted(
                [(r.id, r.hit_count) for r in self.rules.values()],
                key=lambda x: -x[1]
            )[:5]
        }
    
    def export_rules(self) -> str:
        """导出规则"""
        data = {
            "rules": [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "condition": r.condition,
                    "action": r.action.value,
                    "priority": r.priority.value,
                    "status": r.status.value,
                    "tags": r.tags,
                    "metadata": r.metadata
                }
                for r in self.rules.values()
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    def import_rules(self, rules_json: str) -> int:
        """导入规则"""
        data = json.loads(rules_json)
        count = 0
        
        for r in data.get("rules", []):
            rule = Rule(
                id=r["id"],
                name=r["name"],
                description=r["description"],
                condition=r["condition"],
                action=RuleAction(r["action"]),
                priority=RulePriority(r["priority"]),
                status=RuleStatus(r.get("status", "active")),
                tags=r.get("tags", []),
                metadata=r.get("metadata", {})
            )
            self.rules[rule.id] = rule
            count += 1
        
        return count


# 全局规则引擎
_rule_engine: Optional[RuleEngine] = None


def get_rule_engine() -> RuleEngine:
    """获取全局规则引擎"""
    global _rule_engine
    if _rule_engine is None:
        _rule_engine = RuleEngine()
    return _rule_engine
