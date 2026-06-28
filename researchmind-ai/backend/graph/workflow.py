from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Callable

from langgraph.graph import END, StateGraph

from agents.citation_agent import CitationAgent
from agents.extractor_agent import ExtractorAgent
from agents.fact_checker_agent import FactCheckerAgent
from agents.gap_analysis_agent import GapAnalysisAgent
from agents.planner_agent import PlannerAgent
from agents.report_generator_agent import ReportGeneratorAgent
from agents.search_agent import SearchAgent
from agents.source_evaluator_agent import SourceEvaluatorAgent
from agents.summarizer_agent import SummarizerAgent
from memory.vector_store import research_memory
from models.schemas import AgentLog, ExecutionHistoryItem, ResearchState
from utils.metrics import metrics_registry

logger = logging.getLogger(__name__)


class ResearchWorkflow:
    max_retries = 3

    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.search = SearchAgent()
        self.evaluator = SourceEvaluatorAgent()
        self.extractor = ExtractorAgent()
        self.fact_checker = FactCheckerAgent()
        self.gap_analysis = GapAnalysisAgent()
        self.summarizer = SummarizerAgent()
        self.citation = CitationAgent()
        self.report_generator = ReportGeneratorAgent()
        self.graph = self._build_graph()

    def _node(self, step: str, agent_name: str, agent_method: Callable[[ResearchState], ResearchState], store_memory: bool = False):
        def wrapped(raw_state: dict[str, Any]) -> dict[str, Any]:
            state = ResearchState.model_validate(raw_state)
            if state.error:
                state.logs.append(AgentLog(agent=agent_name, status="skipped", message=f"Skipped {step} because workflow is already failed."))
                return state.as_graph_dict()

            history = ExecutionHistoryItem(step=step, agent=agent_name, started_at=datetime.utcnow())
            state.history.append(history)
            last_error: Exception | None = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    state.logs.append(AgentLog(agent=agent_name, status="running", message=f"Starting {step}.", attempt=attempt))
                    updated = agent_method(state)
                    if store_memory:
                        research_memory.store_information(updated.research_id, updated.extracted_information)
                    history.completed_at = datetime.utcnow()
                    history.status = "completed"
                    history.attempts = attempt
                    updated.current_step = step
                    updated.logs.append(AgentLog(agent=agent_name, status="completed", message=f"Completed {step}.", attempt=attempt))
                    metrics_registry.record_agent(agent_name, "completed")
                    return updated.as_graph_dict()
                except Exception as exc:
                    last_error = exc
                    logger.exception("%s failed on attempt %s", agent_name, attempt)
                    state.logs.append(AgentLog(agent=agent_name, status="retrying", message=str(exc), attempt=attempt))

            message = str(last_error) if last_error else f"{agent_name} failed"
            history.completed_at = datetime.utcnow()
            history.status = "failed"
            history.attempts = self.max_retries
            history.error = message
            state.error = message
            state.logs.append(AgentLog(agent=agent_name, status="failed", message=message, attempt=self.max_retries))
            metrics_registry.record_agent(agent_name, "failed")
            return state.as_graph_dict()

        return wrapped

    def _build_graph(self):
        graph = StateGraph(dict)
        graph.add_node("planner", self._node("Planner", self.planner.name, self.planner.run))
        graph.add_node("search", self._node("Search", self.search.name, self.search.run))
        graph.add_node("evaluate_sources", self._node("Source Evaluation", self.evaluator.name, self.evaluator.run))
        graph.add_node("extract", self._node("Extraction", self.extractor.name, self.extractor.run, store_memory=True))
        graph.add_node("fact_check", self._node("Verification", self.fact_checker.name, self.fact_checker.run))
        graph.add_node("gap_analysis", self._node("Gap Analysis", self.gap_analysis.name, self.gap_analysis.run))
        graph.add_node("summarize", self._node("Summary", self.summarizer.name, self.summarizer.run))
        graph.add_node("cite", self._node("Citation", self.citation.name, self.citation.run))
        graph.add_node("report", self._node("Report", self.report_generator.name, self.report_generator.run))

        graph.set_entry_point("planner")
        graph.add_edge("planner", "search")
        graph.add_edge("search", "evaluate_sources")
        graph.add_edge("evaluate_sources", "extract")
        graph.add_edge("extract", "fact_check")
        graph.add_edge("fact_check", "gap_analysis")
        graph.add_conditional_edges(
            "gap_analysis",
            self._route_after_gap,
            {"research_more": "planner", "finish": "summarize"},
        )
        graph.add_edge("summarize", "cite")
        graph.add_edge("cite", "report")
        graph.add_edge("report", END)
        return graph.compile()

    def _route_after_gap(self, raw_state: dict[str, Any]) -> str:
        state = ResearchState.model_validate(raw_state)
        if state.error:
            return "finish"
        return "research_more" if state.missing_topics and state.loop_count < state.max_loops else "finish"

    def run(self, state: ResearchState) -> ResearchState:
        result = self.graph.invoke(state.as_graph_dict(), {"recursion_limit": 40})
        return ResearchState.model_validate(result)


research_workflow = ResearchWorkflow()
