"""Base tool interface for Research Agent tools."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Result from a tool execution."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}


class BaseTool(ABC):
    """Base class for all agent tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    @abstractmethod
    def get_function_schema(self) -> Dict[str, Any]:
        """Get OpenAI function calling schema for this tool."""
        pass
    
    def validate_input(self, **kwargs) -> Tuple[bool, Optional[str]]:
        """Validate input parameters. Override for custom validation."""
        return True, None
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"
