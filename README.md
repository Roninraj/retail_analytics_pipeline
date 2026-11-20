

# Industrial-Grade Customer Retail Analytics Pipeline

An end-to-end, high-performance data analytics pipeline designed to process over 1M+ retail transactions, perform ML-driven customer segmentation, and serve real-time insights via a scalable microservices architecture.

##  Industrial Architecture

### 1. Data Ingestion & Collection
*   **Service:** Python Ingestion Worker (`Scripts/ingest_data.py`).
*   **Layer:** Raw Ingestion Layer (MySQL).
*   **Process:** Handles robust parsing of large datasets and bulk-loading into the ingestion layer.

### 2. Processing & Transformation (ETL)
*   **Engine:** Apache Spark 3.5.0 (PySpark).
*   **Process:** Distributed cleaning, deduplication, and transformation of raw transaction data.

### 3. Analytics & Modeling
*   **Engine:** Spark MLlib.
*   **Algorithms:** RFM (Recency, Frequency, Monetary) Analysis + K-Means Clustering for advanced customer segmentation.

### 4. Data Storage (Analytical Warehouse)
*   **Layer:** Structured Analytics Layer (MySQL).
*   **Store:** Pre-aggregated metrics, cluster profiles, and temporal trends optimized for high-speed querying.

### 5. Data Serving (Industrial Backend)
*   **Framework:** FastAPI.
*   **Features:**
    *   **Asynchronous I/O:** High-concurrency request handling.
    *   **Pydantic Schemas:** Strict data validation and serialization.
    *   **Connection Pooling:** Optimized database performance using SQLAlchemy.
    *   **Layered Architecture:** Clear separation of API and Data access.

### 6. Visualization & Monitoring (BI Dashboard)
*   **Framework:** Django + Plotly + Bootstrap 5.
*   **Insights:** Executive KPI Scorecards, Global Revenue Heatmaps, Product Performance Charts, and Cluster Analysis.

##  Orchestration & Deployment

The entire system is containerized and managed via **Kubernetes**.

### Prerequisites
*   Docker Desktop (with Kubernetes enabled) or Minikube.
*   `kubectl` installed and configured.

### Quick Deploy
```bash
# Deploys the full stack including DB, Jobs, API, and Dashboard
bash Scripts/deploy.sh
```

## 📈 Monitoring
Access the dashboard at `http://localhost:8080`.
Verify job logs with `kubectl logs -l job-name=spark-analytics-job`.
