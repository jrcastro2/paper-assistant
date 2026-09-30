from types import ModuleType
from typing import Callable

TOOLS = [
    {
        "name": "search_papers",
        "description": "Search for scientific papers by topic or keyword. Returns a list of matching papers with their IDs.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The search query, e.g. 'neutrino oscillations'"},
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
                "paper_id": {"type": "string", "description": "The paper ID"},
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
                "paper_id": {"type": "string", "description": "The paper ID"},
            },
            "required": ["paper_id"],
        },
    },
]


def make_tool_functions(module: ModuleType) -> dict[str, Callable]:
    """Build the tool dispatch table from a data module."""
    return {
        "search_papers": module.search_papers,
        "get_paper_details": module.get_paper_details,
        "get_citation_count": module.get_citation_count,
    }
