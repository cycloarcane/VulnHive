#!/usr/bin/env bash
set -e

# Build the docker container
docker build -t vuln-test-server .

echo ""
echo "============================================================"
echo "Starting Vulnerable Server..."
echo "Use Arrow Keys + Space to select vulnerabilities, Enter to start."
echo "Press Ctrl+C at any time to stop."
echo "============================================================"
echo ""

# Run the docker container with interactive TTY allocated
docker run -it --rm -p 8000:8000 vuln-test-server
