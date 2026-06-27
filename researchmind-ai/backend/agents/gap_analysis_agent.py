from __future__ import annotations

from backend.agents.base import BaseAgent
from backend.models.schemas import ResearchState, ResearchTask


class GapAnalysisAgent(BaseAgent):
    name = "Gap Analysis"

    def run(self, state: ResearchState) -> ResearchState:
        gaps: list[ResearchTask] = []
        weak_topics = self._weak_topics(state)
        low_confidence = len(state.verified_information.unverified) + len(state.verified_information.needs_more_research)

        for idx, topic in enumerate(weak_topics[:4]):
            gaps.append(
                ResearchTask(
                    title=f"Evidence gap: {topic}",
                    query=f"{state.user_query} {topic} authoritative evidence",
                    rationale="Missing or weak evidence for a required report section.",
                    priority=10 - idx,
                )
            )

        if state.verified_information.contradictions:
            gaps.append(
                ResearchTask(
                    title="Contradiction resolution",
                    query=f"{state.user_query} contradiction evidence comparison",
                    rationale="Resolve contradictory findings before final synthesis.",
                    priority=9,
                )
            )

        if low_confidence > max(3, len(state.verified_information.verified)):
            gaps.append(
                ResearchTask(
                    title="Low confidence claims",
                    query=f"{state.user_query} peer reviewed evidence recent analysis",
                    rationale="Improve confidence for unsupported or low-evidence claims.",
                    priority=8,
                )
            )

        state.missing_topics = gaps if state.loop_count < state.max_loops else []
        state.current_step = self.name
        needs_research = bool(state.missing_topics)
        self.event(state, f"Gap analysis complete. needs_research={needs_research}; generated {len(state.missing_topics)} tasks.")
        return state

    def _weak_topics(self, state: ResearchState) -> list[str]:
        verified_topics = {claim.sub_topic for claim in state.verified_information.verified}
        return [topic for topic in state.sub_topics if topic not in verified_topics]
