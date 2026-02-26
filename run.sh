#!/usr/bin/env bash
set -e

# VulnHive ASCII Art
echo -e "\e[1;31m██╗   ██╗██╗   ██╗██╗     ███╗   ██╗\e[1;32m██╗  ██╗██╗██╗   ██╗███████╗\e[0m"
echo -e "\e[1;31m██║   ██║██║   ██║██║     ████╗  ██║\e[1;32m██║  ██║██║██║   ██║██╔════╝\e[0m"
echo -e "\e[1;31m██║   ██║██║   ██║██║     ██╔██╗ ██║\e[1;32m███████║██║██║   ██║█████╗  \e[0m"
echo -e "\e[1;31m╚██╗ ██╔╝██║   ██║██║     ██║╚██╗██║\e[1;32m██╔══██║██║╚██╗ ██╔╝██╔══╝  \e[0m"
echo -e "\e[1;31m ╚████╔╝ ╚██████╔╝███████╗██║ ╚████║\e[1;32m██║  ██║██║ ╚████╔╝ ███████╗\e[0m"
echo -e "\e[1;31m  ╚═══╝   ╚═════╝ ╚══════╝╚═╝  ╚═══╝\e[1;32m╚═╝  ╚═╝╚═╝  ╚═══╝  ╚══════╝\e[0m"
echo -e "\e[1;33m                [ THE REAL-WORLD VULNERABILITY HIVE ]\e[0m"
echo ""

# Check for docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed."
    exit 1
fi

# Clean up any old selection and lockdown state
rm -f .selection .lockdown

# Isolated environment setup for interactive menu
if command -v uv &> /dev/null; then
    uv run --quiet --with questionary python3 selector.py
else
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment for the interactive menu..."
        python3 -m venv .venv
    fi
    ./.venv/bin/python3 -m pip install -q questionary rich
    ./.venv/bin/python3 selector.py
fi

# Read selection from file
if [ ! -f ".selection" ]; then
    echo "No services selected. Exiting."
    exit 0
fi

SERVICES=$(cat .selection)
rm -f .selection

# Check for Lockdown Mode
COMPOSE_CMD="docker-compose"
if [ -f ".lockdown" ]; then
    echo -e "\e[1;31m[!] LOCKDOWN MODE ENABLED: Internet egress is blocked.\e[0m"
    COMPOSE_CMD="docker-compose -f docker-compose.yml -f docker-compose.lockdown.yml"
    rm -f .lockdown
fi

echo "Spinning up VulnHive nodes: $SERVICES..."
$COMPOSE_CMD up -d $SERVICES

echo ""
echo "============================================================"
echo "VULNHIVE IS ACTIVE (Localhost Only)"
echo "LFI/RCE:    http://127.0.0.1:54321/cgi-bin/.%%32e/.%%32e/.%%32e/.%%32e/etc/passwd"
echo "Atom RCE:   http://127.0.0.1:54322"
echo "Cuppa SQLi: http://127.0.0.1:54323"
echo "Wonder XSS: http://127.0.0.1:54324"
echo "PHP B-door: http://127.0.0.1:54325/?cmd=id"
echo "SSRF:       http://127.0.0.1:54326"
echo "Fuel Auth:  http://127.0.0.1:54327"
echo "IDOR Node:  http://127.0.0.1:54328"
echo "Config Node: http://127.0.0.1:54329"
echo "Crypto Node: http://127.0.0.1:54330"
echo "Log4j Node:  http://127.0.0.1:54331"
echo "Logging Fail: http://127.0.0.1:54332"
echo "Exceptional:  http://127.0.0.1:54333/?crash=1"
echo "============================================================"

# Trap Ctrl+C to stop services
trap "echo -e '\nClosing the Hive...'; docker-compose down; exit" INT

echo ""
echo "Do you want to launch the VulnHive SOC Terminal? (y/n)"
read -p "> " launch_dash

if [[ "$launch_dash" == "y" || "$launch_dash" == "Y" ]]; then
    if command -v uv &> /dev/null; then
        uv run --quiet --with rich python3 dashboard.py
    else
        clear
        ./.venv/bin/python3 dashboard.py
    fi
else
    echo "Press Ctrl+C to bring services down."
    docker-compose logs -f $SERVICES
fi
