"""
Assignment 11 — Monitoring & Alerts starter (TODO).

Tracks block rate, rate-limit hits, judge fail rate.
Fires alerts when thresholds are exceeded.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Alert:
    metric: str
    value: float
    threshold: float
    message: str


@dataclass
class MonitoringAlert:
    """Aggregate counters from pipeline plugins and emit alerts."""

    block_rate_threshold: float = 0.5
    rate_limit_hit_threshold: int = 5
    judge_fail_rate_threshold: float = 0.3
    alerts: list[Alert] = field(default_factory=list)

    # Counters — update these from your pipeline after each request
    total_requests: int = 0
    blocked_requests: int = 0
    rate_limit_hits: int = 0
    judge_checks: int = 0
    judge_fails: int = 0
    injection_blocks: int = 0
    topic_blocks: int = 0
    output_blocks: int = 0
    egress_blocks: int = 0
    errors: int = 0
    _alert_keys: set[str] = field(default_factory=set, repr=False)

    def check_metrics(self) -> list[Alert]:
        """TODO: compute rates, append Alert objects when thresholds exceeded."""
        snapshot = self.snapshot()
        self._maybe_alert(
            "block_rate",
            snapshot["block_rate"],
            self.block_rate_threshold,
            "High block rate may indicate attacks or false positives.",
        )
        self._maybe_alert(
            "rate_limit_hits",
            float(self.rate_limit_hits),
            float(self.rate_limit_hit_threshold),
            "Rate-limit hits are above the configured threshold.",
        )
        self._maybe_alert(
            "judge_fail_rate",
            snapshot["judge_fail_rate"],
            self.judge_fail_rate_threshold,
            "Safety judge fail rate is above the configured threshold.",
        )
        return self.alerts

    def export_json(self, filepath: str = "outputs/metrics.json"):
        """TODO: write metrics + alerts to JSON."""
        self.check_metrics()
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.snapshot(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def _maybe_alert(self, metric: str, value: float, threshold: float, message: str):
        if value <= threshold:
            return
        key = f"{metric}:warning"
        if key in self._alert_keys:
            return
        self._alert_keys.add(key)
        self.alerts.append(
            Alert(metric=metric, value=value, threshold=threshold, message=message)
        )

    def snapshot(self) -> dict:
        block_rate = (
            self.blocked_requests / self.total_requests
            if self.total_requests
            else 0.0
        )
        judge_fail_rate = (
            self.judge_fails / self.judge_checks if self.judge_checks else 0.0
        )
        return {
            "total_requests": self.total_requests,
            "blocked_requests": self.blocked_requests,
            "block_rate": block_rate,
            "rate_limit_hits": self.rate_limit_hits,
            "judge_checks": self.judge_checks,
            "judge_fails": self.judge_fails,
            "judge_fail_rate": judge_fail_rate,
            "injection_blocks": self.injection_blocks,
            "topic_blocks": self.topic_blocks,
            "output_blocks": self.output_blocks,
            "egress_blocks": self.egress_blocks,
            "errors": self.errors,
            "alerts": [
                {
                    "metric": a.metric,
                    "value": a.value,
                    "threshold": a.threshold,
                    "message": a.message,
                }
                for a in self.alerts
            ],
        }
