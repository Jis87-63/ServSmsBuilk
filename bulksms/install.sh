#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

pkg update -y
pkg upgrade -y
pkg install -y python termux-api git
python -m pip install --upgrade pip
python -m pip install requests rich typer pandas openpyxl

echo "BulkSMS 1.0 instalado. Instale também o app Termux:API no Android e conceda permissão de SMS."
