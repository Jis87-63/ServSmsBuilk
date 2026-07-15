"""Estatísticas de importação e envio."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta


@dataclass
class SmsStats:
    total_imported: int = 0
    total_sent: int = 0
    success: int = 0
    failures: int = 0
    elapsed_seconds: float = 0.0

    @property
    def percent(self) -> float:
        return 0.0 if self.total_imported == 0 else (self.total_sent / self.total_imported) * 100

    def elapsed_text(self) -> str:
        return str(timedelta(seconds=int(self.elapsed_seconds)))
