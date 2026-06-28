from __future__ import annotations

from datetime import datetime
from urllib.parse import urlparse

from agents.base import BaseAgent
from models.schemas import RankedSource, ResearchState, SearchResult


class SourceEvaluatorAgent(BaseAgent):
    name = "Source Evaluator"
    trusted_tlds = (".gov", ".edu", ".org")
    academic_domains = ("nature.com", "science.org", "springer.com", "sciencedirect.com", "arxiv.org", "pubmed.ncbi.nlm.nih.gov")
    government_domains = ("who.int", "oecd.org", "worldbank.org", "nih.gov", "nasa.gov")
    industry_domains = ("mckinsey.com", "gartner.com", "ibm.com", "microsoft.com", "googleblog.com", "openai.com")
    spam_terms = ("casino", "coupon", "betting", "adult", "clickbait", "free-money")

    def run(self, state: ResearchState) -> ResearchState:
        deduped: dict[str, SearchResult] = {}
        for source in state.search_results:
            domain = source.domain or urlparse(source.url).netloc.replace("www.", "")
            source.domain = domain
            if domain not in deduped or len(source.content) > len(deduped[domain].content):
                deduped[domain] = source

        ranked = [self.score_source(source) for source in deduped.values()]
        state.ranked_sources = sorted(
            [source for source in ranked if source.trust_score >= 45],
            key=lambda item: item.trust_score,
            reverse=True,
        )
        state.current_step = self.name
        self.event(state, f"Ranked {len(state.ranked_sources)} sources after duplicate website removal.")
        return state

    def score_source(self, source: SearchResult) -> RankedSource:
        domain = source.domain or urlparse(source.url).netloc.replace("www.", "")
        is_local_pack = source.author == "ResearchMind local analysis pack"
        domain_authority = 82.0 if is_local_pack else 70.0 if domain.endswith(self.trusted_tlds) else 50.0
        academic_score = 70.0 if is_local_pack else 95.0 if domain.endswith(".edu") or any(item in domain for item in self.academic_domains) else 25.0
        government_score = 55.0 if is_local_pack else 95.0 if domain.endswith(".gov") or any(item in domain for item in self.government_domains) else 20.0
        industry_score = 65.0 if is_local_pack else 85.0 if any(item in domain for item in self.industry_domains) else 35.0
        freshness_score = self._freshness(source.published_date)
        trust_score = domain_authority * 0.3 + freshness_score * 0.2 + academic_score * 0.2 + government_score * 0.15 + industry_score * 0.15
        reasons: list[str] = []
        if domain.endswith(self.trusted_tlds):
            reasons.append("trusted top-level domain")
        if any(item in domain for item in self.academic_domains):
            reasons.append("academic source signal")
        if any(item in domain for item in self.government_domains):
            reasons.append("government or public institution signal")
        if source.published_date:
            reasons.append("publication date available")
        if len(source.content) > 800:
            trust_score += 5
            reasons.append("substantial source content")
        if any(term in domain.lower() or term in source.title.lower() for term in self.spam_terms):
            trust_score -= 50
            reasons.append("spam-like signal detected")
        if is_local_pack:
            trust_score = max(trust_score, 76.0)
            reasons.append("offline local analysis pack")
        source_data = source.model_dump()
        source_data["domain"] = domain
        return RankedSource(
            **source_data,
            trust_score=max(0, min(100, trust_score)),
            domain_authority=domain_authority,
            freshness_score=freshness_score,
            academic_score=academic_score,
            government_score=government_score,
            industry_score=industry_score,
            evaluation_reason=", ".join(reasons) or "basic source metadata available",
        )

    def _freshness(self, published_date: str | None) -> float:
        if not published_date:
            return 45.0
        try:
            year = int(published_date[:4])
            age = max(0, datetime.utcnow().year - year)
            return max(20.0, 100.0 - age * 12)
        except ValueError:
            return 45.0
