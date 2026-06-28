from __future__ import annotations

import json
import logging
from typing import Any

import google.generativeai as genai

from utils.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        self.enabled = bool(settings.gemini_api_key)
        if self.enabled:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
        else:
            self.model = None

    def generate_text(self, prompt: str, fallback: str = "") -> str:
        if not self.enabled or self.model is None:
            return fallback
        try:
            response = self.model.generate_content(prompt)
            return getattr(response, "text", "") or fallback
        except Exception:
            logger.exception("Gemini generation failed")
            return fallback

    def generate_json(self, prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        text = self.generate_text(
            f"{prompt}\nReturn only valid JSON. Do not wrap it in markdown.",
            fallback=json.dumps(fallback),
        )
        try:
            cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Gemini returned non-JSON; using fallback")
            return fallback


gemini_client = GeminiClient()
