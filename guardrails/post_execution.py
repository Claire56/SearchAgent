"""Post-execution hooks for validating and sanitizing tool outputs."""

from typing import Dict, Any, Optional, List, Callable
from tools.base_tool import ToolResult
from guardrails.pii_redactor import PIIRedactor
from utils.logger import logger


class PostExecutionHook:
    """Post-execution validation hook for tool outputs."""
    
    def __init__(self, pii_redactor: Optional[PIIRedactor] = None):
        self.pii_redactor = pii_redactor or PIIRedactor()
        self.custom_hooks: List[Callable] = []
    
    def register_hook(self, hook: Callable[[str, ToolResult], ToolResult]) -> None:
        """Register a custom post-execution hook."""
        self.custom_hooks.append(hook)
    
    def process(
        self,
        tool_name: str,
        result: ToolResult
    ) -> ToolResult:
        """
        Process tool result after execution.
        
        Args:
            tool_name: Name of the tool
            result: Tool result
        
        Returns:
            Processed tool result
        """
        logger.debug(f"Post-execution processing for {tool_name}")
        
        processed_result = result
        
        # 1. PII redaction
        if processed_result.success and processed_result.data:
            if isinstance(processed_result.data, dict):
                processed_result.data = self.pii_redactor.redact_tool_output(processed_result.data)
            elif isinstance(processed_result.data, str):
                redacted_text, counts = self.pii_redactor.redact(processed_result.data)
                processed_result.data = redacted_text
                if counts:
                    processed_result.metadata["redaction_info"] = counts
        
        # 2. Custom hooks
        for hook in self.custom_hooks:
            processed_result = hook(tool_name, processed_result)
        
        logger.debug(f"Post-execution processing completed for {tool_name}")
        return processed_result
