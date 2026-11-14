"""Sarvam-powered conversation turns for Twilio voice calls."""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel

from core import llm
from voice.base import Brief


class VoiceReply(BaseModel):
    text: str
    language_code: Literal["hi-IN", "mr-IN", "en-IN"] = "hi-IN"
    end_call: bool = False


def respond(transcript: str, brief: Brief | None, history: list[dict]) -> VoiceReply:
    """Generate one short spoken response without allowing the model to invent figures."""
    context = {
        "merchant": brief.merchant_name if brief else "the merchant",
        "proposal": brief.title if brief else "general business assistance",
        "language": brief.language if brief else "hi-IN",
        "history": history[-6:],
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are Vyapaar Mitra, a concise voice assistant for an Indian merchant. "
                "Reply in the caller's language, choosing Hindi hi-IN, Marathi mr-IN, or "
                "Indian English en-IN. Keep replies under 25 words and natural for a phone "
                "call. Never invent or calculate rupee amounts, percentages, counts, dates, "
                "or customer details. Use only figures already spoken in the proposal. "
                "If the caller clearly says goodbye, set end_call true. Return JSON only with "
                "text, language_code, and end_call."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {"context": context, "caller_said": transcript},
                ensure_ascii=False,
            ),
        },
    ]
    result, _meta = llm.complete(
        messages,
        VoiceReply,
        label="twilio_voice_turn",
        max_tokens=300,
        reasoning_effort=None,
    )
    return result
