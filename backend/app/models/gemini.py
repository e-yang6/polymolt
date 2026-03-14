"""Google Gemini provider — chat generation."""

from __future__ import annotations

import logging

from app.config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-1.5-flash"


def generate(
    user_prompt: str,
    *,
    system_prompt: str | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
) -> str:
    """Call Gemini with optional system_instruction and return the text response."""
    model = (model or DEFAULT_MODEL).strip()
    if not GOOGLE_API_KEY:
        return "Error: GOOGLE_API_KEY is not set."
    try:
        from google import genai
        genai.Client(api_key=GOOGLE_API_KEY)
        kwargs: dict = {}
        if system_prompt:
            kwargs["system_instruction"] = system_prompt
        gen = genai.GenerativeModel(model, **kwargs)
        resp = gen.generate_content(user_prompt)
        return (resp.text or "").strip()
    except Exception as e:
        logger.exception("Gemini generate failed")
        return f"Error: {e!s}"
