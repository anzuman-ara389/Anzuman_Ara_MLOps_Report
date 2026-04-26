# M6 – Data Engineering and Machine Learning Operations in Business
# Customer Churn MLOps Pipeline
Submitted by: Anzuman Ara
Student ID: 20241266


# Project Overview:
This project implements an advanced end-to-end MLOps pipeline for customer churn prediction. The main goal is to design a production-oriented system that can handle live data ingestion, preprocessing, model training, deployment, monitoring, drift detection, and retraining in a structured and reproducible way.

The system predicts whether a customer is likely to churn based on input features such as customer profile, service usage, billing behavior, and contract type.

A lightweight Streamlit frontend is included for interactive predictions and operational monitoring. FastAPI is used to expose real-time REST API endpoints. SQLite is used as a lightweight relational database to store live customer data, logs, drift reports, and model registry information.

# Pipeline Structure:
The pipeline consists of the following components:

1. Live Data Ingestion
New customer records are continuously simulated and inserted into the SQLite database. This represents how production systems receive incoming customer events from CRM, subscription, or billing systems.
Data ingestion can be triggered in three ways:
Manual execution using Python script
API endpoint /ingest-live
Scheduled GitHub Actions workflow
All incoming records are stored in the raw_customers table.

2. Database Layer
SQLite is used as the main storage layer.
Tables used:
raw_customers
prediction_logs
drift_reports
model_registry
This provides structured storage, reproducibility, and traceability.

3. Preprocessing
The pipeline reads raw customer data from the database and applies preprocessing steps:
handling missing values
numeric conversion
categorical encoding
target transformation
schema consistency checks
Processed data is stored as:
data/processed_data.csv

4. Feature Engineering
An additional derived feature is created:
avg_monthly_value = MonthlyCharges / (tenure + 1)
This helps capture the relationship between customer spending and customer lifetime.

5. Model Training
A Random Forest Classifier is used because it performs well on structured tabular data and is robust with limited tuning.
Training process:
load processed data
split train/test sets
train model
evaluate metrics
save artifacts
register model version

6. Model Versioning and Artifacts
Each training run saves versioned artifacts:
artifacts/model_YYYYMMDD_HHMMSS.pkl
artifacts/model_latest.pkl
artifacts/columns_latest.pkl
artifacts/metrics_latest.json
This supports rollback, reproducibility, and model comparison.

7. Deployment
FastAPI is used to deploy the trained model.
Available endpoints:
/health
/predict
/ingest-live
/drift-check
/retrain
/model-info
The API receives customer input data and returns churn predictions in real time.

8. Monitoring
Prediction logs are stored in the database to track model behavior over time.
The system also monitors incoming live data for drift.

9. Drift Detection
The pipeline compares historical customer data with the latest incoming batch using statistical mean shift.
Monitored features:
MonthlyCharges
TotalCharges
tenure
If drift score exceeds threshold:
0.20
A drift alert is created.

10. Conditional Retraining
If drift is detected:
Preprocess → Retrain → Save New Model
If no drift is found:
Retraining skipped
This reduces unnecessary compute cost.

11. Frontend Dashboard
A Streamlit dashboard is included with:
API health check
Live data ingestion button
Drift check button
Latest model information
Customer prediction form
Prediction result display
This improves usability and demonstrates real deployment.

# Project Structure:
customer-churn-mlops
├── app/                    # FastAPI application
│   └── main.py
├── src/                    # Pipeline scripts
│   ├── database.py
│   ├── live_ingestion.py
│   ├── preprocess.py
│   ├── train.py
│   ├── drift_detection.py
│   ├── auto_retrain.py
│   ├── check_database.py
│   ├── check_registry.py
│   └── check_drift.py
├── data/                   # SQLite database and processed files
│   ├── churn_mlops.db
│   └── processed_data.csv
├── artifacts/             # Saved models, metrics, schemas
├── logs/                  # Optional logs
├── .github/workflows/     # GitHub Actions automation
├── frontend.py            # Streamlit dashboard
├── Dockerfile             # Container setup
├── requirements.txt
└── README.md
# How to Run (Without Docker)
# Step 1: Install dependencies
pip install -r requirements.txt
# Step 2: Initialize database
python src/database.py
# Step 3: Generate live customer data
python src/live_ingestion.py
# Step 4: Run preprocessing
python src/preprocess.py
# # Step 5: Train model
python src/train.py
# Step 6: Run FastAPI server
uvicorn app.main:app --reload
# Step 7: Open Swagger API Docs
http://127.0.0.1:8000/docs
# Step 8: Run Streamlit dashboard
streamlit run frontend.py
# Step 9: Open frontend
http://localhost:8501
# How to Run with Docker
# Step 1: Build Docker image
docker build -t churn-mlops .
# Step 2: Run container
docker run -p 8000:8000 churn-mlops
# Step 3: Open API Docs
http://localhost:8000/docs
API Usage
Use the /predict endpoint.
Example input:
{
  "gender": "Female",
  "SeniorCitizen": 0,
  "Partner": "Yes",
  "Dependents": "No",
  "tenure": 12,
  "PhoneService": "Yes",
  "MultipleLines": "No",
  "InternetService": "Fiber optic",
  "OnlineSecurity": "No",
  "OnlineBackup": "Yes",
  "DeviceProtection": "No",
  "TechSupport": "No",
  "StreamingTV": "Yes",
  "StreamingMovies": "Yes",
  "Contract": "Month-to-month",
  "PaperlessBilling": "Yes",
  "PaymentMethod": "Electronic check",
  "MonthlyCharges": 79.85,
  "TotalCharges": 957.2
}
Latest Model Performance
Latest training run:
Accuracy: 0.8235
Precision: 0.75
Recall: 0.50
F1 Score: 0.60

# Scheduled Execution
A GitHub Actions workflow is included to support scheduled daily pipeline execution and manual triggering.

# The workflow performs:
database initialization
live data ingestion
preprocessing
model training
drift detection
conditional retraining

# Notes
The system simulates live customer data using generated production-like records
SQLite is used for structured storage and monitoring
The focus is on pipeline design, deployment, automation, and reproducibility
Logs, metrics, and model versions are stored for traceability
The solution is Docker-ready and API-deployable