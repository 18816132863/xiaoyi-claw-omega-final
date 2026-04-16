"""Session summary generation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SessionSummary:
    """Summary of a completed session."""
    session_id: str
    task_id: Optional[str]
    start_time: datetime
    end_time: datetime
    status: str
    steps_completed: int
    steps_failed: int
    skills_used: list[str]
    key_decisions: list[str]
    outcome: str
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "task_id": self.task_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "status": self.status,
            "steps_completed": self.steps_completed,
            "steps_failed": self.steps_failed,
            "skills_used": self.skills_used,
            "key_decisions": self.key_decisions,
            "outcome": self.outcome
        }


class SessionSummarizer:
    """Generates session summaries."""
    
    def __init__(self):
        self.summaries: list[SessionSummary] = []
    
    def create_summary(
        self,
        session_id: str,
        task_id: str,
        start_time: datetime,
        end_time: datetime,
        status: str,
        steps_completed: int,
        steps_failed: int,
        skills_used: list[str],
        key_decisions: list[str],
        outcome: str
    ) -> SessionSummary:
        summary = SessionSummary(
            session_id=session_id,
            task_id=task_id,
            start_time=start_time,
            end_time=end_time,
            status=status,
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            skills_used=skills_used,
            key_decisions=key_decisions,
            outcome=outcome
        )
        self.summaries.append(summary)
        return summary
    
    def get_by_session(self, session_id: str) -> Optional[SessionSummary]:
        for s in self.summaries:
            if s.session_id == session_id:
                return s
        return None
    
    def get_recent(self, n: int = 10) -> list[SessionSummary]:
        return self.summaries[-n:]
