# Paper Assistant

A command-line tool that uses an LLM to answer questions about scientific papers
by querying the [INSPIRE HEP](https://inspirehep.net) database. Built as a
hands-on exploration of LLM tool calling and agentic workflows using the
[Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python).

---

## What it demonstrates

**Tool calling** — the model is given a set of functions it can invoke. When it
needs data to answer a question, it emits a structured `tool_use` request instead
of guessing. The host code executes the function and returns the result.

**Agentic loop** — rather than one round-trip, the model runs in a loop: it can
call tools, receive results, reason about them, and call more tools — all
autonomously — until it has enough information to give a final answer.

**Swappable data sources** — the agent and tool definitions are decoupled from
the data layer. The same loop runs against either a local mock dataset or the
live INSPIRE API, selectable at runtime.

---

## How it works

Three tools are available to the model:

| Tool | What it does |
|---|---|
| `search_papers(query)` | Search INSPIRE by keyword, returns up to 5 results sorted by citation count |
| `get_paper_details(paper_id)` | Fetch full metadata for a paper: title, authors, year, journal, DOI, abstract |
| `get_citation_count(paper_id)` | Fetch the citation count for a paper |

The model decides which tools to call and in what order. For a question like
*"Find the most cited paper on dark matter detection"*, it will typically:

1. Call `search_papers("dark matter detection")` to get a list of candidates
2. Compare the `citation_count` values already in the results (or call
   `get_citation_count` for each)
3. Call `get_paper_details` on the winner
4. Return a structured answer

None of that sequence is scripted — the model drives it.

The loop in `agent.py` keeps sending tool results back to the model until it
returns `stop_reason == "end_turn"`, at which point the text response is printed.

---

## Project structure

```
paper-assistant/
├── main.py          ← entry point (--source mock|inspire, optional question)
├── agent.py         ← agentic loop
├── tools.py         ← tool definitions (JSON Schema) and dispatch table
├── data/
│   ├── mock.py      ← three-paper mock dataset, no external calls
│   └── inspire.py   ← live INSPIRE HEP API calls via httpx
├── .env.example     ← environment variable template
└── requirements.txt
```

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your [Anthropic API key](https://console.anthropic.com):

```bash
cp .env.example .env
# edit .env:
# ANTHROPIC_API_KEY=sk-ant-...
```

The key is read from the environment at runtime — it is never hardcoded.

---

## Usage

```bash
# Ask a question against the live INSPIRE API (default)
python main.py "Find the most cited paper on dark matter detection"

# Use the local mock dataset (no API calls, useful for testing)
python main.py --source mock "Find papers about neutrino oscillations"

# Default question (neutrino oscillations) against INSPIRE
python main.py
```

### Example output

```
Question: Find the most cited paper about neutrino oscillations and tell me its full details.
Source: inspire

--- step 1 ---
stop_reason: tool_use
tool call: search_papers({'query': 'neutrino oscillations'})
tool result: [{'id': '472711', 'title': 'Evidence for oscillation of atmospheric neutrinos', ...}, ...]

--- step 2 ---
stop_reason: tool_use
tool call: get_citation_count({'paper_id': '472711'})
tool result: {'paper_id': '472711', 'citations': 9284}
tool call: get_citation_count({'paper_id': '338011'})
tool result: {'paper_id': '338011', 'citations': 4821}

--- step 3 ---
stop_reason: tool_use
tool call: get_paper_details({'paper_id': '472711'})
tool result: {'title': 'Evidence for oscillation of atmospheric neutrinos', 'authors': ['Y. Fukuda', ...], ...}

--- step 4 ---
stop_reason: end_turn

Answer:
The most cited paper on neutrino oscillations is **"Evidence for oscillation of
atmospheric neutrinos"** (Super-Kamiokande, 1998) with 9,284 citations ...
```

---

## Notes

The main thing this project made concrete for me is the distinction between the
model *deciding* what to do and the host code *executing* it. The model never
runs Python — it produces structured requests, and the loop acts on them. Once
that separation clicks, the agent pattern is straightforward to extend: add a
tool definition, implement the function, and the model will use it when relevant.

The mock data source (`--source mock`) was useful during development to avoid API
latency and rate limits while getting the tool-calling flow right.

---

## Stack

- Python 3.11+
- [anthropic](https://pypi.org/project/anthropic/) — Anthropic Python SDK
- [httpx](https://pypi.org/project/httpx/) — HTTP client for INSPIRE API calls
- [python-dotenv](https://pypi.org/project/python-dotenv/) — loads `ANTHROPIC_API_KEY` from `.env`
