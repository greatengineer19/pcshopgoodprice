#!/bin/bash
set -e

echo "Stopping old containers..."
docker compose -f local.docker-compose.yml down

echo "Starting new containers..."
docker compose -f local.docker-compose.yml up -d

echo "Cleaning up..."
docker system prune -f

echo "Deployment complete!"
docker compose -f local.docker-compose.yml ps

