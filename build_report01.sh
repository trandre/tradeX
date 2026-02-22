#!/bin/bash
# One-shot script: grants docker access + builds the report01 image
# Run with: bash /opt/tradeX/build_report01.sh

set -e

echo "==> Adding $USER to docker group..."
sudo usermod -aG docker "$USER"

echo "==> Building report01 image (running as docker group)..."
sg docker -c "docker build -f /opt/tradeX/Dockerfile.report01 -t report01 /opt/tradeX"

echo ""
echo "✓ Image 'report01' built successfully."
echo ""
echo "Run it with:"
echo "  docker run --rm --network=host --env-file /opt/tradeX/.env -v /opt/tradeX/logs:/app/logs report01"
echo "  docker run --rm --network=host --env-file /opt/tradeX/.env -v /opt/tradeX/logs:/app/logs report01 > report_\$(date +%F).txt"
