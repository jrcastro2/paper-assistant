import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

# ---------------------------------------------------------------------------
# Mock data (same as stage 2)
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
    query_lower = query.lower()
    results = []
    for paper in PAPERS.values():
        searchable = paper["title"].lower() + " " + " ".join(paper["keywords"])
        if any(word in searchable for word in query_lower.split()):
            results.append({"id": paper["id"], "title": paper["title"], "year": paper["year"]})
    return results


def get_paper_details(paper_id: str) -> dict:
    if paper_id not in PAPERS:
        return {"error": f"No paper found with id '{paper_id}'"}
    return PAPERS[paper_id]


def get_citation_count(paper_id: str) -> dict:
    if paper_id not in CITATIONS:
        return {"error": f"No citation data for id '{paper_id}'"}
    return {"paper_id": paper_id, "citations": CITATIONS[paper_id]}


TOOL_FUNCTIONS = {
    "search_papers": search_papers,
    "get_paper_details": get_paper_details,
    "get_citation_count": get_citation_count,
}

TOOLS = [
    {
        "name": "search_papers",
        "description": "Search for scientific papers by topic or keyword. Returns a list of matching papers with their IDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query"},
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
                "paper_id": {"type": "string", "description": "The paper ID, e.g. 'p001'"},
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
                "paper_id": {"type": "string", "description": "The paper ID, e.g. 'p001'"},
            },
            "required": ["paper_id"],
        },
    },
]


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

def run_agent(user_question: str) -> str:
    messages = [{"role": "user", "content": user_question}]
    step = 0

    while True:
        step += 1
        print(f"\n--- step {step} ---")

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        print(f"stop_reason: {response.stop_reason}")

        # Model is done — return the final text answer
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if hasattr(b, "text"))

        # Model wants to call one or more tools
        # Append the assistant turn first (contains the tool_use blocks)
        messages.append({"role": "assistant", "content": response.content})

        # Process every tool_use block in this response
        # (the model can request multiple tools in a single turn)
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            print(f"tool call: {block.name}({block.input})")
            result = TOOL_FUNCTIONS[block.name](**block.input)
            print(f"tool result: {result}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result),
            })

        # Send all tool results back in a single user turn
        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    question = "Find the most cited paper about neutrino oscillations and tell me its full details."
    print(f"Question: {question}")
    answer = run_agent(question)
    print(f"\nAnswer:\n{answer}")
