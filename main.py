"""Main entry point for the Research Agent."""

import argparse
import sys
from pathlib import Path
from tools import WebSearchTool, URLReaderTool, ReportWriterTool
from agent import ResearchAgent
from utils.config import config
from utils.logger import logger


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Research Agent - Autonomous AI Agent with Safety & Guardrails")
    
    parser.add_argument(
        "command",
        choices=["research", "rollback", "list-checkpoints"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Research query (required for 'research' command)"
    )
    
    parser.add_argument(
        "--require-approval",
        action="store_true",
        help="Require human approval for critical operations"
    )
    
    parser.add_argument(
        "--policy-file",
        type=str,
        help="Path to policy file (default: policies/default_policy.json)"
    )
    
    parser.add_argument(
        "--checkpoint-id",
        type=str,
        help="Checkpoint ID for rollback"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="Maximum number of iterations (overrides config)"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Override config if needed
    if args.max_iterations:
        config.max_iterations = args.max_iterations
    
    if args.require_approval:
        config.require_human_approval = True
    
    # Initialize tools
    tools = [
        WebSearchTool(),
        URLReaderTool(),
        ReportWriterTool()
    ]
    
    # Initialize agent
    agent = ResearchAgent(
        tools=tools,
        require_approval=args.require_approval if args.require_approval else None,
        policy_file=args.policy_file
    )
    
    # Execute command
    if args.command == "research":
        if not args.query:
            print("Error: Query is required for 'research' command", file=sys.stderr)
            sys.exit(1)
        
        print(f"\n🔍 Research Agent")
        print(f"Query: {args.query}")
        print(f"Max iterations: {config.max_iterations}")
        print(f"Human approval: {'Required' if config.require_human_approval else 'Not required'}")
        print("-" * 60)
        
        result = agent.research(args.query)
        
        if result.get("success"):
            print("\n✅ Research completed successfully!")
            if result.get("final_answer"):
                print(f"\n{result['final_answer']}")
            
            state = result.get("state", {})
            print(f"\n📊 Statistics:")
            print(f"  - Iterations: {state.get('iteration', 0)}")
            print(f"  - Sources collected: {len(state.get('sources', []))}")
            print(f"  - Information pieces: {len(state.get('collected_info', []))}")
        else:
            print(f"\n❌ Research failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    
    elif args.command == "rollback":
        if not args.checkpoint_id:
            print("Error: --checkpoint-id is required for 'rollback' command", file=sys.stderr)
            sys.exit(1)
        
        print(f"\n⏪ Rolling back to checkpoint: {args.checkpoint_id}")
        state = agent.rollback(args.checkpoint_id)
        
        if state:
            print("✅ Rollback successful!")
            print(f"State restored from iteration {state.get('iteration', 0)}")
        else:
            print("❌ Rollback failed")
            sys.exit(1)
    
    elif args.command == "list-checkpoints":
        checkpoints = agent.rollback_manager.list_checkpoints()
        
        if checkpoints:
            print("\n📋 Available checkpoints:")
            for cp in checkpoints:
                print(f"  - {cp['checkpoint_id']} ({cp['timestamp']})")
        else:
            print("No checkpoints available")


if __name__ == "__main__":
    main()
