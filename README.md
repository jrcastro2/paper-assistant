# Paper Assistant

A hands-on learning project for LLM tool calling and agentic workflows, built with the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python).

Domain: a metadata assistant for scientific papers, inspired by platforms like INSPIRE-HEP and arXiv.

## What it demonstrates

- **Stage 1** — Basic Anthropic API call: request/response structure, message format, content blocks
- **Stage 2** — Tool calling: defining tools, detecting `tool_use` responses, executing functions locally, returning `tool_result` messages
- **Stage 3** — Agentic loop: the model chains multiple tool calls autonomously until it can answer *(coming soon)*

## Concepts covered

| Concept | Where |
|---|---|
| `messages` array and conversation history | `stage1_basic.py` |
| Tool definitions with JSON Schema | `stage2_tools.py` → `TOOLS` |
| `tool_use` / `tool_result` message flow | `stage2_tools.py` → `run_with_tools()` |
| Multi-step autonomous reasoning | `stage3_agent.py` *(coming soon)* |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your Anthropic API key:

```bash
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY
```

## Running the stages

```bash
python stage1_basic.py   # basic API call
python stage2_tools.py   # tool calling
python stage3_agent.py   # agentic loop (coming soon)
```

## Stack

- Python 3.11+
- [anthropic](https://pypi.org/project/anthropic/) — official Anthropic SDK
- [python-dotenv](https://pypi.org/project/python-dotenv/) — environment variable management
