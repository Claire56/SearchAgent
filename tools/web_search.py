"""Web search tool using Serper API."""

import requests
from typing import Dict, Any, Optional, Tuple
from tools.base_tool import BaseTool, ToolResult
from utils.config import config
from utils.logger import logger


class WebSearchTool(BaseTool):
    """Tool for searching the web using Serper API."""
    
    def __init__(self):
        super().__init__(
            name="search_web",
            description="Search the web for information. Returns a list of relevant URLs and snippets."
        )
        self.api_key = config.serper_api_key
        self.base_url = "https://google.serper.dev/search"
    
    def execute(self, query: str, num_results: int = 10) -> ToolResult:
        """
        Execute web search.
        
        Args:
            query: Search query string
            num_results: Number of results to return (default: 10)
        
        Returns:
            ToolResult with search results
        """
        try:
            # Validate input
            is_valid, error = self.validate_input(query=query, num_results=num_results)
            if not is_valid:
                return ToolResult(success=False, data=None, error=error)
            
            logger.info(f"Searching web for: {query}")
            
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": min(num_results, 10)  # Serper API limit
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract results
            results = []
            organic_results = data.get("organic", [])
            
            for result in organic_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0)
                })
            
            logger.info(f"Found {len(results)} search results")
            
            return ToolResult(
                success=True,
                data={
                    "results": results,
                    "query": query,
                    "total_results": len(results)
                },
                metadata={
                    "num_results": len(results),
                    "query": query
                }
            )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Web search error: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Search API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in web search: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Unexpected error: {str(e)}"
            )
    
    def validate_input(self, query: str, num_results: int = 10) -> Tuple[bool, Optional[str]]:
        """Validate search input."""
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            return False, "Query must be a non-empty string"
        
        if not isinstance(num_results, int) or num_results < 1 or num_results > 10:
            return False, "num_results must be an integer between 1 and 10"
        
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
                        "query": {
                            "type": "string",
                            "description": "The search query string"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results to return (1-10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            }
        }
