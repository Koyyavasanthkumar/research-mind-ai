from __future__ import annotations

import re

from backend.agents.base import BaseAgent
from backend.models.schemas import ExtractedInformation, ResearchState
from backend.utils.gemini import gemini_client


class ExtractorAgent(BaseAgent):
    name = "Information Extractor"

    def run(self, state: ResearchState) -> ResearchState:
        extracted: list[ExtractedInformation] = []
        for source in state.ranked_sources[:16]:
            fallback_claims = self._fallback_claims(source.content or source.title, state.user_query)
            fallback = {
                "facts": fallback_claims,
                "statistics": self._sentences_with_numbers(source.content),
                "important_statements": fallback_claims[:2],
                "definitions": [sentence for sentence in fallback_claims if " is " in sentence.lower()][:3],
                "examples": [sentence for sentence in fallback_claims if "example" in sentence.lower()][:3],
                "tables": [],
            }
            data = gemini_client.generate_json(
                (
                    f"Extract structured information about {state.user_query} from this source. "
                    "Return JSON keys: facts, statistics, important_statements, definitions, examples, tables. "
                    f"Source content: {source.content[:7000]}"
                ),
                fallback,
            )
            extracted.append(
                ExtractedInformation(
                    sub_topic=source.sub_topic,
                    source_url=source.url,
                    facts=[str(item) for item in data.get("facts", []) if str(item).strip()],
                    statistics=[str(item) for item in data.get("statistics", []) if str(item).strip()],
                    important_statements=[str(item) for item in data.get("important_statements", []) if str(item).strip()],
                    definitions=[str(item) for item in data.get("definitions", []) if str(item).strip()],
                    examples=[str(item) for item in data.get("examples", []) if str(item).strip()],
                    tables=[item for item in data.get("tables", []) if isinstance(item, dict)],
                )
            )
        state.extracted_information = extracted
        state.current_step = self.name
        self.event(state, f"Extracted facts, statistics, statements, definitions, examples, and tables from {len(extracted)} sources.")
        return state

    def _fallback_claims(self, content: str, topic: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", content.replace("\n", " "))
        keyword = self._topic_keyword(topic)
        useful = [sentence.strip() for sentence in sentences if len(sentence.strip()) > 45 and keyword in sentence.lower()]
        if useful:
            return useful[:8]
        substantial = [sentence.strip() for sentence in sentences if len(sentence.strip()) > 55]
        return substantial[:8] or [f"The source contains relevant context for {topic}."]

    def _topic_keyword(self, topic: str) -> str:
        stopwords = {"what", "is", "are", "the", "a", "an", "of", "for", "in", "on", "about", "how", "why"}
        for word in re.findall(r"[a-zA-Z0-9]+", topic.lower()):
            if word not in stopwords and len(word) > 2:
                return word
        return topic.lower().split()[0]

    def _sentences_with_numbers(self, content: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", content.replace("\n", " "))
        return [sentence.strip() for sentence in sentences if re.search(r"\d", sentence) and len(sentence.strip()) > 35][:5]
