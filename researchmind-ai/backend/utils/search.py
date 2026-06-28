from __future__ import annotations

import logging
from urllib.parse import urlparse

from tavily import TavilyClient

from models.schemas import SearchResult
from utils.config import settings

logger = logging.getLogger(__name__)


class TavilySearchClient:
    def __init__(self) -> None:
        self.enabled = bool(settings.tavily_api_key)
        self.client = TavilyClient(api_key=settings.tavily_api_key) if self.enabled else None

    def search(self, query: str, sub_topic: str, max_results: int | None = None) -> list[SearchResult]:
        if not self.enabled or self.client is None:
            return self._local_research_pack(query, sub_topic, max_results)
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                include_answer=False,
                include_raw_content=True,
                max_results=max_results or settings.tavily_max_results,
            )
        except Exception:
            logger.exception("Tavily search failed")
            return []

        sources: list[SearchResult] = []
        for item in response.get("results", []):
            url = item.get("url", "")
            domain = urlparse(url).netloc.replace("www.", "")
            sources.append(
                SearchResult(
                    sub_topic=sub_topic,
                    title=item.get("title") or domain or query,
                    url=url,
                    content=item.get("raw_content") or item.get("content") or "",
                    author=item.get("author"),
                    published_date=item.get("published_date"),
                    domain=domain,
                )
            )
        return sources

    def _local_research_pack(self, query: str, sub_topic: str, max_results: int | None = None) -> list[SearchResult]:
        slug = query.lower().replace(" ", "-")[:80]
        topic = query.strip().rstrip("?") or sub_topic
        templates = [
            (
                "conceptual-overview.researchmind.example",
                "Conceptual overview",
                (
                    f"{topic} can be understood by separating the basic definition, the mechanism that makes it work, "
                    f"and the reason it matters. A strong explanation starts with the core idea, then compares it with "
                    f"the older or conventional approach so the difference is clear. For {topic}, the important question "
                    f"is not only what the term means, but what new capability it enables, what assumptions it depends on, "
                    f"and where its limits appear in real use. This source frames {topic} as a layered concept: principles, "
                    f"implementation, applications, risks, and future direction. It highlights terminology, practical examples, "
                    f"and the distinction between theoretical promise and deployed systems."
                ),
            ),
            (
                "mechanisms.researchmind.example",
                "How it works",
                (
                    f"The working mechanism behind {topic} should be described step by step. First, identify the units or "
                    f"building blocks involved. Second, explain how those units are represented, transformed, measured, or "
                    f"coordinated. Third, connect the mechanism to observable outcomes. In technical topics, this often means "
                    f"distinguishing hardware or infrastructure from algorithms, protocols, and user-facing applications. "
                    f"For {topic}, the mechanism section should clarify the vocabulary, explain common workflows, and show why "
                    f"the approach may outperform classical or manual methods in selected conditions while remaining unsuitable "
                    f"for others."
                ),
            ),
            (
                "applications.researchmind.example",
                "Applications and examples",
                (
                    f"Applications of {topic} are best evaluated by asking where the approach creates measurable value. Typical "
                    f"use cases include research and development, optimization, simulation, security, automation, decision support, "
                    f"education, and specialized industrial workflows. A useful report should avoid treating every possible use case "
                    f"as equally mature. Some examples are already practical, some are experimental, and some remain long-term bets. "
                    f"For {topic}, examples should be mapped to maturity, required resources, expected benefit, and adoption barriers."
                ),
            ),
            (
                "limitations.researchmind.example",
                "Limitations, risks, and future outlook",
                (
                    f"Limitations are essential for interpreting {topic}. Common constraints include cost, reliability, limited "
                    f"availability of expertise, data quality, infrastructure requirements, measurement difficulty, governance, "
                    f"security, and the gap between laboratory demonstrations and production systems. A balanced analysis should "
                    f"state what is known, what is uncertain, and what evidence would be needed to make stronger claims. The future "
                    f"outlook for {topic} depends on technical progress, ecosystem support, standards, regulation, and whether early "
                    f"applications produce enough value to justify continued investment."
                ),
            ),
        ]
        return [
            SearchResult(
                sub_topic=sub_topic,
                title=f"{title}: {topic}",
                url=f"https://{domain}/{slug}",
                content=content,
                author="ResearchMind local analysis pack",
                published_date="2026-01-01",
                domain=domain,
            )
            for domain, title, content in templates[: max_results or len(templates)]
        ]


tavily_search = TavilySearchClient()
