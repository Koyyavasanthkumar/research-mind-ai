from __future__ import annotations

import re
from html import escape


CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SCRIPT_TAGS = re.compile(r"<\s*/?\s*script[^>]*>", re.IGNORECASE)


def sanitize_text(value: str) -> str:
    cleaned = CONTROL_CHARS.sub("", value).strip()
    cleaned = SCRIPT_TAGS.sub("", cleaned)
    return escape(cleaned, quote=False)
