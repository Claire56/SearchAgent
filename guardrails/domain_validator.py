"""Domain whitelisting validator."""

from urllib.parse import urlparse
from typing import List, Optional, Tuple
from utils.config import config
from utils.logger import logger


class DomainValidator:
    """Validates URLs against a whitelist of allowed domains."""
    
    def __init__(self, allowed_domains: Optional[List[str]] = None):
        self.allowed_domains = allowed_domains or config.allowed_domains
        self.enabled = config.enable_domain_whitelist
    
    def is_allowed(self, url: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a URL is in the allowed domains list.
        
        Args:
            url: URL to check
        
        Returns:
            Tuple of (is_allowed, error_message)
        """
        if not self.enabled:
            return True, None
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ":" in domain:
                domain = domain.split(":")[0]
            
            # Remove www. prefix for comparison
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Check if domain is in whitelist
            for allowed_domain in self.allowed_domains:
                allowed = allowed_domain.lower()
                if allowed.startswith("www."):
                    allowed = allowed[4:]
                
                if domain == allowed or domain.endswith(f".{allowed}"):
                    logger.debug(f"Domain allowed: {domain}")
                    return True, None
            
            error_msg = f"Domain '{domain}' is not in the whitelist. Allowed domains: {', '.join(self.allowed_domains)}"
            logger.warning(error_msg)
            return False, error_msg
        
        except Exception as e:
            logger.error(f"Error validating domain: {e}")
            return False, f"Error parsing URL: {str(e)}"
    
    def extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return None
    
    def add_domain(self, domain: str) -> None:
        """Add a domain to the whitelist."""
        domain = domain.lower().strip()
        if domain and domain not in self.allowed_domains:
            self.allowed_domains.append(domain)
            logger.info(f"Added domain to whitelist: {domain}")
