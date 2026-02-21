# MLOps Pipeline Prototype

A modern, production-grade MLOps pipeline demonstrating data orchestration, validation, and monitoring using the **Dagster**, **Pydantic**, and **Evidently** stack.

## 🚀 Overview

This project implements a complete data engineering lifecycle for machine learning:
1.  **Orchestration:** Dagster manages the flow of data across assets.
2.  **Validation:** Pydantic ensures data integrity at the ingestion stage.
3.  **Monitoring:** Evidently detects data drift to prevent model performance degradation.

## 📁 Repository Structure

```text
.
├── src/orchestration/       # Dagster definitions and pipeline logic
│   ├── defs/                # Modular asset, job, and schedule definitions
│   ├── basic_assets.py      # Introductory Dagster concepts
│   └── validated_drift_pipeline.py # Integrated end-to-end pipeline
├── schemas/                 # Pydantic data models (Data Validation)
│   ├── sales_validation.py
│   ├── store_location_validation.py
│   └── order_management_validation.py
├── monitoring/              # Evidently AI configurations (Drift Detection)
│   ├── drift_report_html.py
│   ├── drift_detection_logic.py
│   └── sample_results.json  # Example drift report output
├── incoming_data/           # landing zone for raw CSV/JSON files
├── Dockerfile               # Multi-stage, optimized production image
└── pyproject.toml           # Project dependencies and tool configuration
```

## 🛠️ Key Features

-   **Automated Data Ingestion:** Uses Dagster Sensors to monitor `incoming_data/` and trigger pipelines on new file arrivals.
-   **Schema Enforcement:** Strict validation using Pydantic models to catch "bad data" before it reaches downstream processes.
-   **Drift Detection:** Implements Population Stability Index (PSI) checks via Evidently to monitor for distribution shifts in incoming features.
-   **Cloud-Ready Dockerization:** Multi-stage `Dockerfile` leveraging `uv` for lightning-fast builds and minimal image size.

## 🚦 Getting Started

### Prerequisites
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) installed

### Local Development
1. Install dependencies:
   ```bash
   uv sync
   ```
2. Launch the Dagster UI:
   ```bash
   dg dev
   ```
3. Open `http://localhost:3000` to view the asset graph and trigger runs.

### Docker
Build and run the containerized pipeline:
```bash
docker build -t mlops-pipeline .
docker run -p 3000:3000 mlops-pipeline
```

## 📊 Pipeline Flow
`raw_data_batch` (Ingestion) ➔ `validated_data` (Pydantic) ➔ `drift_report` (Evidently)
