import httpx

INSPIRE_API = "https://inspirehep.net/api/literature"


def search_papers(query: str) -> list[dict]:
    response = httpx.get(
        INSPIRE_API,
        params={"q": query, "sort": "mostcited", "size": 5, "fields": "id,titles,authors,citation_count"},
        timeout=10,
    )
    response.raise_for_status()

    results = []
    for hit in response.json()["hits"]["hits"]:
        meta = hit["metadata"]
        results.append({
            "id": hit["id"],
            "title": meta["titles"][0]["title"] if meta.get("titles") else "Unknown",
            "citation_count": meta.get("citation_count", 0),
            "first_author": meta["authors"][0]["full_name"] if meta.get("authors") else "Unknown",
        })
    return results


def get_paper_details(paper_id: str) -> dict:
    response = httpx.get(f"{INSPIRE_API}/{paper_id}", timeout=10)

    if response.status_code == 404:
        return {"error": f"No paper found with id '{paper_id}'"}
    response.raise_for_status()

    meta = response.json()["metadata"]
    pub = meta.get("publication_info", [{}])[0]

    return {
        "id": paper_id,
        "title": meta["titles"][0]["title"] if meta.get("titles") else "Unknown",
        "authors": [a["full_name"] for a in meta.get("authors", [])[:5]],
        "year": pub.get("year"),
        "journal": pub.get("journal_title"),
        "doi": meta["dois"][0]["value"] if meta.get("dois") else None,
        "citation_count": meta.get("citation_count", 0),
        "abstract": meta.get("abstracts", [{}])[0].get("value", "No abstract available"),
    }


def get_citation_count(paper_id: str) -> dict:
    response = httpx.get(
        f"{INSPIRE_API}/{paper_id}",
        params={"fields": "citation_count"},
        timeout=10,
    )

    if response.status_code == 404:
        return {"error": f"No paper found with id '{paper_id}'"}
    response.raise_for_status()

    meta = response.json()["metadata"]
    return {"paper_id": paper_id, "citations": meta.get("citation_count", 0)}
