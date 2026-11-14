"""Twilio voice adapter for the merchant approval call."""

from __future__ import annotations

import os
import time
import uuid

from twilio.rest import Client
from voice.base import Brief, Decision
from voice import local_soundbox

CHANNEL = "sarvam_telephony"


def _setting(name: str) -> str:
    return (os.getenv(name) or "").strip()


def public_base_url() -> str:
    return _setting("PUBLIC_BASE_URL").rstrip("/")


def configured() -> bool:
    return all(_setting(name) for name in (
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "DEMO_PHONE_NUMBER",
        "PUBLIC_BASE_URL",
    ))


def dial(merchant_id: str, brief: Brief) -> Decision:
    """Create an outbound Twilio call and park its decision in the shared registry."""
    if not configured():
        raise RuntimeError(
            "Twilio requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
            "TWILIO_PHONE_NUMBER, DEMO_PHONE_NUMBER and PUBLIC_BASE_URL")

    call_id = "call_%s" % uuid.uuid4().hex[:10]
    callback = "%s/twilio/voice?call_id=%s" % (public_base_url(), call_id)
    status_callback = "%s/twilio/status?call_id=%s" % (public_base_url(), call_id)
    twilio_call = Client(_setting("TWILIO_ACCOUNT_SID"), _setting("TWILIO_AUTH_TOKEN")).calls.create(
        to=_setting("DEMO_PHONE_NUMBER"),
        from_=_setting("TWILIO_PHONE_NUMBER"),
        url=callback,
        method="POST",
        status_callback=status_callback,
        status_callback_method="POST",
        status_callback_event=["completed", "busy", "failed", "no-answer", "canceled"],
    )

    local_soundbox.PENDING[call_id] = {
        "call_id": call_id,
        "merchant_id": merchant_id,
        "brief": brief,
        "audio": None,
        "audio_error": None,
        "reprompts": 0,
        "started_at": time.time(),
        "decision": None,
        "transcripts": [],
        "twilio_call_sid": twilio_call.sid,
    }
    return Decision(
        approved=False,
        outcome="no_answer",
        merchant_id=merchant_id,
        candidate_id=brief.candidate_id,
        call_id=call_id,
        channel=CHANNEL,
        modifications={
            "status": "ringing",
            "twilio_call_sid": twilio_call.sid,
        },
    )
