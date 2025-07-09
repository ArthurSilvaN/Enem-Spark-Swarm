#!/bin/bash

# Build and Run ENEM Spark Pipeline
# This script builds the Docker image and runs the complete pipeline

set -e

echo "Building Docker image..."
docker build -t enem-spark-job -f misc/Dockerfile .

echo "Starting services with Docker Compose..."
cd misc
docker-compose up --scale spark-worker=2 --scale datanode=1 -d

echo "Pipeline started successfully!"
echo "Access Spark Master UI at: http://localhost:8080"
echo "Access HDFS UI at: http://localhost:9870"
echo ""
echo "To stop the services, run: ./bin/stop.sh"
