"""ReAct (Reasoning + Acting) loop implementation."""

from typing import Dict, Any, List, Optional, Callable, Tuple
from tools.base_tool import BaseTool, ToolResult
from agent.state_manager import AgentState
from utils.llm_client import BaseLLMClient
from utils.config import config
from utils.logger import logger


class ReActLoop:
    """Implements the ReAct reasoning loop."""
    
    def __init__(
        self,
        client: BaseLLMClient,
        tools: List[BaseTool],
        max_iterations: Optional[int] = None
    ):
        self.client = client
        self.tools = {tool.name: tool for tool in tools}
        self.max_iterations = max_iterations or config.max_iterations
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI function schemas for all tools."""
        return [tool.get_function_schema() for tool in self.tools.values()]
    
    def think_and_act(
        self,
        state: AgentState,
        pre_execution_hook: Optional[Callable] = None,
        post_execution_hook: Optional[Callable] = None
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        Execute one iteration of the ReAct loop.
        
        Args:
            state: Current agent state
            pre_execution_hook: Optional hook to call before tool execution
            post_execution_hook: Optional hook to call after tool execution
        
        Returns:
            Tuple of (thought, action_result)
        """
        # Build conversation history
        messages = self._build_messages(state)
        
        # Get tool schemas
        tool_schemas = self.get_tool_schemas()
        
        # Call LLM with function calling using abstract client
        response = self.client.create_chat_completion(
            messages=messages,
            tools=tool_schemas if tool_schemas else None,
            tool_choice="auto",
            temperature=0.7
        )
        
        message = response.choices[0].message
        
        # Extract thought
        thought = message.content or ""
        
        # Check if tool call was requested
        tool_calls = message.tool_calls
        
        if tool_calls:
            # Execute tool calls
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = self._parse_tool_args(tool_call.function.arguments)
                
                logger.info(f"Tool call: {tool_name} with args: {tool_args}")
                
                # Pre-execution hook
                if pre_execution_hook:
                    is_valid, error = pre_execution_hook(tool_name, self.tools.get(tool_name), tool_args)
                    if not is_valid:
                        observation = f"Error: {error}"
                        state.add_observation(observation)
                        return thought, {"error": error}
                
                # Execute tool
                if tool_name not in self.tools:
                    observation = f"Error: Unknown tool {tool_name}"
                    state.add_observation(observation)
                    return thought, {"error": observation}
                
                tool = self.tools[tool_name]
                result = tool.execute(**tool_args)
                
                # Post-execution hook
                if post_execution_hook:
                    result = post_execution_hook(tool_name, result)
                
                # Process result
                if result.success:
                    observation = self._format_observation(tool_name, result.data)
                    state.add_observation(observation)
                    state.add_action({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": result.data
                    })
                    
                    # Extract sources if applicable
                    if tool_name == "read_url" and isinstance(result.data, dict):
                        state.add_source(result.data.get("url", ""))
                    elif tool_name == "search_web" and isinstance(result.data, dict):
                        for res in result.data.get("results", []):
                            state.add_source(res.get("url", ""))
                    
                    return thought, result.data
                else:
                    observation = f"Error: {result.error}"
                    state.add_observation(observation)
                    return thought, {"error": result.error}
        
        # No tool call, just thought
        return thought, None
    
    def _build_messages(self, state: AgentState) -> List[Dict[str, Any]]:
        """Build conversation messages from state."""
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            }
        ]
        
        # Add query
        messages.append({
            "role": "user",
            "content": f"Research query: {state.query}"
        })
        
        # Add conversation history (thoughts, actions, observations)
        for i in range(len(state.thoughts)):
            # Thought
            if i < len(state.thoughts):
                messages.append({
                    "role": "assistant",
                    "content": f"Thought: {state.thoughts[i]}"
                })
            
            # Action and observation
            if i < len(state.actions) and i < len(state.observations):
                action = state.actions[i]
                observation = state.observations[i]
                
                # Format action as tool call
                tool_call_id = f"call_{i}"
                messages.append({
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [{
                        "id": tool_call_id,
                        "type": "function",
                        "function": {
                            "name": action["tool"],
                            "arguments": str(action["args"])
                        }
                    }]
                })
                
                messages.append({
                    "role": "tool",
                    "content": observation,
                    "tool_call_id": tool_call_id
                })
        
        return messages
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent."""
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        return f"""You are a research agent that helps users gather information and create research reports.

Current date: {current_date}

Your goal is to:
1. Understand the research query
2. Search for relevant information using available tools
3. Read and extract content from relevant sources (aim for 1-3 quality sources)
4. Synthesize the information
5. CREATE A RESEARCH REPORT - this is your PRIMARY objective

IMPORTANT: When searching for information, always consider the current date above. For queries about "latest" or recent events, use appropriate years in your search (e.g., if today is 2025, search for 2026 for upcoming events, not past years).

Available tools:
- search_web: Search the web for information
- read_url: Read and extract content from a URL
- write_report: Write a research report to a file

Follow the ReAct pattern:
1. Think about what you need to do next
2. Use tools to gather information
3. Observe the results
4. **WRITE THE REPORT as soon as you have sufficient information (even from 1-2 sources)**

CRITICAL RULES:
- DO NOT read the same URL multiple times
- DO NOT search endlessly - 1-3 quality sources is enough
- ALWAYS call write_report before you run out of iterations
- If a URL is blocked or returns an error, try a different source instead
- Your task is NOT complete until you call write_report

Always cite your sources in the final report."""
    
    def _parse_tool_args(self, args_str: str) -> Dict[str, Any]:
        """Parse tool arguments from JSON string."""
        import json
        try:
            return json.loads(args_str)
        except json.JSONDecodeError:
            # Fallback: try to parse as Python dict
            try:
                return eval(args_str)
            except Exception:
                return {}
    
    def _format_observation(self, tool_name: str, data: Any) -> str:
        """Format tool result as observation."""
        if isinstance(data, dict):
            if tool_name == "search_web":
                results = data.get("results", [])
                if results:
                    return f"Found {len(results)} search results. Top results: {', '.join([r.get('title', '') for r in results[:3]])}"
                return "No search results found."
            
            elif tool_name == "read_url":
                title = data.get("title", "Unknown")
                content_length = data.get("content_length", 0)
                return f"Read article '{title}' ({content_length} characters)"
            
            elif tool_name == "write_report":
                filepath = data.get("filepath", "Unknown")
                return f"Report written to {filepath}"
        
        return str(data)
