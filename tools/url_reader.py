"""URL reading tool for extracting content from web pages."""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from tools.base_tool import BaseTool, ToolResult
from utils.logger import logger


class URLReaderTool(BaseTool):
    """Tool for reading and extracting content from URLs."""
    
    def __init__(self):
        super().__init__(
            name="read_url",
            description="Read and extract text content from a URL. Returns the main content of the webpage."
        )
        self.timeout = 10
        self.max_content_length = 50000  # Limit content size
    
    def execute(self, url: str) -> ToolResult:
        """
        Execute URL reading.
        
        Args:
            url: URL to read
        
        Returns:
            ToolResult with extracted content
        """
        try:
            # Validate input
            is_valid, error = self.validate_input(url=url)
            if not is_valid:
                return ToolResult(success=False, data=None, error=error)
            
            logger.info(f"Reading URL: {url}")
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get("content-type", "").lower()
            if "text/html" not in content_type and "text/plain" not in content_type:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unsupported content type: {content_type}"
                )
            
            # Parse HTML
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text(separator="\n", strip=True)
            
            # Truncate if too long
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + "\n\n[Content truncated...]"
            
            # Extract title
            title = soup.find("title")
            title_text = title.get_text(strip=True) if title else "No title"
            
            # Extract meta description
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc.get("content", "") if meta_desc else ""
            
            logger.info(f"Successfully read URL: {url} ({len(text)} characters)")
            
            return ToolResult(
                success=True,
                data={
                    "url": url,
                    "title": title_text,
                    "description": description,
                    "content": text,
                    "content_length": len(text)
                },
                metadata={
                    "url": url,
                    "content_length": len(text)
                }
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"URL reading error: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to fetch URL: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error reading URL: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Unexpected error: {str(e)}"
            )
    
    def validate_input(self, url: str) -> Tuple[bool, Optional[str]]:
        """Validate URL input."""
        if not url or not isinstance(url, str):
            return False, "URL must be a non-empty string"
        
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "URL must have a valid scheme (http/https) and domain"
        except Exception:
            return False, "Invalid URL format"
        
        return True, None
    
    def get_function_schema(self) -> Dict[str, Any]:
        """Get OpenAI function calling schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to read and extract content from"
                        }
                    },
                    "required": ["url"]
                }
            }
        }
