"""Source selector for retrieval."""

from typing import List, Dict, Optional
from enum import Enum


class SourceType(Enum):
    SESSION = "session"
    MEMORY = "memory"
    DOCUMENT = "document"
    SKILL = "skill"
    RULE = "rule"
    REPORT = "report"


class SourceSelector:
    """Selects appropriate sources for retrieval based on intent."""
    
    def __init__(self):
        self.intent_source_map = {
            "task_execution": [SourceType.SESSION, SourceType.MEMORY, SourceType.SKILL],
            "information_retrieval": [SourceType.DOCUMENT, SourceType.MEMORY, SourceType.RULE],
            "troubleshooting": [SourceType.REPORT, SourceType.RULE, SourceType.MEMORY],
            "architecture_query": [SourceType.DOCUMENT, SourceType.RULE, SourceType.MEMORY],
            "skill_discovery": [SourceType.SKILL, SourceType.DOCUMENT],
            "compliance_check": [SourceType.RULE, SourceType.REPORT],
            "general": [SourceType.MEMORY, SourceType.DOCUMENT, SourceType.SESSION]
        }
    
    def select_sources(
        self,
        intent: str,
        profile: str = None,
        explicit_sources: List[str] = None
    ) -> List[SourceType]:
        """Select sources based on intent and profile."""
        if explicit_sources:
            return [SourceType(s) for s in explicit_sources if s in [e.value for e in SourceType]]
        
        # Map intent to source type
        intent_key = self._classify_intent(intent)
        sources = self.intent_source_map.get(intent_key, self.intent_source_map["general"])
        
        # Profile-based adjustments
        if profile:
            sources = self._adjust_for_profile(sources, profile)
        
        return sources
    
    def _classify_intent(self, intent: str) -> str:
        """Classify intent string to intent type."""
        intent_lower = intent.lower()
        
        if any(kw in intent_lower for kw in ["执行", "运行", "execute", "run"]):
            return "task_execution"
        elif any(kw in intent_lower for kw in ["查找", "搜索", "find", "search", "retrieve"]):
            return "information_retrieval"
        elif any(kw in intent_lower for kw in ["错误", "问题", "error", "issue", "troubleshoot"]):
            return "troubleshooting"
        elif any(kw in intent_lower for kw in ["架构", "设计", "architecture", "design"]):
            return "architecture_query"
        elif any(kw in intent_lower for kw in ["技能", "skill", "能力"]):
            return "skill_discovery"
        elif any(kw in intent_lower for kw in ["合规", "规则", "compliance", "rule"]):
            return "compliance_check"
        else:
            return "general"
    
    def _adjust_for_profile(self, sources: List[SourceType], profile: str) -> List[SourceType]:
        """Adjust sources based on profile."""
        # Profile-specific source priorities
        profile_priorities = {
            "developer": [SourceType.DOCUMENT, SourceType.RULE, SourceType.SKILL],
            "operator": [SourceType.REPORT, SourceType.RULE, SourceType.MEMORY],
            "auditor": [SourceType.RULE, SourceType.REPORT, SourceType.DOCUMENT]
        }
        
        if profile in profile_priorities:
            priority = profile_priorities[profile]
            # Reorder sources by priority
            sources = sorted(sources, key=lambda s: priority.index(s) if s in priority else 999)
        
        return sources
