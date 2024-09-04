#!/bin/bash

# Step 1: Stop and remove the current containers
docker compose -f docker-compose-dev.yaml down

# Step 2: Build the server Docker image
docker build -f ./server/Dockerfile -t "server:latest" .

# Step 3: Build the client Docker image
docker build -f ./client/Dockerfile -t "client:latest" .

# Step 4: Start the containers and rebuild if necessary
docker compose -f docker-compose-dev.yaml up -d --build
