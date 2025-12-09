"""Agent state management."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class AgentState:
    """Represents the current state of the agent."""
    
    query: str
    iteration: int = 0
    thoughts: List[str] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    collected_info: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    final_answer: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        """Create state from dictionary."""
        return cls(**data)
    
    def add_thought(self, thought: str) -> None:
        """Add a thought."""
        self.thoughts.append(thought)
        self.updated_at = datetime.now().isoformat()
    
    def add_action(self, action: Dict[str, Any]) -> None:
        """Add an action."""
        self.actions.append(action)
        self.updated_at = datetime.now().isoformat()
    
    def add_observation(self, observation: str) -> None:
        """Add an observation."""
        self.observations.append(observation)
        self.updated_at = datetime.now().isoformat()
    
    def add_info(self, info: Dict[str, Any]) -> None:
        """Add collected information."""
        self.collected_info.append(info)
        self.updated_at = datetime.now().isoformat()
    
    def add_source(self, source: str) -> None:
        """Add a source URL."""
        if source not in self.sources:
            self.sources.append(source)
            self.updated_at = datetime.now().isoformat()
    
    def increment_iteration(self) -> None:
        """Increment iteration counter."""
        self.iteration += 1
        self.updated_at = datetime.now().isoformat()
    
    def set_final_answer(self, answer: str) -> None:
        """Set final answer."""
        self.final_answer = answer
        self.updated_at = datetime.now().isoformat()
