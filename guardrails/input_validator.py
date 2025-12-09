"""Input validation for tool calls."""

from typing import Dict, Any, Optional, List, Tuple
from utils.config import config
from utils.logger import logger


class InputValidator:
    """Validates tool input parameters."""
    
    def __init__(self):
        self.enabled = config.enable_input_validation
        self.max_string_length = 10000
        self.max_list_length = 100
    
    def validate_tool_input(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate tool input parameters.
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, None
        
        try:
            # General validations
            if not isinstance(parameters, dict):
                return False, "Parameters must be a dictionary"
            
            # Tool-specific validations
            if tool_name == "search_web":
                return self._validate_search_web(parameters)
            elif tool_name == "read_url":
                return self._validate_read_url(parameters)
            elif tool_name == "write_report":
                return self._validate_write_report(parameters)
            else:
                # Generic validation for unknown tools
                return self._validate_generic(parameters)
        
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _validate_search_web(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate search_web parameters."""
        if "query" not in params:
            return False, "Missing required parameter: query"
        
        query = params.get("query")
        if not isinstance(query, str) or len(query.strip()) == 0:
            return False, "Query must be a non-empty string"
        
        if len(query) > self.max_string_length:
            return False, f"Query too long (max {self.max_string_length} characters)"
        
        if "num_results" in params:
            num_results = params["num_results"]
            if not isinstance(num_results, int) or num_results < 1 or num_results > 10:
                return False, "num_results must be an integer between 1 and 10"
        
        return True, None
    
    def _validate_read_url(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate read_url parameters."""
        if "url" not in params:
            return False, "Missing required parameter: url"
        
        url = params.get("url")
        if not isinstance(url, str) or len(url.strip()) == 0:
            return False, "URL must be a non-empty string"
        
        if len(url) > 2048:  # URL length limit
            return False, "URL too long (max 2048 characters)"
        
        # Basic URL format check
        if not url.startswith(("http://", "https://")):
            return False, "URL must start with http:// or https://"
        
        return True, None
    
    def _validate_write_report(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate write_report parameters."""
        required = ["title", "content", "sources"]
        for field in required:
            if field not in params:
                return False, f"Missing required parameter: {field}"
        
        title = params.get("title")
        if not isinstance(title, str) or len(title.strip()) == 0:
            return False, "Title must be a non-empty string"
        
        if len(title) > 200:
            return False, "Title too long (max 200 characters)"
        
        content = params.get("content")
        if not isinstance(content, str) or len(content.strip()) == 0:
            return False, "Content must be a non-empty string"
        
        if len(content) > 100000:  # Large but reasonable limit
            return False, "Content too long (max 100000 characters)"
        
        sources = params.get("sources")
        if not isinstance(sources, list):
            return False, "Sources must be a list"
        
        if len(sources) > self.max_list_length:
            return False, f"Too many sources (max {self.max_list_length})"
        
        for i, source in enumerate(sources):
            if not isinstance(source, str):
                return False, f"Source {i} must be a string"
            if len(source) > 2048:
                return False, f"Source {i} URL too long"
        
        return True, None
    
    def _validate_generic(self, params: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Generic validation for unknown tools."""
        # Check for suspicious patterns
        for key, value in params.items():
            if isinstance(value, str):
                # Check for potential injection attempts
                suspicious_patterns = [
                    "../",
                    "file://",
                    "javascript:",
                    "data:",
                    "<script",
                    "eval(",
                    "exec("
                ]
                
                value_lower = value.lower()
                for pattern in suspicious_patterns:
                    if pattern in value_lower:
                        logger.warning(f"Suspicious pattern detected in parameter '{key}': {pattern}")
                        return False, f"Suspicious pattern detected in parameter '{key}'"
        
        return True, None
