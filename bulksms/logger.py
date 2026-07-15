"""Registro de eventos de envio em CSV."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

HEADERS = ["data", "hora", "numero", "status", "mensagem", "latencia_segundos", "erro"]


def create_log_file(logs_dir: Path) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    path = logs_dir / f"sms_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        csv.DictWriter(file, fieldnames=HEADERS).writeheader()
    return path


def write_log(path: Path, number: str, status: str, message: str, latency: float = 0.0, error: str = "") -> None:
    now = datetime.now()
    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=HEADERS)
        writer.writerow({
            "data": now.strftime("%Y-%m-%d"),
            "hora": now.strftime("%H:%M:%S"),
            "numero": number,
            "status": status,
            "mensagem": message,
            "latencia_segundos": f"{latency:.3f}",
            "erro": error,
        })


def list_logs(logs_dir: Path) -> list[Path]:
    logs_dir.mkdir(parents=True, exist_ok=True)
    return sorted([p for p in logs_dir.iterdir() if p.is_file()], key=lambda p: p.stat().st_mtime, reverse=True)
