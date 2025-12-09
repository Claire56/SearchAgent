"""Main Research Agent implementation."""

from typing import Dict, Any, Optional, List, Tuple
from openai import OpenAI
from tools.base_tool import BaseTool
from agent.react_loop import ReActLoop
from agent.state_manager import AgentState
from guardrails.pre_execution import PreExecutionHook
from guardrails.post_execution import PostExecutionHook
from governance.human_approval import HumanApproval
from governance.policy_checker import PolicyChecker
from governance.rollback_manager import RollbackManager
from utils.config import config
from utils.logger import logger


class ResearchAgent:
    """Main Research Agent with ReAct pattern, guardrails, and governance."""
    
    def __init__(
        self,
        tools: List[BaseTool],
        require_approval: Optional[bool] = None,
        policy_file: Optional[str] = None
    ):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=config.openai_api_key)
        
        # Initialize ReAct loop
        self.react_loop = ReActLoop(self.client, tools)
        
        # Initialize guardrails
        self.pre_execution_hook = PreExecutionHook()
        self.post_execution_hook = PostExecutionHook()
        
        # Initialize governance
        self.human_approval = HumanApproval(enabled=require_approval)
        self.policy_checker = PolicyChecker(policy_file=policy_file)
        self.rollback_manager = RollbackManager()
        
        # Tools
        self.tools = {tool.name: tool for tool in tools}
    
    def research(self, query: str) -> Dict[str, Any]:
        """
        Execute research query.
        
        Args:
            query: Research query string
        
        Returns:
            Dictionary with research results
        """
        logger.info(f"Starting research: {query}")
        
        # Initialize state
        state = AgentState(query=query)
        
        # Create initial checkpoint
        checkpoint_id = self.rollback_manager.create_checkpoint(state.to_dict())
        logger.info(f"Initial checkpoint: {checkpoint_id}")
        
        try:
            # Main ReAct loop
            for iteration in range(config.max_iterations):
                state.increment_iteration()
                logger.info(f"Iteration {state.iteration}/{config.max_iterations}")
                
                # Create checkpoint before iteration
                checkpoint_id = self.rollback_manager.create_checkpoint(state.to_dict())
                
                # Think and act
                thought, action_result = self.react_loop.think_and_act(
                    state,
                    pre_execution_hook=self._pre_execution_wrapper,
                    post_execution_hook=self._post_execution_wrapper
                )
                
                # Add thought
                state.add_thought(thought)
                
                # Check if we should continue
                if self._should_stop(state, action_result):
                    logger.info("Agent decided to stop")
                    break
                
                # Check for errors
                if action_result and "error" in action_result:
                    logger.warning(f"Error in iteration {iteration}: {action_result['error']}")
                    # Decide whether to continue or stop
                    if "critical" in action_result.get("error", "").lower():
                        break
            
            # Generate final report if we have enough information
            if state.sources and len(state.collected_info) > 0:
                # Policy check before writing report
                plan = {
                    "sources": state.sources,
                    "content_length": sum(len(str(info)) for info in state.collected_info)
                }
                
                is_compliant, violations = self.policy_checker.check_plan(plan)
                if not is_compliant:
                    logger.warning(f"Policy violations: {violations}")
                    # Could request human approval here or adjust plan
                
                # Request approval for report writing
                approval_context = {
                    "title": f"Research Report: {query}",
                    "sources": state.sources,
                    "num_sources": len(state.sources)
                }
                
                if self.human_approval.requires_approval("write_report", approval_context):
                    is_approved, approval_id = self.human_approval.request_approval(
                        "write_report",
                        approval_context
                    )
                    if not is_approved:
                        logger.warning("Report writing was not approved")
                        return {
                            "success": False,
                            "error": "Report writing was not approved",
                            "state": state.to_dict()
                        }
                
                # Write report
                report_result = self._write_final_report(state, query)
                
                if report_result.get("success"):
                    state.set_final_answer(f"Report written to {report_result.get('filepath')}")
                else:
                    logger.error(f"Failed to write report: {report_result.get('error')}")
            
            logger.info("Research completed")
            
            return {
                "success": True,
                "state": state.to_dict(),
                "final_answer": state.final_answer
            }
        
        except Exception as e:
            logger.error(f"Error during research: {e}")
            
            # Rollback on error
            if self.rollback_manager.enabled and checkpoint_id:
                logger.info("Attempting rollback...")
                rolled_back_state = self.rollback_manager.rollback(checkpoint_id)
                if rolled_back_state:
                    logger.info("Rollback successful")
            
            return {
                "success": False,
                "error": str(e),
                "state": state.to_dict() if state else None
            }
    
    def _pre_execution_wrapper(
        self,
        tool_name: str,
        tool: BaseTool,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Wrapper for pre-execution hook."""
        # Check human approval
        if self.human_approval.requires_approval(tool_name, parameters):
            is_approved, _ = self.human_approval.request_approval(tool_name, parameters)
            if not is_approved:
                return False, "Operation not approved"
        
        # Run pre-execution hook
        return self.pre_execution_hook.validate(tool_name, tool, parameters)
    
    def _post_execution_wrapper(self, tool_name: str, result) -> Any:
        """Wrapper for post-execution hook."""
        return self.post_execution_hook.process(tool_name, result)
    
    def _should_stop(self, state: AgentState, action_result: Optional[Dict[str, Any]]) -> bool:
        """Determine if agent should stop."""
        # Stop if we've reached max iterations
        if state.iteration >= config.max_iterations:
            return True
        
        # Stop if we wrote a report
        if action_result and isinstance(action_result, dict):
            if "filepath" in action_result:
                return True
        
        # Stop if we have enough information (heuristic)
        if len(state.sources) >= 5 and len(state.collected_info) >= 3:
            # Check if agent is trying to write report
            if state.thoughts and "write" in state.thoughts[-1].lower() and "report" in state.thoughts[-1].lower():
                return True
        
        return False
    
    def _write_final_report(self, state: AgentState, query: str) -> Dict[str, Any]:
        """Write final research report."""
        if "write_report" not in self.tools:
            return {"success": False, "error": "Report writer tool not available"}
        
        # Synthesize content from collected information
        content_parts = [
            f"# Research Report: {query}",
            "",
            "## Summary",
            ""
        ]
        
        # Add collected information
        for i, info in enumerate(state.collected_info, 1):
            if isinstance(info, dict):
                if "content" in info:
                    content_parts.append(f"### Source {i}")
                    content_parts.append(info["content"][:1000])  # Limit per source
                    content_parts.append("")
        
        content_parts.extend([
            "## Sources",
            ""
        ])
        
        for i, source in enumerate(state.sources, 1):
            content_parts.append(f"{i}. {source}")
        
        content = "\n".join(content_parts)
        
        # Write report
        report_tool = self.tools["write_report"]
        result = report_tool.execute(
            title=f"Research Report: {query}",
            content=content,
            sources=state.sources,
            format="markdown"
        )
        
        if result.success:
            # Policy check
            report_data = {
                "title": f"Research Report: {query}",
                "content": content,
                "sources": state.sources
            }
            is_compliant, violations = self.policy_checker.check_report(report_data)
            
            if not is_compliant:
                logger.warning(f"Report policy violations: {violations}")
                result.metadata["policy_violations"] = violations
        
        return result.data if result.success else {"success": False, "error": result.error}
    
    def rollback(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Rollback to a checkpoint."""
        state_dict = self.rollback_manager.rollback(checkpoint_id)
        if state_dict:
            return AgentState.from_dict(state_dict).to_dict()
        return None
