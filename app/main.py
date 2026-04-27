from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
import sqlite3
import subprocess
import os

from src.database import get_connection
from src.live_ingestion import ingest_live_data

app = FastAPI(title="Advanced Customer Churn MLOps API")

MODEL_PATH = "artifacts/model_latest.pkl"
COLUMNS_PATH = "artifacts/columns_latest.pkl"


def load_artifacts():
    model = joblib.load(MODEL_PATH)
    columns = joblib.load(COLUMNS_PATH)
    return model, columns


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


@app.get("/")
def home():
    return {"message": "MLOps API Running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/ingest-live")
def ingest_live(rows: int = 20):
    ingest_live_data(rows)
    return {"message": f"{rows} live records inserted"}


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
        SELECT model_version, accuracy, created_at
        FROM model_registry
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "model_version": row[0],
            "accuracy": row[1],
            "created_at": row[2]
        }

    return {"message": "No model found"}


@app.post("/predict")
def predict(data: CustomerInput):
    model, columns = load_artifacts()

    df = pd.DataFrame([data.model_dump()])

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.fillna(0)

    df["avg_monthly_value"] = df["MonthlyCharges"] / (df["tenure"] + 1)

    df = pd.get_dummies(df, drop_first=True)
    df = df.reindex(columns=columns, fill_value=0)

    pred = int(model.predict(df)[0])
    result = "Churn" if pred == 1 else "No Churn"

    if hasattr(model, "predict_proba"):
        proba = float(max(model.predict_proba(df)[0]))
    else:
        proba = None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prediction_logs
        (input_data, prediction, probability)
        VALUES (?, ?, ?)
    """, (str(data.model_dump()), result, proba))

    conn.commit()
    conn.close()

    os.makedirs("logs", exist_ok=True)

    with open("logs/prediction.log", "a", encoding="utf-8") as f:
        f.write(f"Prediction={result}, Probability={proba}\n")

    return {
        "prediction": result,
        "probability": proba
    }