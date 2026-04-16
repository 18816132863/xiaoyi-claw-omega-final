"""Conflict resolver for context sources."""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Conflict:
    """Represents a conflict between sources."""
    source_a: str
    source_b: str
    conflict_type: str  # contradiction, overlap, outdated
    description: str
    resolution: str
    winner: str


class ConflictResolver:
    """Resolves conflicts between context sources."""
    
    def __init__(self):
        self.resolution_strategies = {
            "contradiction": self._resolve_contradiction,
            "overlap": self._resolve_overlap,
            "outdated": self._resolve_outdated
        }
    
    def resolve(self, sources: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Resolve conflicts between sources.
        
        Returns:
            Tuple of (resolved_sources, conflicts)
        """
        conflicts = []
        resolved = []
        seen = set()
        
        for i, source_a in enumerate(sources):
            source_id_a = source_a.get("source_id", str(i))
            
            if source_id_a in seen:
                continue
            
            # Check against remaining sources
            for j, source_b in enumerate(sources[i+1:], i+1):
                source_id_b = source_b.get("source_id", str(j))
                
                conflict = self._detect_conflict(source_a, source_b)
                if conflict:
                    conflicts.append(conflict)
                    
                    # Mark loser as seen (don't include)
                    if conflict.winner == source_id_a:
                        seen.add(source_id_b)
                    else:
                        seen.add(source_id_a)
                        break
            
            if source_id_a not in seen:
                resolved.append(source_a)
        
        return resolved, [c.__dict__ for c in conflicts]
    
    def _detect_conflict(self, source_a: Dict, source_b: Dict) -> Optional[Conflict]:
        """Detect conflict between two sources."""
        # Check for contradiction
        if self._is_contradiction(source_a, source_b):
            return self._resolve_contradiction(source_a, source_b)
        
        # Check for overlap
        if self._is_overlap(source_a, source_b):
            return self._resolve_overlap(source_a, source_b)
        
        # Check for outdated
        if self._is_outdated(source_a, source_b):
            return self._resolve_outdated(source_a, source_b)
        
        return None
    
    def _is_contradiction(self, source_a: Dict, source_b: Dict) -> bool:
        """Check if sources contradict each other."""
        # Simple heuristic: check for negation patterns
        content_a = source_a.get("content", "").lower()
        content_b = source_b.get("content", "").lower()
        
        # TODO: Implement more sophisticated contradiction detection
        return False
    
    def _is_overlap(self, source_a: Dict, source_b: Dict) -> bool:
        """Check if sources overlap significantly."""
        content_a = set(source_a.get("content", "").lower().split())
        content_b = set(source_b.get("content", "").lower().split())
        
        if not content_a or not content_b:
            return False
        
        overlap = len(content_a & content_b) / min(len(content_a), len(content_b))
        return overlap > 0.8
    
    def _is_outdated(self, source_a: Dict, source_b: Dict) -> bool:
        """Check if one source is outdated compared to another."""
        time_a = source_a.get("created_at")
        time_b = source_b.get("created_at")
        
        if not time_a or not time_b:
            return False
        
        # If same source type and one is much older
        if source_a.get("source_type") == source_b.get("source_type"):
            # TODO: Compare timestamps
            pass
        
        return False
    
    def _resolve_contradiction(self, source_a: Dict, source_b: Dict) -> Conflict:
        """Resolve contradiction between sources."""
        # Prefer higher importance
        importance_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        imp_a = importance_order.get(source_a.get("metadata", {}).get("importance", "medium"), 2)
        imp_b = importance_order.get(source_b.get("metadata", {}).get("importance", "medium"), 2)
        
        if imp_a >= imp_b:
            winner = source_a.get("source_id", "a")
        else:
            winner = source_b.get("source_id", "b")
        
        return Conflict(
            source_a=source_a.get("source_id", "a"),
            source_b=source_b.get("source_id", "b"),
            conflict_type="contradiction",
            description="Sources contradict each other",
            resolution="Selected higher importance source",
            winner=winner
        )
    
    def _resolve_overlap(self, source_a: Dict, source_b: Dict) -> Conflict:
        """Resolve overlap between sources."""
        # Prefer more recent or higher relevance
        rel_a = source_a.get("relevance", 0)
        rel_b = source_b.get("relevance", 0)
        
        winner = source_a.get("source_id", "a") if rel_a >= rel_b else source_b.get("source_id", "b")
        
        return Conflict(
            source_a=source_a.get("source_id", "a"),
            source_b=source_b.get("source_id", "b"),
            conflict_type="overlap",
            description="Sources overlap significantly",
            resolution="Selected higher relevance source",
            winner=winner
        )
    
    def _resolve_outdated(self, source_a: Dict, source_b: Dict) -> Conflict:
        """Resolve outdated source."""
        # Prefer more recent
        winner = source_b.get("source_id", "b")  # Assume b is newer
        
        return Conflict(
            source_a=source_a.get("source_id", "a"),
            source_b=source_b.get("source_id", "b"),
            conflict_type="outdated",
            description="One source is outdated",
            resolution="Selected more recent source",
            winner=winner
        )
