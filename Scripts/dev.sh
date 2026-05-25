#!/bin/bash

echo "Starting Local Development Environment (Docker Compose) on new ports..."

# Launch Docker Compose
docker compose up -d

echo "---------------------------------------------------"
echo "Development environment is UP!"
echo "Backend (Hot-reload): http://localhost:9000"
echo "Frontend (Hot-reload): http://localhost:9090"
echo "MySQL: localhost:3307"
echo "---------------------------------------------------"
echo "To initialize DB: docker exec -it retail-spark-dev python3 Scripts/init_db.py"
echo "To run Ingestion: docker exec -it retail-spark-dev python3 Scripts/ingest_data.py"
echo "To run Analytics: docker exec -it retail-spark-dev /opt/spark/bin/spark-submit --jars /opt/spark/jars/mysql-connector-j-8.0.33.jar Scripts/spark_analytics.py"
echo "---------------------------------------------------"
echo "Logs: docker compose logs -f"
