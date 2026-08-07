"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from guardrails.output_guardrails import content_filter


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into runtime callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, float] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """TODO: store input + start timestamp keyed by request_id/user_id."""
        request_id = request_id or uuid4().hex
        self._open[request_id] = time.perf_counter()
        self.logs.append(
            {
                "request_id": request_id,
                "event": "input",
                "timestamp": utc_now_iso(),
                "user_id": user_id,
                "text_hash": _sha256(text),
                "text_preview": _redacted_preview(text),
            }
        )
        return request_id

    def record_output(
        self,
        *,
        user_id: str,
        text: str,
        blocked: bool = False,
        layer: str | None = None,
        request_id: str | None = None,
    ):
        """TODO: store output, layer decision, latency; append to self.logs."""
        request_id = request_id or uuid4().hex
        started = self._open.pop(request_id, None)
        latency_ms = None
        if started is not None:
            latency_ms = round((time.perf_counter() - started) * 1000, 3)
        self.logs.append(
            {
                "request_id": request_id,
                "event": "output",
                "timestamp": utc_now_iso(),
                "user_id": user_id,
                "blocked": bool(blocked),
                "layer": layer,
                "latency_ms": latency_ms,
                "text_hash": _sha256(text),
                "text_preview": _redacted_preview(text),
            }
        )
        return request_id

    def export_json(self, filepath: str = "outputs/audit_log.json"):
        """Write logs to disk (JSON array)."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.logs, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _redacted_preview(text: str, limit: int = 160) -> str:
    filtered = content_filter(text or "")
    return filtered["redacted"][:limit]
