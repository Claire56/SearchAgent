"""Example usage of the Research Agent."""

from tools import WebSearchTool, URLReaderTool, ReportWriterTool
from agent import ResearchAgent
from utils.config import config
from utils.logger import logger


def example_basic_research():
    """Example: Basic research query."""
    print("=" * 60)
    print("Example 1: Basic Research")
    print("=" * 60)
    
    # Initialize tools
    tools = [
        WebSearchTool(),
        URLReaderTool(),
        ReportWriterTool()
    ]
    
    # Initialize agent
    agent = ResearchAgent(tools=tools)
    
    # Execute research
    result = agent.research("What are the latest developments in AI safety?")
    
    if result.get("success"):
        print("\n✅ Research completed!")
        print(f"Final answer: {result.get('final_answer')}")
    else:
        print(f"\n❌ Research failed: {result.get('error')}")


def example_with_approval():
    """Example: Research with human approval required."""
    print("\n" + "=" * 60)
    print("Example 2: Research with Human Approval")
    print("=" * 60)
    
    tools = [
        WebSearchTool(),
        URLReaderTool(),
        ReportWriterTool()
    ]
    
    # Initialize agent with approval required
    agent = ResearchAgent(tools=tools, require_approval=True)
    
    result = agent.research("Research quantum computing breakthroughs")
    
    if result.get("success"):
        print("\n✅ Research completed!")
    else:
        print(f"\n❌ Research failed: {result.get('error')}")


def example_rollback():
    """Example: Demonstrating rollback capability."""
    print("\n" + "=" * 60)
    print("Example 3: Rollback Demonstration")
    print("=" * 60)
    
    tools = [
        WebSearchTool(),
        URLReaderTool(),
        ReportWriterTool()
    ]
    
    agent = ResearchAgent(tools=tools)
    
    # List available checkpoints
    checkpoints = agent.rollback_manager.list_checkpoints()
    
    if checkpoints:
        print(f"\nAvailable checkpoints: {len(checkpoints)}")
        latest = checkpoints[0]
        print(f"Latest checkpoint: {latest['checkpoint_id']}")
        
        # Rollback to latest checkpoint
        print("\nRolling back...")
        state = agent.rollback(latest['checkpoint_id'])
        
        if state:
            print(f"✅ Rolled back to iteration {state.get('iteration', 0)}")
        else:
            print("❌ Rollback failed")
    else:
        print("No checkpoints available. Run a research query first.")


if __name__ == "__main__":
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set OPENAI_API_KEY and SERPER_API_KEY in your .env file")
        exit(1)
    
    # Run examples
    print("\n🚀 Research Agent Examples\n")
    
    # Uncomment the example you want to run:
    # example_basic_research()
    # example_with_approval()
    # example_rollback()
    
    print("\n💡 To run examples, uncomment them in example.py")
