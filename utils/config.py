"""Configuration management for the Research Agent."""

import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    agent_model: str = os.getenv("AGENT_MODEL", "gpt-4")
    
    # Serper API
    serper_api_key: str = os.getenv("SERPER_API_KEY", "")
    
    # Agent Configuration
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))
    max_tool_calls_per_step: int = int(os.getenv("MAX_TOOL_CALLS_PER_STEP", "1"))
    
    # Safety & Governance
    require_human_approval: bool = os.getenv("REQUIRE_HUMAN_APPROVAL", "false").lower() == "true"
    enable_rollback: bool = os.getenv("ENABLE_ROLLBACK", "true").lower() == "true"
    policy_file: str = os.getenv("POLICY_FILE", "policies/default_policy.json")
    
    # Guardrails
    enable_domain_whitelist: bool = os.getenv("ENABLE_DOMAIN_WHITELIST", "true").lower() == "true"
    enable_pii_redaction: bool = os.getenv("ENABLE_PII_REDACTION", "true").lower() == "true"
    enable_input_validation: bool = os.getenv("ENABLE_INPUT_VALIDATION", "true").lower() == "true"
    
    # Domain Whitelist (default safe domains for research)
    allowed_domains: List[str] = [
        "arxiv.org",
        "nature.com",
        "science.org",
        "github.com",
        "stackoverflow.com",
        "wikipedia.org",
        "ieee.org",
        "acm.org",
        "scholar.google.com",
        "pubmed.ncbi.nlm.nih.gov",
    ]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/agent.log")
    
    # Data directories
    state_dir: str = "data/state"
    reports_dir: str = "data/reports"
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        if not cls.serper_api_key:
            raise ValueError("SERPER_API_KEY is required")


config = Config()
