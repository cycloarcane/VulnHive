#!/usr/bin/env bash
set -e

# Build the docker container
docker build -t vuln-test-server .

echo ""
echo "============================================================"
echo "Starting Hardened Vulnerable Server..."
echo "Use Arrow Keys + Space to select vulnerabilities, Enter to start."
echo "Press Ctrl+C at any time to stop."
echo "============================================================"
echo ""

# Run the docker container with strict isolation
docker run -it --rm 
  -p 8000:8000 
  --cap-drop=ALL 
  --security-opt=no-new-privileges 
  --read-only 
  --tmpfs /tmp:rw,noexec,nosuid 
  --cpus="0.5" 
  --memory="256m" 
  --pids-limit=50 
  vuln-test-server
