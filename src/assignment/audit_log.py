"""
Assignment 11 — Audit Log starter (TODO).

Records every interaction for forensics. Never blocks by itself —
other layers catch attacks; this layer makes them reviewable.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone


class AuditLogPlugin:
    """Framework-agnostic audit logger (wire into runtime callbacks or your pipeline)."""

    def __init__(self):
        self.name = "audit_log"
        self.logs: list[dict] = []
        self._open: dict[str, float] = {}

    def record_input(self, *, user_id: str, text: str, request_id: str | None = None):
        """TODO: store input + start timestamp keyed by request_id/user_id."""
        raise NotImplementedError("Implement AuditLogPlugin.record_input")

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
        raise NotImplementedError("Implement AuditLogPlugin.record_output")

    def export_json(self, filepath: str = "outputs/audit_log.json"):
        """Write logs to disk (JSON array)."""
        # TODO: ensure parent dirs exist, dump self.logs with indent=2
        raise NotImplementedError("Implement AuditLogPlugin.export_json")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
