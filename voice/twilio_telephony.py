"""Twilio call creation and protected media helpers."""

from __future__ import annotations

import os
import secrets
import time
import uuid

import httpx
from twilio.request_validator import RequestValidator
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from memory import store
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


def validate_signature(url: str, params: dict, signature: str | None) -> bool:
    """Validate a Twilio callback, with an explicit local-test opt out."""
    setting = (_setting("TWILIO_VALIDATE_WEBHOOKS") or "true").lower()
    if setting in ("0", "false", "no", "off"):
        return True
    token = _setting("TWILIO_AUTH_TOKEN")
    if not token or not signature:
        return False
    return RequestValidator(token).validate(url, params, signature)


def canonical_webhook_url(path: str, query: str = "") -> str:
    url = "%s%s" % (public_base_url(), path)
    return "%s?%s" % (url, query) if query else url


def _persist(call_id: str, **kwargs) -> None:
    connection = store.connect()
    try:
        store.update_call_session(connection, call_id, **kwargs)
    finally:
        connection.close()


def update_status(call_id: str, status: str) -> None:
    call = local_soundbox.PENDING.get(call_id)
    if call is not None:
        call["twilio_status"] = status
    _persist(call_id, status=status)


def audio_url(call_id: str, turn: int, token: str) -> str:
    return "%s/twilio/audio?call_id=%s&turn=%d&token=%s" % (
        public_base_url(), call_id, turn, token)


def download_recording(recording_url: str) -> bytes:
    """Download a Twilio recording using credentials kept only in the environment."""
    if not recording_url:
        raise ValueError("Twilio did not provide a recording URL")
    url = recording_url
    if not url.endswith(".wav"):
        url += ".wav"
    with httpx.Client(timeout=45.0,
                      auth=(_setting("TWILIO_ACCOUNT_SID"),
                            _setting("TWILIO_AUTH_TOKEN"))) as client:
        response = client.get(url)
    if response.status_code >= 400:
        raise RuntimeError("Twilio recording download returned %d" % response.status_code)
    if not response.content:
        raise RuntimeError("Twilio recording was empty")
    return response.content


def dial(merchant_id: str, brief: Brief) -> Decision:
    """Create an outbound call and keep its context server-side."""
    if not configured():
        raise RuntimeError(
            "Twilio requires TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
            "TWILIO_PHONE_NUMBER, DEMO_PHONE_NUMBER and PUBLIC_BASE_URL")

    call_id = "call_%s" % uuid.uuid4().hex[:16]
    callback = "%s/twilio/voice?call_id=%s" % (public_base_url(), call_id)
    status_callback = "%s/twilio/status?call_id=%s" % (public_base_url(), call_id)
    call_parameters = {
        "to": _setting("DEMO_PHONE_NUMBER"),
        "from_": _setting("TWILIO_PHONE_NUMBER"),
        "url": callback,
    }
    # Trial accounts reject optional call parameters in some account regions. POST is
    # Twilio's default for url callbacks, so omitting method keeps the trial request small.
    if (_setting("TWILIO_STATUS_CALLBACK") or "false").lower() in ("1", "true", "yes", "on"):
        call_parameters["status_callback"] = status_callback
    try:
        twilio_call = Client(
            _setting("TWILIO_ACCOUNT_SID"), _setting("TWILIO_AUTH_TOKEN")
        ).calls.create(
            **call_parameters,
        )
    except TwilioRestException as exc:
        message = getattr(exc, "msg", None) or "Twilio rejected the call"
        code = getattr(exc, "code", None)
        suffix = " (code %s)" % code if code else ""
        raise RuntimeError("Twilio rejected the call%s: %s" % (suffix, message)) from exc
    except Exception as exc:
        raise RuntimeError("Twilio could not create the call: %s" % type(exc).__name__) from exc

    local_soundbox.PENDING[call_id] = {
        "call_id": call_id,
        "merchant_id": merchant_id,
        "brief": brief,
        "audio": None,
        "audio_by_turn": {},
        "audio_error": None,
        "audio_token": secrets.token_urlsafe(24),
        "reprompts": 0,
        "started_at": time.time(),
        "decision": None,
        "transcripts": [],
        "history": [],
        "phase": "approval",
        "twilio_call_sid": twilio_call.sid,
        "twilio_status": "initiated",
    }
    connection = store.connect()
    try:
        store.record_call_session(
            connection, call_id, merchant_id, "initiated", CHANNEL,
            candidate_id=brief.candidate_id, twilio_sid=twilio_call.sid,
            metadata={"phase": "approval", "audio_token": local_soundbox.PENDING[call_id]["audio_token"]},
        )
    finally:
        connection.close()
    return Decision(
        approved=False,
        outcome="no_answer",
        merchant_id=merchant_id,
        candidate_id=brief.candidate_id,
        call_id=call_id,
        channel=CHANNEL,
        modifications={"status": "initiated", "twilio_call_sid": twilio_call.sid},
    )
