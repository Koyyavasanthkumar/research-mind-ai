from __future__ import annotations

from backend.agents.base import BaseAgent
from backend.models.schemas import ResearchPlan, ResearchState, ResearchTask
from backend.utils.gemini import gemini_client


class PlannerAgent(BaseAgent):
    name = "Planner"

    def run(self, state: ResearchState) -> ResearchState:
        missing = [task.query for task in state.missing_topics]
        default_topics = [
            "History",
            "Working Principle",
            "Applications",
            "Advantages",
            "Disadvantages",
            "Future",
            "Latest Trends",
            "Ethics",
        ]
        fallback_queries = missing or [f"{state.user_query} {topic}" for topic in default_topics[: max(4, state.depth + 4)]]
        fallback = {
            "objective": f"Produce a verified research report about {state.user_query}.",
            "intent": "Informational research report with evidence-backed synthesis.",
            "strategy": "Search authoritative sources, compare claims, preserve uncertainty, and cite every important finding.",
            "tasks": [
                {
                    "title": query.replace(state.user_query, "").strip() or query,
                    "query": query,
                    "rationale": "Required for a complete research report.",
                    "priority": max(1, 10 - idx),
                }
                for idx, query in enumerate(fallback_queries)
            ],
        }
        data = gemini_client.generate_json(
            (
                "Understand the user intent, break the topic into multiple research tasks, generate subtopics, "
                "prioritize research order, and return JSON with objective, intent, strategy, and tasks. "
                f"User query: {state.user_query}. Missing gaps: {missing}. Depth: {state.depth}."
            ),
            fallback,
        )
        tasks = [ResearchTask(**task) for task in data.get("tasks", fallback["tasks"])]
        tasks.sort(key=lambda task: task.priority, reverse=True)
        state.research_plan = ResearchPlan(
            objective=data.get("objective", fallback["objective"]),
            intent=data.get("intent", fallback["intent"]),
            strategy=data.get("strategy", fallback["strategy"]),
            tasks=tasks,
        )
        state.sub_topics = [task.title for task in tasks]
        state.missing_topics = []
        state.loop_count += 1
        state.current_step = self.name
        self.event(state, f"Created {len(tasks)} prioritized research tasks.")
        return state
