#!/bin/bash
set -euo pipefail

IMAGE_NAME="infusion-pump-sim"
CONTAINER_NAME="infusion-pump-run"

echo "=== Building Docker image ==="
docker build -t "$IMAGE_NAME" .

echo "=== Running simulation ==="
docker run --name "$CONTAINER_NAME" "$IMAGE_NAME"

echo "=== Copying resultados.csv to local ==="
docker cp "$CONTAINER_NAME":/app/resultados.csv ./resultados.csv

echo "=== Cleaning up container ==="
docker rm "$CONTAINER_NAME"

echo "=== Done! resultados.csv saved locally ==="
