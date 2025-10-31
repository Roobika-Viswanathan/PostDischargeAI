from typing import List
from duckduckgo_search import DDGS

from .config import settings
from .schemas import WebSearchResult


def web_search(query: str, max_results: int | None = None) -> List[WebSearchResult]:
    k = max_results or settings.web_search_results
    results: List[WebSearchResult] = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=k):
            results.append(
                WebSearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", ""),
                )
            )
    return results


