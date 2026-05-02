from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import sqlite3
import subprocess

from src.database import get_connection, initialize_database
from src.live_ingestion import ingest_live_data

app = FastAPI(title="AI-Powered Customer Retention System API")

MODEL_PATH = "artifacts/model_latest.pkl"
COLUMNS_PATH = "artifacts/columns_latest.pkl"


class CustomerInput(BaseModel):
    gender: str
    SeniorCitizen: int
    Partner: str
    Dependents: str
    tenure: int
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float
    TotalCharges: float


def load_model():
    model = joblib.load(MODEL_PATH)
    columns = joblib.load(COLUMNS_PATH)
    return model, columns


@app.get("/")
def home():
    return {"message": "Customer Retention System API Running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ingest-live")
def ingest_live(rows: int = 20):
    ingest_live_data(rows)
    return {"message": f"{rows} generated records inserted"}


@app.post("/customer-event")
def add_customer_event(data: CustomerInput):
    initialize_database()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO raw_customers (
            gender, SeniorCitizen, Partner, Dependents, tenure,
            PhoneService, MultipleLines, InternetService,
            OnlineSecurity, OnlineBackup, DeviceProtection, TechSupport,
            StreamingTV, StreamingMovies, Contract,
            PaperlessBilling, PaymentMethod,
            MonthlyCharges, TotalCharges, Churn, source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.gender,
        data.SeniorCitizen,
        data.Partner,
        data.Dependents,
        data.tenure,
        data.PhoneService,
        data.MultipleLines,
        data.InternetService,
        data.OnlineSecurity,
        data.OnlineBackup,
        data.DeviceProtection,
        data.TechSupport,
        data.StreamingTV,
        data.StreamingMovies,
        data.Contract,
        data.PaperlessBilling,
        data.PaymentMethod,
        data.MonthlyCharges,
        data.TotalCharges,
        "Unknown",
        "api_post"
    ))

    conn.commit()
    conn.close()

    return {
        "message": "Customer data received via API and stored in database",
        "flow": "API → DB"
    }


@app.get("/latest-customers")
def latest_customers():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, gender, tenure, Contract, MonthlyCharges, source, created_at
        FROM raw_customers
        ORDER BY id DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    conn.close()

    return {"latest_customers": rows}


@app.post("/predict")
def predict(data: CustomerInput):
    model, columns = load_model()

    df = pd.DataFrame([data.model_dump()])

    df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.fillna(0)

    df["avg_monthly_value"] = df["MonthlyCharges"] / (df["tenure"] + 1)

    df = pd.get_dummies(df, drop_first=True)
    df = df.reindex(columns=columns, fill_value=0)

    pred = int(model.predict(df)[0])
    prediction = "Churn" if pred == 1 else "No Churn"

    if hasattr(model, "predict_proba"):
        probability = float(max(model.predict_proba(df)[0]))
    else:
        probability = 0.0

    # Business rule:
    # If model predicts Churn, at least Medium retention action is required.
    if prediction == "Churn":
        if probability >= 0.75:
            risk_level = "High"
        else:
            risk_level = "Medium"
    else:
        risk_level = "Low"

    if risk_level == "High":
        revenue_at_risk = round(data.MonthlyCharges * 6, 2)
    elif risk_level == "Medium":
        revenue_at_risk = round(data.MonthlyCharges * 3, 2)
    else:
        revenue_at_risk = 0

    if risk_level == "High":
        recommended_action = "Priority retention call with discount offer"
    elif risk_level == "Medium":
        recommended_action = "Send targeted promotional offer and follow-up"
    else:
        recommended_action = "No immediate retention action required"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prediction_logs
        (input_data, prediction, probability, risk_level, revenue_at_risk, recommended_action)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        str(data.model_dump()),
        prediction,
        probability,
        risk_level,
        revenue_at_risk,
        recommended_action
    ))

    conn.commit()
    conn.close()

    return {
        "prediction": prediction,
        "probability": probability,
        "risk_level": risk_level,
        "revenue_at_risk": revenue_at_risk,
        "recommended_action": recommended_action
    }


@app.post("/drift-check")
def drift_check():
    subprocess.run(["python", "-m", "src.drift_detection"])
    return {"message": "Drift detection completed"}


@app.post("/retrain")
def retrain():
    subprocess.run(["python", "-m", "src.preprocess"])
    subprocess.run(["python", "-m", "src.train"])
    return {"message": "Model retrained successfully"}


@app.get("/model-info")
def model_info():
    conn = sqlite3.connect("data/churn_mlops.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT model_version, accuracy, precision, recall, f1_score, created_at
        FROM model_registry
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    return {"model_info": row}