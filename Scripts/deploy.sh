#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"

echo "Starting Retail Analytics Pipeline Deployment..."

# Build Docker images (assuming minikube or local registry)
echo "Building Docker images..."
docker build -t retail-ingest:latest -f Dockerfile.ingest .
docker build -t retail-spark:latest -f Dockerfile.spark .
docker build -t retail-backend:latest -f Dockerfile.backend .
docker build -t retail-frontend:latest -f Dockerfile.frontend .

# Apply K8s manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/mysql.yaml

echo "Waiting for MySQL to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/mysql

echo "Running Ingestion and Spark Jobs..."
kubectl apply -f k8s/jobs.yaml

echo "Deploying Backend and Frontend..."
kubectl apply -f k8s/apps.yaml

echo "Deployment complete. Frontend will be available at http://localhost:30080 (assuming NodePort access)"
