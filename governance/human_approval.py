"""Human-in-the-loop approval system."""

from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from utils.config import config
from utils.logger import logger


class ApprovalStatus(Enum):
    """Approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class HumanApproval:
    """Manages human-in-the-loop approvals for critical operations."""
    
    def __init__(self, enabled: Optional[bool] = None):
        self.enabled = enabled if enabled is not None else config.require_human_approval
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
    
    def requires_approval(self, operation: str, context: Dict[str, Any]) -> bool:
        """
        Check if an operation requires human approval.
        
        Args:
            operation: Operation type (e.g., "write_report", "read_url")
            context: Operation context
        
        Returns:
            True if approval is required
        """
        if not self.enabled:
            return False
        
        # Critical operations that always require approval
        critical_operations = ["write_report"]
        
        # Operations that require approval for sensitive domains
        sensitive_domain_operations = ["read_url"]
        
        if operation in critical_operations:
            return True
        
        if operation in sensitive_domain_operations:
            # Check if URL is from a sensitive domain
            url = context.get("url", "")
            if self._is_sensitive_domain(url):
                return True
        
        return False
    
    def _is_sensitive_domain(self, url: str) -> bool:
        """Check if URL is from a sensitive domain."""
        # Example: You might want to require approval for certain domains
        sensitive_domains = [
            # Add domains that require approval
        ]
        
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return any(sd in domain for sd in sensitive_domains)
        except Exception:
            return False
    
    def request_approval(
        self,
        operation: str,
        context: Dict[str, Any],
        approval_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Request human approval for an operation.
        
        Args:
            operation: Operation type
            context: Operation context
            approval_id: Optional approval ID (auto-generated if not provided)
        
        Returns:
            Tuple of (is_approved, approval_id)
        """
        if not self.requires_approval(operation, context):
            return True, None
        
        import uuid
        if approval_id is None:
            approval_id = str(uuid.uuid4())
        
        self.pending_approvals[approval_id] = {
            "operation": operation,
            "context": context,
            "status": ApprovalStatus.PENDING,
            "created_at": self._get_timestamp()
        }
        
        logger.warning(f"Human approval required for {operation}")
        logger.info(f"Approval ID: {approval_id}")
        logger.info(f"Context: {context}")
        
        # In a real implementation, this would integrate with a UI or notification system
        # For now, we'll use a simple prompt
        print(f"\n⚠️  HUMAN APPROVAL REQUIRED")
        print(f"Operation: {operation}")
        print(f"Approval ID: {approval_id}")
        print(f"Context: {context}")
        print(f"\nApprove? (yes/no): ", end="")
        
        response = input().strip().lower()
        
        if response in ["yes", "y"]:
            self.approve(approval_id)
            return True, approval_id
        else:
            self.reject(approval_id, reason="User rejected")
            return False, approval_id
    
    def approve(self, approval_id: str, reason: Optional[str] = None) -> None:
        """Approve a pending operation."""
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Approval ID not found: {approval_id}")
        
        self.pending_approvals[approval_id]["status"] = ApprovalStatus.APPROVED
        self.pending_approvals[approval_id]["approved_at"] = self._get_timestamp()
        if reason:
            self.pending_approvals[approval_id]["reason"] = reason
        
        logger.info(f"Approval granted: {approval_id}")
    
    def reject(self, approval_id: str, reason: Optional[str] = None) -> None:
        """Reject a pending operation."""
        if approval_id not in self.pending_approvals:
            raise ValueError(f"Approval ID not found: {approval_id}")
        
        self.pending_approvals[approval_id]["status"] = ApprovalStatus.REJECTED
        self.pending_approvals[approval_id]["rejected_at"] = self._get_timestamp()
        if reason:
            self.pending_approvals[approval_id]["reason"] = reason
        
        logger.warning(f"Approval rejected: {approval_id} - {reason}")
    
    def get_status(self, approval_id: str) -> Optional[ApprovalStatus]:
        """Get approval status."""
        if approval_id not in self.pending_approvals:
            return None
        return self.pending_approvals[approval_id]["status"]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
