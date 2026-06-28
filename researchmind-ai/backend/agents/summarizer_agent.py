from __future__ import annotations

from agents.base import BaseAgent
from models.schemas import ResearchState, SummaryBundle
from utils.gemini import gemini_client


class SummarizerAgent(BaseAgent):
    name = "Summarizer"

    def run(self, state: ResearchState) -> ResearchState:
        claims = state.verified_information.verified or state.verified_information.unverified
        claim_text = "\n".join(f"- {claim.claim}" for claim in claims[:40])
        fallback = self._fallback_summary(state, claims)
        data = gemini_client.generate_json(
            (
                "Generate executive_summary, detailed_summary, bullet_summary, and key_takeaways "
                f"for this verified research topic: {state.user_query}\nClaims:\n{claim_text}"
            ),
            fallback,
        )
        state.summaries = SummaryBundle(**data)
        state.current_step = self.name
        self.event(state, "Generated executive summary, detailed summary, bullet summary, and key takeaways.")
        return state

    def _fallback_summary(self, state: ResearchState, claims) -> dict:
        topic = state.user_query.strip().rstrip("?")
        ranked_count = len(state.ranked_sources)
        claim_items = [claim.claim for claim in claims if claim.claim.strip()]
        evidence_note = (
            f"This report used {ranked_count} ranked local/offline sources because live Tavily or Gemini keys are not configured."
            if ranked_count
            else "Live source collection was unavailable, so the report uses local analytical fallback material."
        )
        detailed_parts = [
            f"{topic} is best understood as a concept with four layers: what it means, how it works, where it is useful, and what limits its adoption. {evidence_note}",
            f"At the definition level, {topic} needs a clear distinction between the core principle and surrounding hype. The useful question is not just the dictionary meaning, but what capability becomes possible, what resources are required, and what evidence shows the idea working.",
            f"At the mechanism level, the topic should be explained through its building blocks, the process that connects those blocks, and the output produced by that process. A strong technical explanation should connect vocabulary to practical workflow rather than only listing terms.",
            f"At the application level, {topic} should be judged by maturity. Some uses may already be practical, some may be experimental, and some may depend on future improvements in cost, reliability, tooling, or standards.",
            f"At the limitation level, the important risks are overclaiming, weak evidence, implementation cost, specialist skill requirements, governance, and the gap between demonstrations and dependable production use.",
        ]
        if claim_items:
            detailed_parts.append("Key extracted findings include: " + " ".join(claim_items[:10]))
        bullets = claim_items[:8] or [
            f"Define {topic} in plain language before discussing technical details.",
            f"Explain the mechanism behind {topic}, including inputs, process, outputs, and constraints.",
            f"Separate mature applications of {topic} from experimental or speculative claims.",
            f"Evaluate benefits against cost, reliability, expertise, governance, and adoption barriers.",
            f"Use stronger external sources for final production-grade citations when API keys are configured.",
        ]
        takeaways = claim_items[:5] or [
            f"{topic} should be explained through definition, mechanism, applications, limitations, and outlook.",
            "A useful report must separate verified capability from future promise.",
            "Depth improves when sources include examples, constraints, and implementation context.",
            "Offline mode can provide structured analysis, but live search should be enabled for real citations.",
            "The strongest conclusion is one that documents uncertainty instead of hiding it.",
        ]
        return {
            "executive_summary": (
                f"{topic} was analyzed as a multi-layer research topic covering definition, operating mechanism, "
                f"applications, limitations, and future outlook. The evidence indicates that a good understanding of "
                f"{topic} requires both conceptual clarity and careful separation of practical use cases from claims "
                f"that still need stronger validation."
            ),
            "detailed_summary": "\n\n".join(detailed_parts),
            "bullet_summary": bullets,
            "key_takeaways": takeaways,
        }
