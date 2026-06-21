#!/bin/bash
set -euo pipefail

IMAGE_NAME="infusion-pump-sim"
CONTAINER_NAME="infusion-pump-run"

echo "=== Building Docker image ==="
docker build -t "$IMAGE_NAME" .

echo "=== Cleaning up old container if exists ==="
docker rm -f "$CONTAINER_NAME" 2>/dev/null || true

echo "=== Running simulation ==="
docker run --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "=== Copying resultados to local ==="
docker cp "$CONTAINER_NAME":/app/resultados ./

echo "=== Cleaning up container ==="
docker rm "$CONTAINER_NAME"

echo "=== Done! Results saved locally in 'resultados/' ==="
