#!/usr/bin/env python3
"""Minimal stdlib client for TypeSafe Jev ("System One") decisions.

Deliberately dependency-free so the skill's scripts stay zero-dependency and
offline-degradable. Enabled by the TYPESAFE_API_KEY environment variable;
override the endpoint with TYPESAFE_BASE_URL when needed.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

DEFAULT_URL = "https://api.typesafe.ai/v1/systemone"
DEFAULT_MODEL = "jev-latest"


class JevError(RuntimeError):
    """Any failure to obtain a Jev decision; callers should degrade gracefully."""


def api_key() -> str | None:
    return os.environ.get("TYPESAFE_API_KEY") or None


def has_api_key() -> bool:
    return api_key() is not None


def noul(instructions: str) -> dict:
    """Yes/no proposition; answer value is a 0-1 probability."""
    return {"type": "noul", "instructions": instructions}


def choice(instructions: str, criteria: dict[str, str]) -> dict:
    """Pick one option from a closed set defined by criteria."""
    return {"type": "choice", "instructions": instructions, "criteria": criteria}


def score(instructions: str, criteria: list[str]) -> dict:
    """Rate on an ordered scale defined by the criteria list."""
    return {"type": "score", "instructions": instructions, "criteria": criteria}


def system_one(state: str, questions: dict, model: str = DEFAULT_MODEL, timeout: int = 60) -> dict:
    """Evaluate all questions against one state in a single parallel call.

    Returns the parsed response dict (model / answers / usage). Raises
    JevError on any failure; Jev is an optional layer, so callers are
    expected to catch and degrade, never to gate core workflows on it.
    """
    key = api_key()
    if not key:
        raise JevError("TYPESAFE_API_KEY is not set")
    payload = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    request = urllib.request.Request(
        os.environ.get("TYPESAFE_BASE_URL", DEFAULT_URL),
        data=payload,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:500]
        raise JevError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise JevError(f"request failed: {exc}") from exc


def answer_value(answer: dict) -> tuple[object, float | None]:
    """Extract (value, confidence) from one answer object.

    Noul answers carry no separate confidence field, so the probability
    itself serves as the confidence. Unknown shapes return (None, None).
    """
    value = None
    for key in ("choice", "score", "noul"):
        if key in answer:
            value = answer[key]
            break
    confidence = answer.get("confidence")
    if confidence is None and isinstance(value, (int, float)):
        confidence = float(value)
    return value, confidence
