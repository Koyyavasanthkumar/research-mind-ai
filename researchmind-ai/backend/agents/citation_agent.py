from __future__ import annotations

from datetime import datetime

from agents.base import BaseAgent
from models.schemas import Citation, CitationStyle, RankedSource, ResearchState


class CitationAgent(BaseAgent):
    name = "Citation"

    def run(self, state: ResearchState) -> ResearchState:
        citations: list[Citation] = []
        for style in (CitationStyle.APA, CitationStyle.IEEE, CitationStyle.MLA):
            for idx, source in enumerate(state.ranked_sources[:30], start=1):
                citations.append(Citation(style=style, source_url=source.url, text=self.format(source, style, idx)))
        state.citations = citations
        state.current_step = self.name
        self.event(state, f"Generated {len(citations)} citations across APA, IEEE, and MLA.")
        return state

    def format(self, source: RankedSource, style: CitationStyle, idx: int) -> str:
        accessed = datetime.utcnow().strftime("%B %d, %Y")
        year = self._year(source.published_date)
        author = source.author or source.domain
        if style == CitationStyle.IEEE:
            return f"[{idx}] {author}, \"{source.title},\" {source.domain}, {year}. [Online]. Available: {source.url}. Accessed: {accessed}."
        if style == CitationStyle.MLA:
            return f"{author}. \"{source.title}.\" {source.domain}, {year}, {source.url}. Accessed {accessed}."
        return f"{author}. ({year}). {source.title}. {source.domain}. Retrieved {accessed}, from {source.url}"

    def _year(self, published_date: str | None) -> str:
        if published_date and len(published_date) >= 4 and published_date[:4].isdigit():
            return published_date[:4]
        return "n.d."
