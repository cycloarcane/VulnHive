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
    "lfi-target": {"name": "Apache LFI", "port": 54321, "owasp": "A01", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "crypto-target": {"name": "SweetRice Crypto", "port": 54330, "owasp": "A02", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "sqli-target": {"name": "Cuppa SQLi", "port": 54323, "owasp": "A03", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "rce-target": {"name": "Atom CMS RCE", "port": 54322, "owasp": "A03", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "xss-target": {"name": "Wonder XSS", "port": 54324, "owasp": "A03", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "design-target": {"name": "Bus Pass IDOR", "port": 54328, "owasp": "A04", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "config-target": {"name": "CMSimple Config", "port": 54329, "owasp": "A05", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "outdated-target": {"name": "Log4j Node", "port": 54331, "owasp": "A06", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "auth-target": {"name": "Fuel CMS Auth", "port": 54327, "owasp": "A07", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "backdoor-target": {"name": "PHP Backdoor", "port": 54325, "owasp": "A08", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "logging-target": {"name": "Silent Admin", "port": 54332, "owasp": "A09", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"},
    "ssrf-target": {"name": "osTicket SSRF", "port": 54326, "owasp": "A10", "reqs": 0, "attacks": 0, "status": "[red]OFFLINE[/]"}
}

OWASP_DESCRIPTIONS = {
    "A01: Broken Access Control": "Failure to enforce restrictions on what authenticated users can do.",
    "A02: Cryptographic Failures": "Exposure of sensitive data due to weak or missing encryption.",
    "A03: Injection": "User-supplied data is not validated, filtered, or sanitised by the application.",
    "A04: Insecure Design": "Vulnerabilities resulting from fundamental architectural and design flaws.",
    "A05: Security Misconfiguration": "Insecure default configurations, open storage, or verbose error messages.",
    "A06: Vulnerable Components": "Using third-party libraries or frameworks with known security flaws.",
    "A07: Identification/Auth Failures": "Weaknesses in session management or user identity verification.",
    "A08: Software/Data Integrity": "Failures in protecting code or data from unauthorised modification.",
    "A09: Logging/Monitoring Failures": "Critical events are not logged, or monitoring is insufficient to detect attacks.",
    "A10: SSRF": "Web applications fetch remote resources without validating the user-supplied URL."
}

recent_logs = deque(maxlen=20)
recent_attacks = deque(maxlen=15)

ATTACK_PATTERNS = {
    "SQLi": re.compile(r"(%27|%22|\bunion\s+select\b|\bselect\s+.*from\b|--|#|\bOR\s+1=1\b|'\s+|--\s+)", re.IGNORECASE),
    "LFI": re.compile(r"(\.\./|\.\.\\|%2e%2e|etc/passwd|etc/shadow|cgi-bin)", re.IGNORECASE),
    "XSS": re.compile(r"(%3C|<)script(%3E|>)|alert\(|onerror=|onload=", re.IGNORECASE),
    "RCE": re.compile(r"(zerodium|\bsystem\s*\(|\beval\s*\(|\bwhoami\b|\bid\b|\bls\s+-)", re.IGNORECASE),
    "SSRF": re.compile(r"(localhost|127\.0\.0\.1|169\.254\.169\.254|0\.0\.0\.0|http:\/\/|https:\/\/)", re.IGNORECASE),
    "AUTH": re.compile(r"(\badmin\b|\blogin\b|\bauth\b|fuel|pages\/select\/)", re.IGNORECASE),
    "IDOR": re.compile(r"(viewid=|id=\d+)", re.IGNORECASE),
    "MISCONFIG": re.compile(r"(&login|\bpasswd=\b|\bpassword=\b|config|setup)", re.IGNORECASE),
    "CRYPTO": re.compile(r"(\.db\.php|hash|md5|base64|encrypt|decrypt)", re.IGNORECASE),
    "LOG4J": re.compile(r"(\$\{jndi:(ldap|rmi|dns|dns):\/\/)", re.IGNORECASE)
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
            output = subprocess.check_output(["docker", "ps", "--format", "{{.Names}}"]).decode()
            for key in services.keys():
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
        Layout(name="left", ratio=1),
        Layout(name="logs", ratio=2)
    )
    layout["left"].split_column(
        Layout(name="stats", ratio=2),
        Layout(name="reference", ratio=1)
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

    # Stats Table (Sorted by OWASP)
    table = Table(expand=True, border_style="cyan", show_header=True, header_style="bold cyan")
    table.add_column("Service", style="bold white")
    table.add_column("Port", justify="center", style="cyan")
    table.add_column("OWASP", justify="center", style="bold yellow")
    table.add_column("Status", justify="center")
    table.add_column("Attacks", justify="right", style="red")

    # Sort services by OWASP tag (A01, A02, etc.)
    sorted_svc = sorted(services.items(), key=lambda x: x[1]['owasp'])
    for _, data in sorted_svc:
        table.add_row(data["name"], str(data["port"]), data["owasp"], data["status"], str(data["attacks"]))
    layout["stats"].update(Panel(table, title="[bold cyan]Hive Node Status", border_style="cyan"))

    # OWASP Reference Panel
    ref_text = Text()
    for cat, desc in OWASP_DESCRIPTIONS.items():
        ref_text.append(f"{cat}: ", style="bold yellow")
        ref_text.append(f"{desc}\n", style="white")
    layout["reference"].update(Panel(ref_text, title="[bold white]OWASP Top Ten Reference", border_style="white"))

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
