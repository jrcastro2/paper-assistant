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
