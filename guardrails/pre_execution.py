"""Pre-execution hooks for validating tool calls before execution."""

from typing import Dict, Any, Optional, List, Callable, Tuple
from tools.base_tool import BaseTool
from guardrails.domain_validator import DomainValidator
from guardrails.input_validator import InputValidator
from utils.logger import logger


class PreExecutionHook:
    """Pre-execution validation hook for tool calls."""
    
    def __init__(
        self,
        domain_validator: Optional[DomainValidator] = None,
        input_validator: Optional[InputValidator] = None
    ):
        self.domain_validator = domain_validator or DomainValidator()
        self.input_validator = input_validator or InputValidator()
        self.custom_hooks: List[Callable] = []
    
    def register_hook(self, hook: Callable[[str, Dict[str, Any]], Tuple[bool, Optional[str]]]) -> None:
        """Register a custom validation hook."""
        self.custom_hooks.append(hook)
    
    def validate(
        self,
        tool_name: str,
        tool: BaseTool,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a tool call before execution.
        
        Args:
            tool_name: Name of the tool
            tool: Tool instance
            parameters: Tool parameters
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.debug(f"Pre-execution validation for {tool_name}")
        
        # 1. Input validation
        is_valid, error = self.input_validator.validate_tool_input(tool_name, parameters)
        if not is_valid:
            logger.warning(f"Input validation failed: {error}")
            return False, error
        
        # 2. Domain validation (for URL-based tools)
        if tool_name == "read_url" and "url" in parameters:
            url = parameters["url"]
            is_allowed, error = self.domain_validator.is_allowed(url)
            if not is_allowed:
                logger.warning(f"Domain validation failed: {error}")
                return False, error
        
        # 3. Tool-specific validation
        is_valid, error = tool.validate_input(**parameters)
        if not is_valid:
            logger.warning(f"Tool validation failed: {error}")
            return False, error
        
        # 4. Custom hooks
        for hook in self.custom_hooks:
            is_valid, error = hook(tool_name, parameters)
            if not is_valid:
                logger.warning(f"Custom hook validation failed: {error}")
                return False, error
        
        logger.debug(f"Pre-execution validation passed for {tool_name}")
        return True, None
