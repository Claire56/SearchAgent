# Quick Start Guide

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   SERPER_API_KEY=your_serper_key_here
   ```

   Get your API keys:
   - OpenAI: https://platform.openai.com/api-keys
   - Serper: https://serper.dev/api-key

3. **Run your first research:**
   ```bash
   python main.py research "What are the latest developments in AI safety?"
   ```

## Key Features Demonstrated

### 1. Tool-Calling Agents (ReAct Pattern)
- The agent uses **ReAct** (Reasoning + Acting) pattern
- Core loop: **Thought → Action (Tool Call) → Observation**
- Tools: `search_web`, `read_url`, `write_report`

**Example:**
```python
from tools import WebSearchTool, URLReaderTool, ReportWriterTool
from agent import ResearchAgent

tools = [WebSearchTool(), URLReaderTool(), ReportWriterTool()]
agent = ResearchAgent(tools=tools)
result = agent.research("Your research query")
```

### 2. Secure Execution & Guardrails

**Pre-execution hooks:**
- Domain whitelisting (only approved domains can be accessed)
- Input validation (checks tool parameters)
- Custom validation hooks

**Post-execution hooks:**
- PII redaction (removes emails, phone numbers, SSNs, etc.)
- Output validation
- Custom processing hooks

**Example:**
```python
# Domain whitelist is automatically enforced
# Try accessing a non-whitelisted domain - it will be blocked

# PII is automatically redacted from outputs
# Email addresses, phone numbers, etc. are replaced with [REDACTED]
```

### 3. Safety, Reliability, Governance

**Human-in-the-loop:**
```bash
# Require approval for critical operations
python main.py research "Your query" --require-approval
```

**Policy checking:**
- Policies are defined in `policies/default_policy.json`
- Checks include: minimum sources, domain limits, citation requirements

**Rollback:**
```bash
# List checkpoints
python main.py list-checkpoints

# Rollback to a checkpoint
python main.py rollback --checkpoint-id checkpoint_20240101_120000_abc123
```

## Learning Path

### Week 1: Tool-Calling Agents
1. Study `agent/react_loop.py` - Understand the ReAct pattern
2. Study `tools/` - See how tools are implemented
3. Run a simple research query and observe the agent's reasoning

### Week 2: Guardrails
1. Study `guardrails/pre_execution.py` - Pre-execution validation
2. Study `guardrails/post_execution.py` - Post-execution processing
3. Study `guardrails/pii_redactor.py` - PII redaction
4. Try accessing a non-whitelisted domain to see it blocked

### Week 3: Governance
1. Study `governance/human_approval.py` - Human-in-the-loop
2. Study `governance/policy_checker.py` - Policy enforcement
3. Study `governance/rollback_manager.py` - State rollback
4. Simulate a failure and practice rollback

## Common Tasks

### Add a new tool:
1. Create a class inheriting from `BaseTool` in `tools/`
2. Implement `execute()` and `get_function_schema()`
3. Add it to the tools list when initializing the agent

### Customize guardrails:
1. Modify `guardrails/pre_execution.py` or `post_execution.py`
2. Add custom hooks using `register_hook()`
3. Update domain whitelist in `utils/config.py`

### Update policies:
1. Edit `policies/default_policy.json`
2. Or use `PolicyChecker.update_policy()` programmatically

## Troubleshooting

**Error: "OPENAI_API_KEY is required"**
- Make sure you've created a `.env` file with your API key

**Error: "Domain not in whitelist"**
- Add the domain to `config.allowed_domains` in `utils/config.py`
- Or disable domain whitelisting: `ENABLE_DOMAIN_WHITELIST=false` in `.env`

**Agent stops early:**
- Increase `MAX_ITERATIONS` in `.env`
- Check logs in `logs/agent.log`

## Next Steps

1. **Experiment** with different research queries
2. **Customize** tools and guardrails for your use case
3. **Extend** the agent with new capabilities
4. **Deploy** as an API or web service

For detailed documentation, see `README.md`.
