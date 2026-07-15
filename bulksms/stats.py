"""Estatísticas de importação, envio, latência e frequência."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta


@dataclass
class SmsStats:
    total_imported: int = 0
    total_sent: int = 0
    success: int = 0
    failures: int = 0
    elapsed_seconds: float = 0.0
    latencies: list[float] = field(default_factory=list)

    @property
    def percent(self) -> float:
        return 0.0 if self.total_imported == 0 else (self.total_sent / self.total_imported) * 100

    @property
    def messages_per_minute(self) -> float:
        return 0.0 if self.elapsed_seconds <= 0 else (self.total_sent / self.elapsed_seconds) * 60

    @property
    def average_latency(self) -> float:
        return 0.0 if not self.latencies else sum(self.latencies) / len(self.latencies)

    @property
    def min_latency(self) -> float:
        return 0.0 if not self.latencies else min(self.latencies)

    @property
    def max_latency(self) -> float:
        return 0.0 if not self.latencies else max(self.latencies)

    def elapsed_text(self) -> str:
        return str(timedelta(seconds=int(self.elapsed_seconds)))
