from __future__ import annotations

import threading
import time
from collections import defaultdict


class MetricsRegistry:
    def __init__(self) -> None:
        self.started_at = time.time()
        self._lock = threading.Lock()
        self.request_count = 0
        self.error_count = 0
        self.total_latency_ms = 0.0
        self.path_counts: dict[str, int] = defaultdict(int)
        self.status_counts: dict[str, int] = defaultdict(int)
        self.agent_runs: dict[str, int] = defaultdict(int)
        self.agent_failures: dict[str, int] = defaultdict(int)

    def record_request(self, path: str, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self.request_count += 1
            self.total_latency_ms += latency_ms
            self.path_counts[path] += 1
            self.status_counts[str(status_code)] += 1
            if status_code >= 500:
                self.error_count += 1

    def record_agent(self, agent_name: str, status: str) -> None:
        with self._lock:
            self.agent_runs[agent_name] += 1
            if status.lower() == "failed":
                self.agent_failures[agent_name] += 1

    def snapshot(self) -> dict:
        with self._lock:
            avg_latency = self.total_latency_ms / self.request_count if self.request_count else 0.0
            return {
                "uptime_seconds": round(time.time() - self.started_at, 2),
                "request_count": self.request_count,
                "error_count": self.error_count,
                "average_latency_ms": round(avg_latency, 2),
                "path_counts": dict(self.path_counts),
                "status_counts": dict(self.status_counts),
                "agent_runs": dict(self.agent_runs),
                "agent_failures": dict(self.agent_failures),
            }


metrics_registry = MetricsRegistry()
