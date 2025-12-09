"""Report writing tool for generating research reports."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from tools.base_tool import BaseTool, ToolResult
from utils.config import config
from utils.logger import logger


class ReportWriterTool(BaseTool):
    """Tool for writing research reports to disk."""
    
    def __init__(self):
        super().__init__(
            name="write_report",
            description="Write a research report to a file. The report should include title, content, and sources."
        )
        self.reports_dir = Path(config.reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def execute(
        self,
        title: str,
        content: str,
        sources: List[str],
        format: str = "markdown"
    ) -> ToolResult:
        """
        Execute report writing.
        
        Args:
            title: Report title
            content: Report content
            sources: List of source URLs
            format: Output format (markdown or json)
        
        Returns:
            ToolResult with file path
        """
        try:
            # Validate input
            is_valid, error = self.validate_input(
                title=title,
                content=content,
                sources=sources,
                format=format
            )
            if not is_valid:
                return ToolResult(success=False, data=None, error=error)
            
            logger.info(f"Writing report: {title}")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "" for c in title)
            safe_title = safe_title.replace(" ", "_")[:50]
            filename = f"{safe_title}_{timestamp}.{format}"
            filepath = self.reports_dir / filename
            
            # Write report
            if format == "markdown":
                report_text = self._format_markdown(title, content, sources)
            elif format == "json":
                report_data = {
                    "title": title,
                    "content": content,
                    "sources": sources,
                    "created_at": datetime.now().isoformat()
                }
                report_text = json.dumps(report_data, indent=2)
            else:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Unsupported format: {format}"
                )
            
            filepath.write_text(report_text, encoding="utf-8")
            
            logger.info(f"Report written to: {filepath}")
            
            return ToolResult(
                success=True,
                data={
                    "filepath": str(filepath),
                    "filename": filename,
                    "format": format,
                    "size": len(report_text)
                },
                metadata={
                    "filepath": str(filepath),
                    "format": format
                }
            )
        
        except Exception as e:
            logger.error(f"Error writing report: {e}")
            return ToolResult(
                success=False,
                data=None,
                error=f"Failed to write report: {str(e)}"
            )
    
    def _format_markdown(self, title: str, content: str, sources: List[str]) -> str:
        """Format report as markdown."""
        lines = [
            f"# {title}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            content,
            "",
            "---",
            "",
            "## Sources",
            ""
        ]
        
        for i, source in enumerate(sources, 1):
            lines.append(f"{i}. {source}")
        
        return "\n".join(lines)
    
    def validate_input(
        self,
        title: str,
        content: str,
        sources: List[str],
        format: str = "markdown"
    ) -> Tuple[bool, Optional[str]]:
        """Validate report input."""
        if not title or not isinstance(title, str) or len(title.strip()) == 0:
            return False, "Title must be a non-empty string"
        
        if not content or not isinstance(content, str) or len(content.strip()) == 0:
            return False, "Content must be a non-empty string"
        
        if not isinstance(sources, list):
            return False, "Sources must be a list"
        
        if format not in ["markdown", "json"]:
            return False, "Format must be 'markdown' or 'json'"
        
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
                        "title": {
                            "type": "string",
                            "description": "The title of the research report"
                        },
                        "content": {
                            "type": "string",
                            "description": "The main content of the report"
                        },
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of source URLs cited in the report"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "description": "Output format (default: markdown)",
                            "default": "markdown"
                        }
                    },
                    "required": ["title", "content", "sources"]
                }
            }
        }
