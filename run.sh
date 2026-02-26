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

echo "============================================================"
echo "                [ VULNHIVE: THE REAL-WORLD VULNERABILITY HIVE ]"
echo "============================================================"
echo ""

# Check for docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed."
    exit 1
fi

echo "Select services to spin up (Separated by space, e.g. 1 2):"
echo "1) LFI/RCE (Apache 2.4.49)      - Port 54321"
echo "2) RCE (Atom CMS 2.0)           - Port 54322"
echo "3) SQLi (Cuppa CMS v1.0)        - Port 54323"
echo "4) XSS (WonderCMS 3.4.2)        - Port 54324"
echo "5) PHP RCE (Backdoor)           - Port 54325"
echo "6) SSRF (osTicket 1.14.2)       - Port 54326"
echo "7) Auth Failure (Fuel CMS 1.4.1) - Port 54327"
echo "8) Insecure Design (Bus Pass 1.0) - Port 54328"
echo "9) ALL SERVICES"
echo ""
read -p "Selection: " choice

SERVICES=""
for i in $choice; do
    case $i in
        1) SERVICES="$SERVICES lfi-target" ;;
        2) SERVICES="$SERVICES rce-target target-db" ;;
        3) SERVICES="$SERVICES sqli-target target-db" ;;
        4) SERVICES="$SERVICES xss-target" ;;
        5) SERVICES="$SERVICES backdoor-target" ;;
        6) SERVICES="$SERVICES ssrf-target target-db" ;;
        7) SERVICES="$SERVICES auth-target target-db" ;;
        8) SERVICES="$SERVICES design-target target-db" ;;
        9) SERVICES="lfi-target rce-target sqli-target xss-target backdoor-target ssrf-target auth-target design-target target-db" ;;
    esac
done

if [ -z "$SERVICES" ]; then
    echo "No services selected. Exiting."
    exit 0
fi

echo "Spinning up VulnHive nodes: $SERVICES..."
docker-compose up -d $SERVICES

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
echo "============================================================"

# Trap Ctrl+C to stop services
trap "echo -e '\nClosing the Hive...'; docker-compose down; exit" INT

echo ""
echo "Do you want to launch the VulnHive SOC Terminal? (y/n)"
read -p "> " launch_dash

if [[ "$launch_dash" == "y" || "$launch_dash" == "Y" ]]; then
    # Isolated dependency management
    if command -v uv &> /dev/null; then
        echo "Launching SOC with uv..."
        uv run --with rich python3 dashboard.py
    else
        if [ ! -d ".venv" ]; then
            echo "Creating virtual environment for the SOC..."
            python3 -m venv .venv
        fi
        echo "Ensuring dependencies in .venv..."
        ./.venv/bin/python3 -m pip install -q rich
        clear
        ./.venv/bin/python3 dashboard.py
    fi
else
    echo "Press Ctrl+C to bring services down."
    docker-compose logs -f $SERVICES
fi

