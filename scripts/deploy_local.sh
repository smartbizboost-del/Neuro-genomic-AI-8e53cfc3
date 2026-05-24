#!/usr/bin/env bash
# Local deploy helper: builds images and runs docker-compose
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

echo "Building Docker images and starting services via docker-compose..."

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not on PATH." >&2
  exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
  echo "docker-compose not found. Trying 'docker compose'..."
  USE_DOCKER_COMPOSE_CMD="docker compose"
else
  USE_DOCKER_COMPOSE_CMD="docker-compose"
fi

# Build images using the local Dockerfiles under docker/
docker build -f docker/Dockerfile.api -t neurogenomic/api:local -t neurogenomic/api:latest docker
docker build -f docker/Dockerfile.worker -t neurogenomic/worker:local -t neurogenomic/worker:latest docker
docker build -f docker/Dockerfile.dashboard -t neurogenomic/dashboard:local -t neurogenomic/dashboard:latest docker

echo "Bringing up services with docker-compose..."
$USE_DOCKER_COMPOSE_CMD up -d --build

echo "Services started. API: http://localhost:8000/docs  Dashboard: http://localhost:8501"
