import sys
import re
import subprocess
import threading
from datetime import datetime
from collections import deque
from time import sleep

from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich.align import Align

# State
services = {
    "lfi-target": {"name": "Apache LFI", "port": 54321, "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "rce-target": {"name": "Atom CMS RCE", "port": 54322, "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "sqli-target": {"name": "Cuppa SQLi", "port": 54323, "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "xss-target": {"name": "Wonder XSS", "port": 54324, "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "backdoor-target": {"name": "PHP Backdoor", "port": 54325, "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "ssrf-target": {"name": "osTicket SSRF", "port": 54326, "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "auth-target": {"name": "Fuel CMS Auth", "port": 54327, "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"}
}

recent_logs = deque(maxlen=20)
recent_attacks = deque(maxlen=15)

ATTACK_PATTERNS = {
    "SQLi": re.compile(r"(%27|%22|union\s+select|select\s+.*from|--|#|OR\s+1=1|'\s+|--\s+)", re.IGNORECASE),
    "LFI": re.compile(r"(\.\.|%2e|etc/passwd|etc/shadow|cgi-bin)", re.IGNORECASE),
    "XSS": re.compile(r"(%3C|<)script(%3E|>)", re.IGNORECASE),
    "RCE": re.compile(r"(zerodium|system\(|cmd=|eval\(|id|whoami|ls\s+-)", re.IGNORECASE),
    "SSRF": re.compile(r"(localhost|127\.0\.0\.1|169\.254\.169\.254|0\.0\.0\.0|http:\/\/|https:\/\/)", re.IGNORECASE),
    "AUTH": re.compile(r"(admin|login|auth|fuel|pages\/select\/)", re.IGNORECASE)
}

def detect_attack(log_line):
    detected = []
    for attack_type, pattern in ATTACK_PATTERNS.items():
        if pattern.search(log_line):
            detected.append(attack_type)
    return detected

def update_status():
    while True:
        try:
            # Get all running container names
            output = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"]).decode()
            for key in services.keys():
                # Check if our target service key exists as a substring in any running container name
                if any(key in line for line in output.splitlines()):
                    services[key]["status"] = "[bold green]ONLINE[/]"
                else:
                    services[key]["status"] = "[bold red]OFFLINE[/]"
        except Exception:
            pass
        sleep(2)

def stream_logs():
    process = subprocess.Popen(
        ["docker-compose", "logs", "-f", "--tail=0"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line: continue
        
        # Parse docker-compose log format
        parts = line.split(" | ", 1)
        if len(parts) == 2:
            container, msg = parts
            svc_key = next((k for k in services.keys() if k in container), None)
            
            if svc_key:
                services[svc_key]["reqs"] += 1
                attacks = detect_attack(msg)
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                recent_logs.append(f"[dim]{timestamp}[/] [cyan]{services[svc_key]['name']}[/] {msg[:100]}...")
                
                if attacks:
                    services[svc_key]["attacks"] += 1
                    tags = " ".join([f"[white on red] {a} [/]" for a in attacks])
                    recent_attacks.append(f"[dim]{timestamp}[/] {tags} [bold red]{services[svc_key]['name']}[/] -> [yellow]{msg[:80]}[/]")

def generate_dashboard():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=8),
        Layout(name="main")
    )
    layout["main"].split_row(
        Layout(name="stats", ratio=1),
        Layout(name="logs", ratio=2)
    )
    layout["logs"].split_column(
        Layout(name="attacks", ratio=1),
        Layout(name="traffic", ratio=1)
    )

    # Header with ASCII Art
    ascii_art = Text()
    ascii_art.append(Text.from_markup("[bold red]██╗   ██╗██╗   ██╗██╗     ███╗   ██╗[/][bold green]██╗  ██╗██╗██╗   ██╗███████╗[/]\n"))
    ascii_art.append(Text.from_markup("[bold red]██║   ██║██║   ██║██║     ████╗  ██║[/][bold green]██║  ██║██║██║   ██║██╔════╝[/]\n"))
    ascii_art.append(Text.from_markup("[bold red]██║   ██║██║   ██║██║     ██╔██╗ ██║[/][bold green]███████║██║██║   ██║█████╗  [/]\n"))
    ascii_art.append(Text.from_markup("[bold red]╚██╗ ██╔╝██║   ██║██║     ██║╚██╗██║[/][bold green]██╔══██║██║╚██╗ ██╔╝██╔══╝  [/]\n"))
    ascii_art.append(Text.from_markup("[bold red] ╚████╔╝ ╚██████╔╝███████╗██║ ╚████║[/][bold green]██║  ██║██║ ╚████╔╝ ███████╗[/]\n"))
    ascii_art.append(Text.from_markup("[bold red]  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═══╝[/][bold green]╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝[/]"))
    
    header_content = Align.center(ascii_art)
    layout["header"].update(Panel(header_content, subtitle="[bold yellow]THE REAL-WORLD VULNERABILITY HIVE[/]", border_style="magenta"))

    # Stats Table
    table = Table(expand=True, border_style="cyan")
    table.add_column("Service", style="bold white")
    table.add_column("Port", justify="center", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Reqs", justify="right", style="green")
    table.add_column("Attacks", justify="right", style="red")

    for key, data in services.items():
        table.add_row(
            data["name"], 
            str(data["port"]), 
            data["status"], 
            str(data["reqs"]), 
            str(data["attacks"]) if data["attacks"] == 0 else f"[bold red]{data['attacks']}[/]"
        )
    layout["stats"].update(Panel(table, title="[bold cyan]Service Overview", border_style="cyan"))

    # Attacks Panel
    attack_text = Text.from_markup("\n".join(recent_attacks)) if recent_attacks else Text("No attacks detected yet...", style="dim")
    layout["attacks"].update(Panel(attack_text, title="[bold red]Detected Exploits & Attacks", border_style="red"))

    # Traffic Panel
    traffic_text = Text.from_markup("\n".join(recent_logs)) if recent_logs else Text("Waiting for traffic...", style="dim")
    layout["traffic"].update(Panel(traffic_text, title="[bold green]Live Traffic Feed", border_style="green"))

    return layout

if __name__ == "__main__":
    threading.Thread(target=update_status, daemon=True).start()
    threading.Thread(target=stream_logs, daemon=True).start()

    with Live(generate_dashboard(), refresh_per_second=4, screen=True) as live:
        try:
            while True:
                live.update(generate_dashboard())
                sleep(0.25)
        except KeyboardInterrupt:
            pass
