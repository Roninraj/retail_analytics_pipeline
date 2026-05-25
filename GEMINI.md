# Project: Industrial-Grade Customer Retail Analytics Pipeline

## Core Mandates
- **Architecture:** Strictly adhere to the 6-stage data analytics pipeline (Ingestion, ETL, Storage, Analysis, Visualization, Orchestration).
- **Backend Standards:**
    - **Service Pattern:** Decouple API routes from data access logic.
    - **Performance:** Use asynchronous patterns and database connection pooling.
    - **Reliability:** Implement comprehensive error handling and structured logging.
    - **Validation:** Every endpoint MUST use Pydantic schemas for response modeling.
- **Scripts Directory:** ALL standalone utility, operational, and processing scripts (DB init, ingestion, Spark jobs) MUST be in the `Scripts/` directory.
- **Visualization:** Dashboards must feature high-impact, interactive BI visualizations (executive scorecards, geospatial maps, and temporal trends).
- **Security:** Use Kubernetes Secrets for sensitive configurations and environment-specific variables.
- **Orchestration:** Maintain separate deployments for services to allow independent scaling.
