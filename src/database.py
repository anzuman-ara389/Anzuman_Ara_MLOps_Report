import sqlite3
from pathlib import Path

DB_PATH = "data/churn_mlops.db"


def get_connection():
    Path("data").mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()


    # 1. RAW CUSTOMER DATA
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gender TEXT,
        SeniorCitizen INTEGER,
        Partner TEXT,
        Dependents TEXT,
        tenure INTEGER,
        PhoneService TEXT,
        MultipleLines TEXT,
        InternetService TEXT,
        OnlineSecurity TEXT,
        OnlineBackup TEXT,
        DeviceProtection TEXT,
        TechSupport TEXT,
        StreamingTV TEXT,
        StreamingMovies TEXT,
        Contract TEXT,
        PaperlessBilling TEXT,
        PaymentMethod TEXT,
        MonthlyCharges REAL,
        TotalCharges REAL,
        Churn TEXT,
        source TEXT DEFAULT 'generated',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

   
    # 2. PREDICTION LOGS (BUSINESS OUTPUT)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        input_data TEXT,
        prediction TEXT,
        probability REAL,
        risk_level TEXT,
        revenue_at_risk REAL,
        recommended_action TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)


    # 3. DRIFT REPORTS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drift_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature_name TEXT,
        old_mean REAL,
        new_mean REAL,
        drift_score REAL,
        status TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 4. MODEL REGISTRY
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_version TEXT,
        accuracy REAL,
        precision REAL,
        recall REAL,
        f1_score REAL,
        model_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")