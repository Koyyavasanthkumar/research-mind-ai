from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.base import BaseAgent
from models.schemas import ResearchState
from utils.search import tavily_search


class SearchAgent(BaseAgent):
    name = "Search"

    def run(self, state: ResearchState) -> ResearchState:
        if not state.research_plan:
            self.event(state, "No plan available for search.", "skipped")
            return state
        seen = {source.url for source in state.search_results}
        with ThreadPoolExecutor(max_workers=min(6, len(state.research_plan.tasks) or 1)) as executor:
            futures = {
                executor.submit(tavily_search.search, task.query, task.title): task
                for task in state.research_plan.tasks
            }
            for future in as_completed(futures):
                for source in future.result():
                    if source.url and source.url not in seen:
                        state.search_results.append(source)
                        seen.add(source.url)
        state.current_step = self.name
        self.event(state, f"Collected {len(state.search_results)} unique sources across {len(state.sub_topics)} subtopics.")
        return state
