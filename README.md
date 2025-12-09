# Research Agent - Autonomous AI Agent with Safety & Guardrails

A comprehensive AI agent system that demonstrates tool-calling, secure execution, and safety governance. This project teaches you how to build autonomous, safe, and reliable AI agents.

## Objectives

This project teaches you:

### 1. Tool-Calling Agents
- **ReAct Pattern**: Reasoning and Acting in language models
- **OpenAI Function Calling**: Structured tool invocation
- **LangChain Tools**: Tool abstraction and management
- **Agent Core Loop**: Thought → Action (Tool Call) → Observation

### 2. Secure Execution & Guardrails
- **Input Validation**: Validate agent tool inputs/outputs
- **Sandboxing**: Conceptual isolation of agent actions
- **Pre-execution Hooks**: Block harmful actions before execution
- **Post-execution Hooks**: Validate and sanitize outputs
- **Domain Whitelisting**: Control which domains can be accessed

### 3. Safety, Reliability, Governance
- **Human-in-the-Loop**: Approvals for critical steps
- **Rollback Strategies**: Save agent state, ability to revert
- **Policy Checks**: Review plans against policies (e.g., must cite sources)
- **State Management**: Track agent execution state

## 🏗️ Project Structure

```
ResearchAgent/
├── README.md                    # This comprehensive guide
├── requirements.txt             # Python dependencies
├── .env.example                # Environment variables template
│
├── agent/                      # Core agent implementation
│   ├── __init__.py
│   ├── research_agent.py      # Main Research Agent with ReAct pattern
│   ├── react_loop.py          # ReAct reasoning loop
│   └── state_manager.py       # Agent state management & rollback
│
├── tools/                      # Agent tools
│   ├── __init__.py
│   ├── web_search.py          # Serper API web search tool
│   ├── url_reader.py          # URL content extraction tool
│   ├── report_writer.py       # Report generation tool
│   └── base_tool.py          # Base tool interface
│
├── guardrails/                 # Security & safety guardrails
│   ├── __init__.py
│   ├── pre_execution.py       # Pre-execution validation hooks
│   ├── post_execution.py      # Post-execution validation hooks
│   ├── domain_validator.py    # Domain whitelisting
│   ├── input_validator.py     # Input validation
│   └── pii_redactor.py       # PII redaction from outputs
│
├── governance/                 # Safety & reliability features
│   ├── __init__.py
│   ├── human_approval.py      # Human-in-the-loop approvals
│   ├── policy_checker.py     # Policy compliance checking
│   └── rollback_manager.py    # State rollback capabilities
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   └── logger.py              # Logging utilities
│
├── data/                       # Data storage
│   ├── state/                 # Agent state snapshots
│   └── reports/               # Generated reports
│
└── main.py                     # Main entry point
```

## 🚀 Quick Start

### 1. Installation

```bash
cd SearchAgent
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file from `.env.example`:

```bash
# OpenAI (for agent LLM)
OPENAI_API_KEY=your_openai_key_here

# Serper API (for web search)
SERPER_API_KEY=your_serper_key_here

# Configuration
AGENT_MODEL=gpt-4
MAX_ITERATIONS=10
REQUIRE_HUMAN_APPROVAL=false
```

### 3. Run the Research Agent

```bash
# Basic research query
python main.py research "What are the latest developments in quantum computing?"

# With human approval required
python main.py research "Research AI safety" --require-approval

# With custom policy
python main.py research "AI trends" --policy-file policies/citation_policy.json
```

## 📚 Core Concepts

### ReAct Pattern

**ReAct (Reasoning + Acting)** is a pattern where the agent:
1. **Thinks** about what to do next
2. **Acts** by calling a tool
3. **Observes** the tool's result
4. **Repeats** until the task is complete

**Example:**
```
Thought: I need to research quantum computing. Let me start by searching for recent articles.
Action: search_web(query="quantum computing 2024")
Observation: Found 10 results including articles from Nature, arXiv...
Thought: Good, now I should read the most relevant articles to gather information.
Action: read_url(url="https://example.com/quantum-article")
Observation: Article content about quantum computing...
```

### Tool-Calling with OpenAI Function Calling

OpenAI's function calling allows structured tool invocation:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
]
```

### Guardrails

**Pre-execution hooks** validate actions before they execute:
- Check if domain is whitelisted
- Validate input parameters
- Block dangerous operations

**Post-execution hooks** sanitize outputs:
- Redact PII (emails, phone numbers, SSNs)
- Validate output format
- Check for policy violations

### Human-in-the-Loop

For critical operations, the agent pauses and requests human approval:
- Before accessing sensitive domains
- Before writing final reports
- When policy violations are detected

### Rollback

The agent saves state at key checkpoints:
- Before each tool call
- After each iteration
- Before critical operations

If something goes wrong, you can rollback to a previous state.

## 🔧 Key Components

### Research Agent (`agent/research_agent.py`)

Main agent that orchestrates the research process:
- Uses ReAct pattern for reasoning
- Manages tool calls
- Handles state transitions
- Integrates guardrails and governance

### Tools (`tools/`)

**Web Search Tool**: Uses Serper API to search the web
**URL Reader Tool**: Extracts and cleans content from URLs
**Report Writer Tool**: Generates structured research reports

### Guardrails (`guardrails/`)

**Pre-execution**: Validates tool calls before execution
**Post-execution**: Sanitizes outputs after execution
**Domain Validator**: Enforces domain whitelisting
**PII Redactor**: Removes personal information

### Governance (`governance/`)

**Human Approval**: Manages approval workflows
**Policy Checker**: Validates against policies
**Rollback Manager**: Handles state rollbacks

## Need to Learn while Building: Follow Below Steps

### 1: Tool-Calling Agents
1. Understand ReAct pattern
2. Implement basic agent loop
3. Add web search tool
4. Add URL reading tool
5. Add report writing tool

### 2: Secure Execution & Guardrails
1. Implement pre-execution hooks
2. Add domain whitelisting
3. Implement input validation
4. Add post-execution hooks
5. Implement PII redaction

### 3: Safety, Reliability, Governance
1. Add human-in-the-loop approvals
2. Implement state management
3. Add rollback capabilities
4. Implement policy checking
5. Test failure scenarios

## 📈 Example Workflow

### 1. User Query
```
"Research the latest developments in AI safety"
```

### 2. Agent Planning
```
Thought: I need to research AI safety. Let me search for recent articles and papers.
```

### 3. Pre-execution Check
```
✅ Domain whitelist check passed
✅ Input validation passed
```

### 4. Tool Execution
```
Action: search_web(query="AI safety 2024")
Observation: Found articles from arXiv, Nature, etc.
```

### 5. Post-execution Check
```
✅ Output validation passed
✅ No PII detected
```

### 6. Continue Loop
```
Thought: Good results. Let me read the most relevant articles.
Action: read_url(url="https://arxiv.org/...")
...
```

### 7. Policy Check
```
✅ All sources cited
✅ Report structure valid
```

### 8. Human Approval (if required)
```
⚠️  Human approval required for final report
[Waiting for approval...]
✅ Approved
```

### 9. Generate Report
```
Action: write_report(title="AI Safety Research", content=..., sources=[...])
```

### 10. Final Output
```
Report generated successfully!
Saved to: data/reports/research_20240101_120000.md
```

## 🚨 Safety Features

### Domain Whitelisting
Only approved domains can be accessed:
```python
ALLOWED_DOMAINS = [
    "arxiv.org",
    "nature.com",
    "github.com",
    # ... more domains
]
```

### PII Redaction
Automatically redacts:
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- Physical addresses

### Policy Enforcement
Example policy:
```json
{
    "must_cite_sources": true,
    "min_sources": 3,
    "max_urls_per_domain": 5,
    "require_peer_reviewed": false
}
```

## 📊 Monitoring & Debugging

### State Snapshots
Agent state is saved at checkpoints:
- `data/state/checkpoint_001.json`
- `data/state/checkpoint_002.json`
- ...

### Logging
All operations are logged:
- Tool calls
- Guardrail checks
- Policy violations
- Human approvals
- Rollbacks

## 🎯 Next Steps

1. **Experiment**: Try different research queries
2. **Customize**: Add your own tools
3. **Enhance**: Implement more sophisticated policies
4. **Scale**: Add multi-agent coordination
5. **Deploy**: Build API endpoint or web interface

---


