import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# Mock data — stands in for a real database or search index
# ---------------------------------------------------------------------------

PAPERS = {
    "p001": {
        "id": "p001",
        "title": "Evidence for Neutrino Oscillations from SNO",
        "authors": ["Q.R. Ahmad", "R.C. Allen", "T.C. Andersen"],
        "year": 2002,
        "abstract": "We report results from the Sudbury Neutrino Observatory showing clear evidence for neutrino flavor transformation.",
        "keywords": ["neutrino", "oscillations", "SNO", "solar neutrino"],
    },
    "p002": {
        "id": "p002",
        "title": "Observation of Neutrino Oscillations at Super-Kamiokande",
        "authors": ["Y. Fukuda", "T. Hayakawa", "E. Ichihara"],
        "year": 1998,
        "abstract": "We present evidence for muon neutrino oscillations using atmospheric neutrinos at Super-Kamiokande.",
        "keywords": ["neutrino", "oscillations", "Super-Kamiokande", "atmospheric"],
    },
    "p003": {
        "id": "p003",
        "title": "The Higgs Boson Discovery at the LHC",
        "authors": ["ATLAS Collaboration", "CMS Collaboration"],
        "year": 2012,
        "abstract": "We report the observation of a new boson consistent with the Standard Model Higgs boson.",
        "keywords": ["Higgs", "boson", "LHC", "Standard Model"],
    },
}

CITATIONS = {
    "p001": 4821,
    "p002": 9302,
    "p003": 12540,
}


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def search_papers(query: str) -> list[dict]:
    """Return papers whose keywords or title match the query."""
    query_lower = query.lower()
    results = []
    for paper in PAPERS.values():
        searchable = paper["title"].lower() + " " + " ".join(paper["keywords"])
        if any(word in searchable for word in query_lower.split()):
            results.append({"id": paper["id"], "title": paper["title"], "year": paper["year"]})
    return results


def get_paper_details(paper_id: str) -> dict:
    """Return full metadata for a paper by ID."""
    if paper_id not in PAPERS:
        return {"error": f"No paper found with id '{paper_id}'"}
    return PAPERS[paper_id]


def get_citation_count(paper_id: str) -> dict:
    """Return the citation count for a paper by ID."""
    if paper_id not in CITATIONS:
        return {"error": f"No citation data for id '{paper_id}'"}
    return {"paper_id": paper_id, "citations": CITATIONS[paper_id]}


# Map tool names to functions — used when dispatching tool calls
TOOL_FUNCTIONS = {
    "search_papers": search_papers,
    "get_paper_details": get_paper_details,
    "get_citation_count": get_citation_count,
}


# ---------------------------------------------------------------------------
# Tool definitions — this is what we send to the model
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "search_papers",
        "description": "Search for scientific papers by topic or keyword. Returns a list of matching papers with their IDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, e.g. 'neutrino oscillations' or 'Higgs boson'",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_paper_details",
        "description": "Get full metadata for a specific paper given its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The paper ID, e.g. 'p001'",
                },
            },
            "required": ["paper_id"],
        },
    },
    {
        "name": "get_citation_count",
        "description": "Get the number of times a paper has been cited, given its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "paper_id": {
                    "type": "string",
                    "description": "The paper ID, e.g. 'p001'",
                },
            },
            "required": ["paper_id"],
        },
    },
]


# ---------------------------------------------------------------------------
# Single-turn tool-calling flow
# ---------------------------------------------------------------------------

def run_with_tools(user_question: str) -> str:
    messages = [{"role": "user", "content": user_question}]

    # First call: send the question + tool definitions
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )

    print(f"[stop_reason: {response.stop_reason}]")

    # If the model didn't ask for a tool, return the text directly
    if response.stop_reason != "tool_use":
        return response.content[0].text

    # Find the tool_use block in the response
    tool_use_block = next(b for b in response.content if b.type == "tool_use")
    tool_name = tool_use_block.name
    tool_input = tool_use_block.input

    print(f"[tool call: {tool_name}({tool_input})]")

    # Execute the function locally
    result = TOOL_FUNCTIONS[tool_name](**tool_input)

    print(f"[tool result: {result}]")

    # Build the next messages list:
    # - append the assistant's response (which contains the tool_use block)
    # - append our tool_result
    messages.append({"role": "assistant", "content": response.content})
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_block.id,
                "content": json.dumps(result),
            }
        ],
    })

    # Second call: model reads the tool result and produces the final answer
    final_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )

    return final_response.content[0].text


if __name__ == "__main__":
    question = "How many times has the Super-Kamiokande neutrino paper been cited?"
    print(f"Question: {question}\n")
    answer = run_with_tools(question)
    print(f"\nAnswer: {answer}")
