"""
Assignment 11 — Defense-in-depth pipeline assembly (TODO).

Wire rate limiter + lab guardrails + judge + audit + monitoring.
You may use OpenAI Responses API plugins, LangGraph, NeMo, or pure Python.
"""
from __future__ import annotations

import re
import json
from urllib.parse import urlparse

from assignment.rate_limiter import RateLimitPlugin
from assignment.audit_log import AuditLogPlugin
from assignment.monitoring import MonitoringAlert


def is_egress_allowed(destination: str, payload: dict | list | str) -> bool:
    """TODO 8A: Enforce a destination allowlist before any data leaves the agent.

    Return ``True`` only for an approved VinBank HTTPS endpoint and ordinary
    banking payload. Return ``False`` for unknown domains and payloads that
    contain a password, API key, database host, phone number or email address.
    Do not let the LLM's prose decide this policy.
    """
    parsed = urlparse(destination or "")
    allowed_paths = {"/v1/transfers", "/v1/cases", "/v1/profile"}
    if parsed.scheme != "https":
        return False
    if parsed.hostname != "api.vinbank.example":
        return False
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        return False
    if parsed.path not in allowed_paths:
        return False

    sensitive_patterns = (
        r"\badmin123\b",
        r"\bsk-[a-zA-Z0-9-]{8,}\b",
        r"\b[a-z0-9.-]+\.internal(?::\d+)?\b",
        r"\bpassword\s*(?:is|[:=])\s*['\"]?[^'\"\s,.]+",
        r"\b0\d{9,10}\b",
        r"\b[\w.-]+@[\w.-]+\.[a-zA-Z]{2,}\b",
    )
    if isinstance(payload, (dict, list)):
        payload_text = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    else:
        payload_text = str(payload or "")
    return not any(
        re.search(pattern, payload_text, re.IGNORECASE)
        for pattern in sensitive_patterns
    )


def build_production_plugins(
    *,
    max_requests: int = 10,
    window_seconds: int = 60,
    use_llm_judge: bool = True,
) -> list:
    """
    TODO 8: Return an ordered list of plugins / layers:

    1. RateLimitPlugin
    2. InputGuardrailPlugin  (from guardrails.input_guardrails)
    3. OutputGuardrailPlugin / LlmJudge  (from guardrails.output_guardrails)
    4. (optional) NeMo wrapper

    Audit/monitoring can be plugins or side observers — document your choice.
    The action gateway calls ``is_egress_allowed`` separately before any sink.
    """
    from guardrails.input_guardrails import InputGuardrailPlugin
    from guardrails.output_guardrails import OutputGuardrailPlugin

    return [
        RateLimitPlugin(max_requests=max_requests, window_seconds=window_seconds),
        InputGuardrailPlugin(),
        OutputGuardrailPlugin(use_llm_judge=use_llm_judge),
    ]


def build_observability():
    """TODO: return (AuditLogPlugin(), MonitoringAlert())."""
    return AuditLogPlugin(), MonitoringAlert()


async def run_assignment_suite(pipeline, student_id: str) -> dict:
    """
    TODO: Run Tests 1–4 from assignment11.md and
    return a dict matching schemas/results.schema.json.

    Write:
      outputs/results.json
      outputs/audit_log.json
      outputs/metrics.json
    """
    raise NotImplementedError("Implement run_assignment_suite")
