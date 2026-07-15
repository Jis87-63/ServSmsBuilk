"""Interface principal do BulkSMS 1.0."""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from importer import generate_mozambique_contacts, import_contacts, list_contact_files
from logger import create_log_file, list_logs, write_log
from sms import send_sms
from stats import SmsStats

ROOT = Path(__file__).resolve().parent
console = Console()


def load_config() -> dict:
    with (ROOT / "config.json").open(encoding="utf-8") as file:
        return json.load(file)


config = load_config()
contacts: list[str] = []
message_text = ""
stats = SmsStats()


def path_from_config(key: str) -> Path:
    return ROOT / config[key]


def header() -> None:
    now = datetime.now()
    console.clear()
    console.print(Panel.fit(
        f"[bold cyan]Welcome to BulkSMS 1.0[/bold cyan]\n\nCriador:\n{config['creator']}\n\nData: {now:%Y-%m-%d}\nHora: {now:%H:%M:%S}",
        border_style="cyan",
    ))


def menu() -> str:
    header()
    console.print("""[bold]
1 Importar contatos
2 Listar arquivos
3 Escolher mensagem
4 Iniciar envio
5 Estatísticas
6 Ver logs
7 Configurações
8 Ajuda
9 Sair[/bold]""")
    return Prompt.ask("Escolha", choices=[str(i) for i in range(1, 10)])


def choose_contact_file() -> Path | None:
    files = list_contact_files(path_from_config("contacts_dir"))
    if not files:
        console.print("[yellow]Nenhum arquivo CSV, TXT ou XLSX encontrado em contacts/.[/yellow]")
        return None
    for index, file in enumerate(files, 1):
        console.print(f"[{index}] {file.name}")
    choice = IntPrompt.ask("Arquivo", choices=[str(i) for i in range(1, len(files) + 1)])
    return files[choice - 1]


def import_contacts_menu() -> None:
    global contacts, stats
    file = choose_contact_file()
    if not file:
        return
    contacts = import_contacts(file, config["default_country_code"])
    stats.total_imported = len(contacts)
    console.print(f"[green]{len(contacts)} contatos válidos importados de {file.name}.[/green]")


def list_files_menu() -> None:
    table = Table(title="Arquivos disponíveis")
    table.add_column("Pasta")
    table.add_column("Arquivo")
    for folder in ["contacts_dir", "messages_dir", "logs_dir", "exports_dir"]:
        directory = path_from_config(folder)
        directory.mkdir(exist_ok=True)
        for file in sorted(directory.iterdir()):
            table.add_row(directory.name, file.name)
    console.print(table)


def choose_message() -> None:
    global message_text
    files = sorted([p for p in path_from_config("messages_dir").iterdir() if p.is_file()])
    for index, file in enumerate(files, 1):
        console.print(f"[{index}] {file.name}")
    console.print("[0] Digitar mensagem manualmente")
    choice = IntPrompt.ask("Escolha", choices=[str(i) for i in range(0, len(files) + 1)])
    if choice == 0:
        message_text = Prompt.ask("Digite a mensagem")
    else:
        message_text = files[choice - 1].read_text(encoding="utf-8").strip()
    console.print(f"[green]Mensagem selecionada com {len(message_text)} caracteres.[/green]")


def panel(current: str, start: float) -> Panel:
    stats.elapsed_seconds = time.time() - start
    body = (
        f"Total de contatos: {stats.total_imported}\nEnviados: {stats.total_sent}\n"
        f"Sucesso: {stats.success}\nFalhas: {stats.failures}\nPercentual concluído: {stats.percent:.1f}%\n"
        f"Tempo decorrido: {stats.elapsed_text()}\nNúmero atual: {current}"
    )
    return Panel(body, title="Envio em andamento", border_style="green")


def start_sending() -> None:
    if not contacts:
        console.print("[red]Importe contatos antes de enviar.[/red]")
        return
    if not message_text:
        console.print("[red]Escolha ou digite uma mensagem antes de enviar.[/red]")
        return
    log_file = create_log_file(path_from_config("logs_dir"))
    start = time.time()
    with Live(panel("Aguardando", start), refresh_per_second=4) as live:
        for number in contacts:
            ok, error = send_sms(number, message_text)
            stats.total_sent += 1
            if ok:
                stats.success += 1
                write_log(log_file, number, "SUCESSO", message_text)
            else:
                stats.failures += 1
                write_log(log_file, number, "FALHA", message_text, error)
            live.update(panel(number, start))
            time.sleep(float(config.get("send_delay_seconds", 1)))
    console.print(f"[green]Envio finalizado. Log: {log_file}[/green]")


def show_stats() -> None:
    console.print(Panel(
        f"Total importados: {stats.total_imported}\nTotal enviados: {stats.total_sent}\nSucesso: {stats.success}\nFalhas: {stats.failures}\nTempo total: {stats.elapsed_text()}",
        title="Estatísticas",
    ))


def show_logs() -> None:
    logs = list_logs(path_from_config("logs_dir"))
    for index, log in enumerate(logs[:20], 1):
        console.print(f"[{index}] {log.name}")
    if logs:
        console.print(logs[0].read_text(encoding="utf-8", errors="ignore")[-2000:])


def settings_menu() -> None:
    console.print_json(json.dumps(config, ensure_ascii=False))
    if Prompt.ask("Executar atualização do GitHub agora?", choices=["s", "n"], default="n") == "s":
        subprocess.run(config["github_update_command"].split(), cwd=ROOT.parent, check=False)
    if Prompt.ask("Gerar contatos de Moçambique +258?", choices=["s", "n"], default="n") == "s":
        quantity = IntPrompt.ask("Quantidade", default=10)
        generated = generate_mozambique_contacts(quantity)
        output = path_from_config("contacts_dir") / f"mozambique_{quantity}.txt"
        output.write_text("\n".join(generated) + "\n", encoding="utf-8")
        console.print(f"[green]Gerado: {output}[/green]")


def help_menu() -> None:
    console.print(Panel("Use contacts/ para CSV, TXT ou XLSX; messages/ para textos; configure permissões de SMS no Termux:API. Atualize arquivos do GitHub em Configurações com git pull --ff-only."))


def main() -> None:
    actions = {"1": import_contacts_menu, "2": list_files_menu, "3": choose_message, "4": start_sending, "5": show_stats, "6": show_logs, "7": settings_menu, "8": help_menu}
    while True:
        choice = menu()
        if choice == "9":
            break
        actions[choice]()
        Prompt.ask("Pressione Enter para continuar", default="")


if __name__ == "__main__":
    main()
