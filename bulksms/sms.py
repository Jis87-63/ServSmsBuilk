"""Envio de SMS usando Termux:API."""
from __future__ import annotations

import shutil
import subprocess


def check_termux_sms() -> bool:
    """Confere se o comando termux-sms-send está disponível."""
    return shutil.which("termux-sms-send") is not None


def send_sms(number: str, message: str) -> tuple[bool, str]:
    """Envia uma mensagem e retorna sucesso/erro sem interromper o lote."""
    if not check_termux_sms():
        return False, "termux-sms-send não encontrado. Instale Termux:API e conceda permissão de SMS."
    try:
        result = subprocess.run(
            ["termux-sms-send", "-n", number, message],
            text=True,
            capture_output=True,
            timeout=60,
            check=False,
        )
    except Exception as exc:  # Mantém o envio em lote resiliente.
        return False, str(exc)
    if result.returncode == 0:
        return True, ""
    return False, (result.stderr or result.stdout or "falha desconhecida").strip()
