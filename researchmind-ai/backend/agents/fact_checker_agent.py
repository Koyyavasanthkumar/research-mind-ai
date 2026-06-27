from __future__ import annotations

from collections import defaultdict

from backend.agents.base import BaseAgent
from backend.models.schemas import ResearchState, VerifiedClaim, VerifiedInformation


class FactCheckerAgent(BaseAgent):
    name = "Fact Checker"

    def run(self, state: ResearchState) -> ResearchState:
        claim_sources: dict[str, set[str]] = defaultdict(set)
        claim_topics: dict[str, str] = {}
        for item in state.extracted_information:
            for claim in item.facts + item.statistics + item.important_statements + item.definitions:
                normalized = self._normalize(claim)
                claim_sources[normalized].add(item.source_url)
                claim_topics[normalized] = item.sub_topic

        verified: list[VerifiedClaim] = []
        unverified: list[VerifiedClaim] = []
        needs_more: list[VerifiedClaim] = []
        contradictions: list[str] = []
        unsupported: list[str] = []
        missing_evidence: list[str] = []

        for normalized, urls in claim_sources.items():
            claim = normalized.capitalize()
            if self._looks_contradictory(claim):
                contradictions.append(claim)
                needs_more.append(
                    VerifiedClaim(
                        claim=claim,
                        sub_topic=claim_topics.get(normalized, "Findings"),
                        source_urls=sorted(urls),
                        status="Needs More Research",
                        confidence=0.35,
                        evidence="Contradictory or disputed language detected.",
                    )
                )
            elif len(urls) >= 2:
                verified.append(
                    VerifiedClaim(
                        claim=claim,
                        sub_topic=claim_topics.get(normalized, "Findings"),
                        source_urls=sorted(urls),
                        status="Verified",
                        confidence=0.82,
                        evidence=f"Supported by {len(urls)} independent sources.",
                    )
                )
            elif self._has_strong_source(state, next(iter(urls))):
                verified.append(
                    VerifiedClaim(
                        claim=claim,
                        sub_topic=claim_topics.get(normalized, "Findings"),
                        source_urls=sorted(urls),
                        status="Verified",
                        confidence=0.72,
                        evidence="Supported by a high-trust source.",
                    )
                )
            else:
                unsupported.append(claim)
                unverified.append(
                    VerifiedClaim(
                        claim=claim,
                        sub_topic=claim_topics.get(normalized, "Findings"),
                        source_urls=sorted(urls),
                        status="Unverified",
                        confidence=0.45,
                        evidence="Only one moderate-trust source currently supports this claim.",
                    )
                )

        covered_topics = {claim.sub_topic for claim in verified + unverified + needs_more}
        for topic in state.sub_topics:
            if topic not in covered_topics:
                missing_evidence.append(f"No strong extracted evidence for subtopic: {topic}")

        state.verified_information = VerifiedInformation(
            verified=verified,
            unverified=unverified,
            needs_more_research=needs_more,
            contradictions=contradictions,
            unsupported_claims=unsupported[:20],
            missing_evidence=missing_evidence,
        )
        state.current_step = self.name
        self.event(state, f"Verified {len(verified)} claims, flagged {len(unverified)} unsupported claims, and found {len(contradictions)} contradictions.")
        return state

    def _normalize(self, claim: str) -> str:
        return " ".join(claim.strip().rstrip(".").lower().split())

    def _looks_contradictory(self, claim: str) -> bool:
        terms = ("contradicts", "disputed", "no evidence", "not proven", "debated", "conflicting")
        return any(term in claim.lower() for term in terms)

    def _has_strong_source(self, state: ResearchState, url: str) -> bool:
        for source in state.ranked_sources:
            if source.url == url:
                return source.trust_score >= 70
        return False
