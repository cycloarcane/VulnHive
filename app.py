import os
import sys
import logging
import sqlite3
import subprocess
from flask import Flask, request, render_template_string, Response
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

app = Flask(__name__)
console = Console()

# In-memory DB for SQLi
def init_db():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'supersecret')")
    cursor.execute("INSERT INTO users (username, password) VALUES ('test', 'test')")
    conn.commit()
    return conn

db_conn = init_db()

active_vulns = []

@app.before_request
def log_request():
    req_details = f"Method: {request.method}
Path: {request.path}
Headers:
"
    for k, v in request.headers.items():
        req_details += f"  {k}: {v}
"
    if request.args:
        req_details += f"Args: {request.args}
"
    if request.form:
        req_details += f"Form: {request.form}
"
    if request.data:
        req_details += f"Data: {request.data.decode('utf-8', errors='ignore')}
"
    
    console.print(Panel(Syntax(req_details, "yaml", theme="monokai", word_wrap=True), title=f"[bold green]Incoming Request: {request.path}[/bold green]", border_style="green"))

@app.route('/')
def index():
    html = "<h1>Vulnerable Test Server</h1><ul>"
    for vuln in active_vulns:
        html += f"<li><a href='/{vuln}'>/{vuln}</a></li>"
    html += "</ul>"
    return html

@app.route('/sqli', methods=['GET', 'POST'])
def sqli():
    if 'sqli' not in active_vulns: return "Disabled", 404
    
    if request.method == 'POST':
        username = request.form.get('username', '')
        query = f"SELECT * FROM users WHERE username = '{username}'"
        console.print(f"[bold red]Executing SQL:[/] {query}")
        try:
            cursor = db_conn.cursor()
            cursor.execute(query)
            user = cursor.fetchone()
            if user: return f"Welcome {user[1]}! Your password is {user[2]}."
            else: return "Invalid user"
        except Exception as e:
            return str(e)
            
    return '<form method="POST">Username: <input type="text" name="username"><input type="submit" value="Login"></form>'

@app.route('/rce', methods=['GET', 'POST'])
def rce():
    if 'rce' not in active_vulns: return "Disabled", 404
        
    if request.method == 'POST':
        ip = request.form.get('ip', '')
        cmd = f"ping -c 1 {ip}"
        console.print(f"[bold red]Executing Command:[/] {cmd}")
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
            return f"<pre>{output}</pre>"
        except Exception as e:
            return str(e)

    return '<form method="POST">Ping IP: <input type="text" name="ip"><input type="submit" value="Ping"></form>'

@app.route('/lfi', methods=['GET'])
def lfi():
    if 'lfi' not in active_vulns: return "Disabled", 404
        
    file_path = request.args.get('file', 'app.py')
    console.print(f"[bold red]Reading File:[/] {file_path}")
    try:
        with open(file_path, 'r') as f:
            return f"<pre>{f.read()}</pre>"
    except Exception as e:
        return str(e)

@app.route('/xss', methods=['GET'])
def xss():
    if 'xss' not in active_vulns: return "Disabled", 404
    
    name = request.args.get('name', 'Guest')
    return render_template_string(f"<h1>Hello {name}</h1>")

if __name__ == '__main__':
    choices = [
        questionary.Choice("SQL Injection (SQLi)", value="sqli"),
        questionary.Choice("Command Injection (RCE)", value="rce"),
        questionary.Choice("Local File Inclusion (LFI)", value="lfi"),
        questionary.Choice("Cross-Site Scripting (XSS)", value="xss")
    ]
    
    selected = questionary.checkbox("Select vulnerabilities to enable:", choices=choices).ask()
    
    if not selected:
        print("No vulnerabilities selected. Exiting.")
        sys.exit(0)
        
    active_vulns.extend(selected)
    console.print(f"[bold yellow]Starting server with vulnerabilities:[/] {', '.join(active_vulns)}")
    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(host='0.0.0.0', port=8000)
