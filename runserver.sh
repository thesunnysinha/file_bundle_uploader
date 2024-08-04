#!/bin/bash

# Stop all running containers
sudo docker stop $(sudo docker ps -q)

# Remove all containers
sudo docker rm $(sudo docker ps -a -q)

# Remove all networks
sudo docker network prune -f

# Remove all volumes
sudo docker volume prune -f

# Remove all unused Docker data, including images
sudo docker system prune -a -f

# Rebuild and start Docker Compose services
sudo docker-compose up --build
