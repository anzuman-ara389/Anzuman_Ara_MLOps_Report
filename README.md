# M6 – Data Engineering and Machine Learning Operations in Business
# AI-Powered Customer Retention System for Telecom Subscription Services
Submitted by: Anzuman Ara
Student ID: 20241266


# Project Overview:
This project implements a production-oriented end-to-end MLOps pipeline for a customer retention system in telecom services.

The main goal of the system is not only to predict customer churn but to support business decision-making by identifying high-risk customers and recommending retention actions.

The system is designed to simulate a real-world production environment where customer data continuously arrives, gets processed, used for prediction, monitored for drift, and retrained when necessary.

FastAPI is used to deploy the model as a real-time API, Streamlit is used for interactive frontend visualization, and SQLite is used as a lightweight database to store data, predictions, drift reports, and model versions.


# Pipeline Structure:
The pipeline consists of the following components:

1. Live Data Ingestion
New customer records are generated using rule-based logic to simulate realistic churn behavior.
Unlike random data, churn is influenced by factors such as contract type, tenure, and monthly charges.

Data ingestion can be triggered in three ways:
- Manual execution using Python script
- API endpoint (/customer-event and /ingest-live)
- Scheduled GitHub Actions workflow

All incoming records are stored in the raw_customers table.


2. Database Layer
SQLite is used as the main storage system to ensure structured data management and reproducibility.

Tables used:
- raw_customers (incoming customer data)
- prediction_logs (predictions and business outputs)
- drift_reports (data drift monitoring)
- model_registry (model versions and metrics)

This enables tracking, monitoring, and version control of the pipeline.


3. Preprocessing
The pipeline reads raw data from the database and performs:

- handling missing values (median for numeric, default for categorical)
- numeric conversion for consistency
- categorical encoding using one-hot encoding
- target transformation for model training

The processed dataset is saved as:
data/processed_data.csv


4. Feature Engineering
To improve model performance, additional features are created:

- avg_monthly_value = MonthlyCharges / tenure
- high_monthly_charge = customers with high billing
- short_tenure = customers with low subscription duration
- estimated_customer_value = MonthlyCharges × tenure

These features help capture customer behavior and improve churn prediction.


5. Model Training
A Random Forest Classifier is used because it performs well on structured tabular data and handles non-linear relationships effectively.

Training steps:
- load processed data
- split into training and testing sets
- train the model
- evaluate performance using multiple metrics

Evaluation metrics:
- Accuracy
- Precision
- Recall
- F1-score

Model artifacts are saved for reproducibility.


6. Model Versioning and Artifacts
Each training run generates versioned artifacts:

- artifacts/model_YYYYMMDD_HHMMSS.pkl
- artifacts/model_latest.pkl
- artifacts/columns_latest.pkl
- artifacts/metrics_latest.json

This allows tracking model changes and supports rollback if needed.


7. Deployment (API Layer)
The trained model is deployed using FastAPI to simulate a production system.

Available endpoints:
- /health
- /predict
- /customer-event
- /ingest-live
- /drift-check
- /retrain
- /model-info

The API enables real-time interaction with the model.


8. Prediction and Business Logic
The system goes beyond simple prediction by converting outputs into business decisions.

For each prediction, the system returns:
- churn prediction (Yes/No)
- probability score
- risk level (High / Medium / Low)
- estimated revenue at risk
- recommended retention action

Example:
Churn → Medium Risk → Send promotional offer
Churn → High Risk → Offer discount and call customer

This makes the system useful for real business applications.


9. Monitoring
The system tracks prediction results and incoming data patterns.

Prediction logs are stored in the database to analyze model behavior over time.


10. Drift Detection
Data drift is detected by comparing historical and recent data distributions.

Monitored features:
- MonthlyCharges
- TotalCharges
- tenure

Drift is detected if:
drift_score > 0.20

This ensures the model remains reliable over time.


11. Conditional Retraining
The system automatically decides whether retraining is required.

If drift is detected:
Preprocess → Train → Save new model

If no drift is detected:
Retraining is skipped

This optimizes performance and reduces unnecessary computation.


12. Automation (GitHub Actions)
A GitHub Actions workflow is implemented to simulate scheduled execution.

The pipeline runs automatically and performs:
- data ingestion
- preprocessing
- model training
- drift detection
- conditional retraining
- automatic commit and push of updated artifacts

This demonstrates continuous integration and automation.


13. Frontend Dashboard
A Streamlit dashboard is developed to provide a user-friendly interface.

Features include:
- API health check
- live data ingestion trigger
- drift detection trigger
- retraining trigger
- customer input form
- prediction display with risk and recommended action
- model performance metrics

This enables non-technical users to interact with the system.


# Project Structure:
customer-retention-mlops
├── app/                    # FastAPI application
├── src/                    # pipeline scripts
├── data/                   # database and processed data
├── artifacts/              # model and metrics
├── logs/                   # logs
├── frontend.py             # Streamlit dashboard
├── Dockerfile              # container setup
├── requirements.txt
├── .github/workflows       # automation pipeline
└── README.md


# How to Run (Without Docker)
pip install -r requirements.txt
python src/database.py
python src/live_ingestion.py
python src/preprocess.py
python src/train.py
uvicorn app.main:app --reload
streamlit run frontend.py


# How to Run (With Docker)
docker build -t retention-system .
docker run -p 8000:8000 retention-system


# API Usage
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


# Latest Model Performance
Accuracy: ~0.92
Precision: ~0.88
Recall: ~0.71
F1 Score: ~0.78


# Notes
- The system simulates production-like data ingestion
- The focus is on pipeline design, automation, and deployment
- Model performance is secondary to system functionality
- The system is fully reproducible, automated, and deployment-ready