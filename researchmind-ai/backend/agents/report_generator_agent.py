from __future__ import annotations

from collections import defaultdict
from html import escape

from agents.base import BaseAgent
from models.schemas import Report, ResearchState
from utils.pdf import export_report_pdf


class ReportGeneratorAgent(BaseAgent):
    name = "Report Generator"

    def run(self, state: ResearchState) -> ResearchState:
        if not state.summaries:
            raise ValueError("Cannot generate a report without summaries.")

        sections = self._sections(state)
        markdown = self._markdown(state, sections)
        html = self._html(state, sections)
        report = Report(
            research_id=state.research_id,
            title=f"Research Report: {state.user_query}",
            table_of_contents=list(sections.keys()) + ["Conclusion", "References"],
            sections=sections,
            conclusion=self._conclusion(state),
            references=state.citations,
            source_cards=state.ranked_sources[:30],
            markdown=markdown,
            html=html,
        )
        report.pdf_path = export_report_pdf(report)
        state.report = report
        state.current_step = self.name
        self.event(state, f"Generated markdown, HTML, table of contents, numbered sections, citations, and PDF at {report.pdf_path}.")
        return state

    def _sections(self, state: ResearchState) -> dict[str, str]:
        grouped: dict[str, list[str]] = defaultdict(list)
        for claim in state.verified_information.verified:
            grouped[claim.sub_topic].append(f"{claim.claim} [{self._citation_number(state, claim.source_urls)}]")
        sections = {
            "1. Executive Summary": state.summaries.executive_summary,
            "2. Detailed Summary": state.summaries.detailed_summary,
            "3. Bullet Summary": "\n".join(f"- {item}" for item in state.summaries.bullet_summary),
            "4. Key Takeaways": "\n".join(f"- {item}" for item in state.summaries.key_takeaways),
        }
        index = 5
        for topic, claims in grouped.items():
            sections[f"{index}. {topic}"] = "\n".join(f"- {claim}" for claim in claims[:12])
            index += 1
        if state.verified_information.unverified:
            sections[f"{index}. Unverified Claims"] = "\n".join(f"- {claim.claim}" for claim in state.verified_information.unverified[:10])
            index += 1
        if state.verified_information.contradictions:
            sections[f"{index}. Contradictions"] = "\n".join(f"- {item}" for item in state.verified_information.contradictions[:10])
        return sections

    def _markdown(self, state: ResearchState, sections: dict[str, str]) -> str:
        lines = [f"# Research Report: {state.user_query}", "", "## Table of Contents"]
        lines.extend(f"- {title}" for title in sections)
        lines.extend(["- Conclusion", "- References", ""])
        for title, body in sections.items():
            lines.extend([f"## {title}", body, ""])
        lines.extend(["## Conclusion", self._conclusion(state), ""])
        lines.append("## References")
        lines.extend(citation.text for citation in state.citations)
        return "\n".join(lines)

    def _html(self, state: ResearchState, sections: dict[str, str]) -> str:
        toc = "".join(f"<li>{escape(title)}</li>" for title in sections)
        body = "".join(f"<section><h2>{escape(title)}</h2><p>{escape(text).replace(chr(10), '<br>')}</p></section>" for title, text in sections.items())
        refs = "".join(f"<li>{escape(citation.text)}</li>" for citation in state.citations)
        return (
            "<!doctype html><html><head><meta charset=\"utf-8\"><title>"
            f"{escape(state.user_query)}</title></head><body><h1>Research Report: {escape(state.user_query)}</h1>"
            f"<h2>Table of Contents</h2><ol>{toc}</ol>{body}"
            f"<h2>Conclusion</h2><p>{escape(self._conclusion(state))}</p>"
            f"<h2>References</h2><ol>{refs}</ol></body></html>"
        )

    def _citation_number(self, state: ResearchState, urls: list[str]) -> int:
        for idx, citation in enumerate(state.citations, start=1):
            if citation.source_url in urls:
                return idx
        return 0

    def _conclusion(self, state: ResearchState) -> str:
        return (
            f"In conclusion, {state.user_query} is not just a definition question; it needs a layered explanation of "
            "principles, mechanisms, applications, limitations, and evidence quality. The current report provides a "
            "structured offline analysis, but production-grade conclusions should be strengthened with live source "
            "collection, current citations, and domain-specific examples."
        )
