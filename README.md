# Paper Assistant

A hands-on learning project for LLM tool calling and agentic workflows, built with the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python).

Domain: a metadata assistant for scientific papers, powered by the [INSPIRE HEP](https://inspirehep.net) database.

## What it demonstrates

- **Tool calling** — defining tools with JSON Schema, detecting `tool_use` responses, executing functions locally, returning `tool_result` messages
- **Agentic loop** — the model chains multiple tool calls autonomously until it can answer, deciding the sequence itself
- **Swappable data sources** — same agent, same tools, different backend (mock or real INSPIRE API)

## Project structure

```
paper-assistant/
├── main.py           ← single entry point (--source mock|inspire)
├── agent.py          ← agentic loop
├── tools.py          ← tool definitions (JSON Schema) + dispatch
└── data/
    ├── mock.py       ← mock data (no external API, good for testing)
    └── inspire.py    ← real INSPIRE HEP API calls
```

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

## Usage

```bash
# default: INSPIRE data, default question
python main.py

# use mock data (no API calls, instant)
python main.py --source mock

# ask your own question
python main.py "Who wrote the most cited paper on the Higgs boson?"
python main.py --source mock "Find papers about neutrino oscillations"
```

## How it works

The agent loop runs until the model returns `end_turn`:

1. Send the user question + tool definitions to Claude
2. If `stop_reason == "tool_use"`, execute the requested tool(s) locally
3. Send the results back as `tool_result` messages
4. Repeat until the model has enough to answer

The model decides which tools to call and in what order — the code just executes what it asks for.

## Stack

- Python 3.11+
- [anthropic](https://pypi.org/project/anthropic/) — official Anthropic SDK
- [httpx](https://pypi.org/project/httpx/) — HTTP client for INSPIRE API
- [python-dotenv](https://pypi.org/project/python-dotenv/) — environment variable management
