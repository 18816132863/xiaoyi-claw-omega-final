"""Risk manager - risk assessment and mitigation."""

from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskCategory(Enum):
    DATA_LOSS = "data_loss"
    SECURITY = "security"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"


@dataclass
class RiskAssessment:
    """Result of risk assessment."""
    risk_id: str
    level: RiskLevel
    category: RiskCategory
    description: str
    factors: List[Dict]
    mitigations: List[str]
    requires_approval: bool
    assessed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class RiskFactor:
    """A factor contributing to risk."""
    name: str
    weight: float
    value: any
    contribution: float


class RiskManager:
    """
    Manages risk assessment and mitigation.
    
    Evaluates risks for:
    - Data operations
    - Security-sensitive actions
    - Performance-impacting changes
    - Compliance requirements
    - Operational changes
    """
    
    def __init__(self):
        self._assessors: Dict[str, callable] = {}
        self._mitigations: Dict[str, List[str]] = {}
        self._assessment_history: List[RiskAssessment] = []
        self._setup_default_assessors()
    
    def _setup_default_assessors(self):
        """Setup default risk assessors."""
        self.register_assessor("file_delete", self._assess_file_delete)
        self.register_assessor("file_write", self._assess_file_write)
        self.register_assessor("command_exec", self._assess_command_exec)
        self.register_assessor("skill_execute", self._assess_skill_execute)
        self.register_assessor("workflow_run", self._assess_workflow_run)
    
    def register_assessor(self, action_type: str, assessor: callable):
        """Register a risk assessor for an action type."""
        self._assessors[action_type] = assessor
    
    def assess(self, action_type: str, context: Dict) -> RiskAssessment:
        """
        Assess risk for an action.
        
        Args:
            action_type: Type of action being assessed
            context: Context for assessment
        
        Returns:
            RiskAssessment with risk level and mitigations
        """
        assessor = self._assessors.get(action_type, self._default_assessor)
        assessment = assessor(action_type, context)
        
        self._assessment_history.append(assessment)
        return assessment
    
    def _default_assessor(self, action_type: str, context: Dict) -> RiskAssessment:
        """Default risk assessor."""
        return RiskAssessment(
            risk_id=f"risk_{action_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            level=RiskLevel.LOW,
            category=RiskCategory.OPERATIONAL,
            description=f"Default assessment for {action_type}",
            factors=[],
            mitigations=[],
            requires_approval=False
        )
    
    def _assess_file_delete(self, action_type: str, context: Dict) -> RiskAssessment:
        """Assess file deletion risk."""
        factors = []
        total_risk = 0.0
        
        # Check if protected file
        path = context.get("path", "")
        protected_patterns = [".openclaw/", "core/", "governance/"]
        is_protected = any(p in path for p in protected_patterns)
        
        if is_protected:
            factors.append({
                "name": "protected_file",
                "weight": 0.5,
                "value": True,
                "contribution": 0.5
            })
            total_risk += 0.5
        
        # Check if critical file
        critical_files = ["AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md"]
        is_critical = any(f in path for f in critical_files)
        
        if is_critical:
            factors.append({
                "name": "critical_file",
                "weight": 0.4,
                "value": True,
                "contribution": 0.4
            })
            total_risk += 0.4
        
        # Determine level
        if total_risk >= 0.7:
            level = RiskLevel.CRITICAL
        elif total_risk >= 0.5:
            level = RiskLevel.HIGH
        elif total_risk >= 0.3:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return RiskAssessment(
            risk_id=f"risk_delete_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            level=level,
            category=RiskCategory.DATA_LOSS,
            description=f"File deletion: {path}",
            factors=factors,
            mitigations=[
                "Use trash instead of rm",
                "Create backup before deletion",
                "Require user confirmation"
            ],
            requires_approval=level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
    
    def _assess_file_write(self, action_type: str, context: Dict) -> RiskAssessment:
        """Assess file write risk."""
        factors = []
        total_risk = 0.0
        
        path = context.get("path", "")
        
        # Check if overwriting
        is_overwrite = context.get("exists", False)
        if is_overwrite:
            factors.append({
                "name": "file_overwrite",
                "weight": 0.2,
                "value": True,
                "contribution": 0.2
            })
            total_risk += 0.2
        
        # Check if protected
        protected_patterns = ["core/", "governance/"]
        is_protected = any(p in path for p in protected_patterns)
        if is_protected:
            factors.append({
                "name": "protected_location",
                "weight": 0.3,
                "value": True,
                "contribution": 0.3
            })
            total_risk += 0.3
        
        # Determine level
        if total_risk >= 0.5:
            level = RiskLevel.HIGH
        elif total_risk >= 0.3:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return RiskAssessment(
            risk_id=f"risk_write_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            level=level,
            category=RiskCategory.OPERATIONAL,
            description=f"File write: {path}",
            factors=factors,
            mitigations=[
                "Create backup before write",
                "Validate content before write"
            ],
            requires_approval=level == RiskLevel.HIGH
        )
    
    def _assess_command_exec(self, action_type: str, context: Dict) -> RiskAssessment:
        """Assess command execution risk."""
        factors = []
        total_risk = 0.0
        
        command = context.get("command", "")
        
        # Check for dangerous patterns
        dangerous_patterns = ["rm -rf", "sudo", "chmod 777", "> /dev/"]
        for pattern in dangerous_patterns:
            if pattern in command:
                factors.append({
                    "name": "dangerous_pattern",
                    "weight": 0.4,
                    "value": pattern,
                    "contribution": 0.4
                })
                total_risk += 0.4
                break
        
        # Check for network operations
        network_patterns = ["curl", "wget", "ssh", "scp"]
        for pattern in network_patterns:
            if pattern in command:
                factors.append({
                    "name": "network_operation",
                    "weight": 0.2,
                    "value": pattern,
                    "contribution": 0.2
                })
                total_risk += 0.2
                break
        
        # Determine level
        if total_risk >= 0.6:
            level = RiskLevel.CRITICAL
        elif total_risk >= 0.4:
            level = RiskLevel.HIGH
        elif total_risk >= 0.2:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return RiskAssessment(
            risk_id=f"risk_exec_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            level=level,
            category=RiskCategory.SECURITY,
            description=f"Command execution: {command[:50]}...",
            factors=factors,
            mitigations=[
                "Review command before execution",
                "Run in sandbox if possible",
                "Require approval for dangerous commands"
            ],
            requires_approval=level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        )
    
    def _assess_skill_execute(self, action_type: str, context: Dict) -> RiskAssessment:
        """Assess skill execution risk."""
        skill_id = context.get("skill_id", "")
        skill_status = context.get("skill_status", "stable")
        
        factors = []
        total_risk = 0.0
        
        # Check skill status
        if skill_status == "deprecated":
            factors.append({
                "name": "deprecated_skill",
                "weight": 0.3,
                "value": skill_status,
                "contribution": 0.3
            })
            total_risk += 0.3
        elif skill_status == "experimental":
            factors.append({
                "name": "experimental_skill",
                "weight": 0.2,
                "value": skill_status,
                "contribution": 0.2
            })
            total_risk += 0.2
        
        # Determine level
        if total_risk >= 0.3:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return RiskAssessment(
            risk_id=f"risk_skill_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            level=level,
            category=RiskCategory.OPERATIONAL,
            description=f"Skill execution: {skill_id}",
            factors=factors,
            mitigations=[
                "Check skill documentation",
                "Use stable version if available"
            ],
            requires_approval=False
        )
    
    def _assess_workflow_run(self, action_type: str, context: Dict) -> RiskAssessment:
        """Assess workflow execution risk."""
        workflow_id = context.get("workflow_id", "")
        step_count = context.get("step_count", 0)
        has_critical = context.get("has_critical_steps", False)
        
        factors = []
        total_risk = 0.0
        
        # Check complexity
        if step_count > 10:
            factors.append({
                "name": "complex_workflow",
                "weight": 0.2,
                "value": step_count,
                "contribution": 0.2
            })
            total_risk += 0.2
        
        # Check for critical steps
        if has_critical:
            factors.append({
                "name": "critical_steps",
                "weight": 0.3,
                "value": True,
                "contribution": 0.3
            })
            total_risk += 0.3
        
        # Determine level
        if total_risk >= 0.4:
            level = RiskLevel.HIGH
        elif total_risk >= 0.2:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        return RiskAssessment(
            risk_id=f"risk_workflow_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            level=level,
            category=RiskCategory.OPERATIONAL,
            description=f"Workflow execution: {workflow_id}",
            factors=factors,
            mitigations=[
                "Review workflow steps",
                "Enable checkpointing",
                "Prepare rollback plan"
            ],
            requires_approval=level == RiskLevel.HIGH
        )
    
    def get_assessment_history(self, limit: int = 100) -> List[RiskAssessment]:
        """Get recent assessments."""
        return self._assessment_history[-limit:]
    
    def get_high_risk_actions(self) -> List[RiskAssessment]:
        """Get high/critical risk assessments."""
        return [
            a for a in self._assessment_history
            if a.level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]
