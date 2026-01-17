#!/bin/bash
set -e

echo "Setting up swap if not exists..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

echo "Stopping old containers..."
docker compose -f production.docker-compose.yml down

echo "Starting new containers..."
docker compose -f production.docker-compose.yml up -d

echo "Cleaning up..."
docker system prune -f

echo "Deployment complete!"
docker compose -f production.docker-compose.yml ps
