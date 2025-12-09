"""Policy compliance checker."""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse
from utils.config import config
from utils.logger import logger


class PolicyChecker:
    """Checks agent actions against policies."""
    
    def __init__(self, policy_file: Optional[str] = None):
        self.policy_file = Path(policy_file or config.policy_file)
        self.policy: Dict[str, Any] = self._load_policy()
    
    def _load_policy(self) -> Dict[str, Any]:
        """Load policy from file."""
        if self.policy_file.exists():
            try:
                with open(self.policy_file, "r") as f:
                    policy = json.load(f)
                logger.info(f"Loaded policy from {self.policy_file}")
                return policy
            except Exception as e:
                logger.warning(f"Failed to load policy file: {e}. Using default policy.")
        
        # Default policy
        return {
            "must_cite_sources": True,
            "min_sources": 3,
            "max_urls_per_domain": 5,
            "require_peer_reviewed": False,
            "max_report_length": 10000,
            "forbidden_domains": []
        }
    
    def check_plan(self, plan: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check a plan against policies.
        
        Args:
            plan: Plan dictionary
        
        Returns:
            Tuple of (is_compliant, violations)
        """
        violations = []
        
        # Check source requirements
        if self.policy.get("must_cite_sources", True):
            sources = plan.get("sources", [])
            if not sources:
                violations.append("Plan must include sources")
            elif len(sources) < self.policy.get("min_sources", 3):
                violations.append(f"Plan must include at least {self.policy.get('min_sources')} sources")
        
        # Check domain limits
        max_per_domain = self.policy.get("max_urls_per_domain", 5)
        if "sources" in plan:
            from collections import Counter
            from urllib.parse import urlparse
            
            domains = []
            for source in plan.get("sources", []):
                try:
                    parsed = urlparse(source)
                    domains.append(parsed.netloc)
                except Exception:
                    pass
            
            domain_counts = Counter(domains)
            for domain, count in domain_counts.items():
                if count > max_per_domain:
                    violations.append(f"Too many URLs from {domain} (max {max_per_domain})")
        
        # Check forbidden domains
        forbidden = self.policy.get("forbidden_domains", [])
        if "sources" in plan:
            for source in plan.get("sources", []):
                try:
                    parsed = urlparse(source)
                    if parsed.netloc in forbidden:
                        violations.append(f"Forbidden domain: {parsed.netloc}")
                except Exception:
                    pass
        
        is_compliant = len(violations) == 0
        
        if violations:
            logger.warning(f"Policy violations: {violations}")
        else:
            logger.info("Plan complies with policy")
        
        return is_compliant, violations
    
    def check_report(self, report: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check a report against policies.
        
        Args:
            report: Report dictionary
        
        Returns:
            Tuple of (is_compliant, violations)
        """
        violations = []
        
        # Check source citations
        if self.policy.get("must_cite_sources", True):
            sources = report.get("sources", [])
            if not sources:
                violations.append("Report must cite sources")
            elif len(sources) < self.policy.get("min_sources", 3):
                violations.append(f"Report must cite at least {self.policy.get('min_sources')} sources")
        
        # Check report length
        max_length = self.policy.get("max_report_length", 10000)
        content = report.get("content", "")
        if len(content) > max_length:
            violations.append(f"Report too long (max {max_length} characters)")
        
        is_compliant = len(violations) == 0
        
        if violations:
            logger.warning(f"Report policy violations: {violations}")
        else:
            logger.info("Report complies with policy")
        
        return is_compliant, violations
    
    def update_policy(self, updates: Dict[str, Any]) -> None:
        """Update policy with new values."""
        self.policy.update(updates)
        logger.info(f"Policy updated: {updates}")
        
        # Save to file
        try:
            self.policy_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.policy_file, "w") as f:
                json.dump(self.policy, f, indent=2)
            logger.info(f"Policy saved to {self.policy_file}")
        except Exception as e:
            logger.warning(f"Failed to save policy: {e}")
