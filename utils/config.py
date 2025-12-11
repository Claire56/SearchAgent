"""Configuration management for the Research Agent."""

import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration.
    
    LLM Provider Configuration:
    - Default: Azure OpenAI (if AZURE_OPENAI_KEY is set)
    - Fallback: Regular OpenAI (if OPENAI_API_KEY is set)
    
    The factory will automatically choose Azure OpenAI if credentials are available.
    """
    
    # Azure OpenAI Configuration (DEFAULT)
    azure_openai_key: str = os.getenv("AZURE_OPENAI_KEY", "")
    azure_openai_endpoint: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    azure_openai_deployment: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
    azure_api_version: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Regular OpenAI Configuration (FALLBACK)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    agent_model: str = os.getenv("AGENT_MODEL", "gpt-4")
    
    # Serper API (OPTIONAL - Uses DuckDuckGo if not provided)
    # Get a Serper API key from https://serper.dev if you want to use it
    # Otherwise, DuckDuckGo will be used automatically (FREE, no API key needed)
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
        "observer.ug",
        "newvision.co.ug",
        "kigezi.co.ug",
        "dailymonitor.com",
        "dailymonitor.co.ug",
        "monitor.co.ug",
        "ntv.co.ug",
        "theeastafrican.co.ke",
         "africanews.com",
        "aljazeera.com",
        "aljazeera.net",
        "aljazeera.org",
        "aljazeera.tv",
        "aljazeera.com.au",
        "aljazeera.com.br",
        "aljazeera.com.mx",
        "aljazeera.com.ar",
        "aljazeera.com.es",
        "nationalgeographic.com",
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
        """
        Validate required configuration.
        
        The factory pattern will try Azure OpenAI first (default),
        then fall back to regular OpenAI if Azure credentials aren't available.
        At least one set of credentials must be provided.
        """
        has_azure = bool(cls.azure_openai_key and cls.azure_openai_endpoint and cls.azure_openai_deployment)
        has_openai = bool(cls.openai_api_key)
        
        if not has_azure and not has_openai:
            raise ValueError(
                "No LLM provider configured. Please provide either:\n"
                "1. Azure OpenAI (DEFAULT): AZURE_OPENAI_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT\n"
                "2. Regular OpenAI (FALLBACK): OPENAI_API_KEY"
            )
        
        # SERPER_API_KEY is optional - DuckDuckGo will be used if not provided
        # No validation needed for search API


config = Config()
