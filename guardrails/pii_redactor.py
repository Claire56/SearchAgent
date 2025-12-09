"""PII (Personally Identifiable Information) redaction."""

import re
from typing import Dict, Any, List, Optional
from utils.config import config
from utils.logger import logger


class PIIRedactor:
    """Redacts PII from text content."""
    
    def __init__(self):
        self.enabled = config.enable_pii_redaction
        
        # Regex patterns for different PII types
        self.patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "credit_card": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
        }
    
    def redact(self, text: str) -> Tuple[str, Dict[str, int]]:
        """
        Redact PII from text.
        
        Args:
            text: Text to redact
        
        Returns:
            Tuple of (redacted_text, redaction_counts)
        """
        if not self.enabled:
            return text, {}
        
        redacted = text
        counts = {}
        
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(redacted)
            count = len(matches) if isinstance(matches, list) else 1 if matches else 0
            
            if count > 0:
                if pii_type == "email":
                    redacted = pattern.sub("[EMAIL_REDACTED]", redacted)
                elif pii_type == "phone":
                    redacted = pattern.sub("[PHONE_REDACTED]", redacted)
                elif pii_type == "ssn":
                    redacted = pattern.sub("[SSN_REDACTED]", redacted)
                elif pii_type == "credit_card":
                    redacted = pattern.sub("[CARD_REDACTED]", redacted)
                elif pii_type == "ip_address":
                    # Only redact if it looks like a private IP or suspicious
                    redacted = pattern.sub(lambda m: self._redact_ip(m.group()), redacted)
                
                counts[pii_type] = count
                logger.debug(f"Redacted {count} {pii_type} instances")
        
        if counts:
            logger.info(f"Redacted PII: {counts}")
        
        return redacted, counts
    
    def _redact_ip(self, ip: str) -> str:
        """Redact IP address if it's private or suspicious."""
        parts = ip.split(".")
        if len(parts) == 4:
            first_octet = int(parts[0])
            # Redact private IPs (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
            if (first_octet == 10 or
                first_octet == 192 or
                (first_octet == 172 and 16 <= int(parts[1]) <= 31)):
                return "[IP_REDACTED]"
        return ip  # Don't redact public IPs by default
    
    def redact_tool_output(self, tool_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Redact PII from tool output.
        
        Args:
            tool_result: Tool result dictionary
        
        Returns:
            Redacted tool result
        """
        if not self.enabled:
            return tool_result
        
        redacted_result = tool_result.copy()
        
        # Redact from common text fields
        text_fields = ["content", "snippet", "description", "data"]
        
        for field in text_fields:
            if field in redacted_result and isinstance(redacted_result[field], str):
                redacted_result[field], counts = self.redact(redacted_result[field])
                if counts:
                    redacted_result.setdefault("redaction_info", {})[field] = counts
        
        # Handle nested data structures
        if "data" in redacted_result and isinstance(redacted_result["data"], dict):
            redacted_data = redacted_result["data"].copy()
            
            # Redact from results list
            if "results" in redacted_data and isinstance(redacted_data["results"], list):
                for result in redacted_data["results"]:
                    if isinstance(result, dict):
                        for key in ["snippet", "content", "description"]:
                            if key in result and isinstance(result[key], str):
                                result[key], _ = self.redact(result[key])
            
            redacted_result["data"] = redacted_data
        
        return redacted_result
