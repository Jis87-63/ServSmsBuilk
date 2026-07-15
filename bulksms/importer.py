"""Importação e normalização de contatos para o BulkSMS 1.0."""
from __future__ import annotations

import random
import re
from pathlib import Path
from typing import Iterable

import csv
import importlib


SUPPORTED_EXTENSIONS = {".csv", ".txt", ".xlsx"}
MOZAMBIQUE_PREFIX = "+258"


def list_contact_files(contacts_dir: Path) -> list[Path]:
    """Retorna arquivos de contatos aceitos, ordenados por nome."""
    contacts_dir.mkdir(parents=True, exist_ok=True)
    return sorted(
        [p for p in contacts_dir.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS],
        key=lambda p: p.name.lower(),
    )


def normalize_phone(value: object, default_country_code: str = MOZAMBIQUE_PREFIX) -> str | None:
    """Normaliza números para E.164, priorizando Moçambique (+258)."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return None
    text = re.sub(r"[^0-9+]", "", text)
    if text.startswith("00"):
        text = "+" + text[2:]
    if text.startswith("+"):
        digits = "+" + re.sub(r"\D", "", text)
    else:
        digits_only = re.sub(r"\D", "", text)
        if digits_only.startswith(default_country_code.replace("+", "")):
            digits = "+" + digits_only
        else:
            digits = default_country_code + digits_only.lstrip("0")
    # Moçambique: +258 + 9 dígitos nacionais.
    if re.fullmatch(r"\+258\d{9}", digits):
        return digits
    return None


def _values_from_txt(path: Path) -> Iterable[object]:
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        yield line.strip()


def _values_from_table(path: Path) -> Iterable[object]:
    if path.suffix.lower() == ".csv":
        with path.open(encoding="utf-8", errors="ignore", newline="") as file:
            sample = file.read(2048)
            file.seek(0)
            dialect = csv.Sniffer().sniff(sample) if sample.strip() else csv.excel
            reader = csv.DictReader(file, dialect=dialect)
            columns = reader.fieldnames or []
            preferred = [c for c in columns if c.strip().lower() in {"telefone", "phone", "numero", "número", "contacto", "contato", "sms"}]
            for row in reader:
                for column in (preferred or columns):
                    value = row.get(column, "")
                    if normalize_phone(value):
                        yield value
                        break
        return

    openpyxl = importlib.import_module("openpyxl")
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    sheet = workbook.active
    rows = sheet.iter_rows(values_only=True)
    headers = [str(cell or "") for cell in next(rows, [])]
    preferred_indexes = [i for i, c in enumerate(headers) if c.strip().lower() in {"telefone", "phone", "numero", "número", "contacto", "contato", "sms"}]
    indexes = preferred_indexes or list(range(len(headers)))
    for row in rows:
        for index in indexes:
            value = row[index] if index < len(row) else ""
            if normalize_phone(value):
                yield value
                break


def import_contacts(path: Path, default_country_code: str = MOZAMBIQUE_PREFIX) -> list[str]:
    """Importa contatos, remove vazios/duplicados e mantém a ordem."""
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato não suportado: {suffix}")
    raw_values = _values_from_txt(path) if suffix == ".txt" else _values_from_table(path)
    contacts: list[str] = []
    seen: set[str] = set()
    for value in raw_values:
        phone = normalize_phone(value, default_country_code)
        if phone and phone not in seen:
            seen.add(phone)
            contacts.append(phone)
    return contacts


def generate_mozambique_contacts(quantity: int, prefixes: list[str] | None = None) -> list[str]:
    """Gera números moçambicanos aleatórios e únicos para testes autorizados."""
    if quantity < 1:
        raise ValueError("A quantidade deve ser maior que zero.")
    prefixes = prefixes or ["82", "83", "84", "85", "86", "87"]
    max_unique = len(prefixes) * 10_000_000
    if quantity > max_unique:
        raise ValueError(f"Quantidade muito alta. Máximo possível: {max_unique}.")

    contacts: set[str] = set()
    while len(contacts) < quantity:
        prefix = random.choice(prefixes)
        suffix = random.randint(0, 9_999_999)
        phone = normalize_phone(f"{prefix}{suffix:07d}")
        if phone:
            contacts.add(phone)
    return list(contacts)
