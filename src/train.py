import pandas as pd
import joblib
import json
import sqlite3
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


DB_PATH = "data/churn_mlops.db"


def save_model_registry(version, metrics, model_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO model_registry
        (model_version, accuracy, created_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
    """, (version, metrics["accuracy"]))

    conn.commit()
    conn.close()


def train_model():
    df = pd.read_csv("data/processed_data.csv")

    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    metrics = {
        "accuracy": round(accuracy_score(y_test, preds), 4),
        "precision": round(precision_score(y_test, preds), 4),
        "recall": round(recall_score(y_test, preds), 4),
        "f1_score": round(f1_score(y_test, preds), 4)
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version = f"model_{timestamp}"

    model_path = f"artifacts/{version}.pkl"
    latest_model = "artifacts/model_latest.pkl"

    columns_path = f"artifacts/columns_{timestamp}.pkl"
    latest_columns = "artifacts/columns_latest.pkl"

    metrics_path = f"artifacts/metrics_{timestamp}.json"
    latest_metrics = "artifacts/metrics_latest.json"

    joblib.dump(model, model_path)
    joblib.dump(model, latest_model)

    joblib.dump(list(X.columns), columns_path)
    joblib.dump(list(X.columns), latest_columns)

    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    with open(latest_metrics, "w") as f:
        json.dump(metrics, f, indent=4)

    save_model_registry(version, metrics, model_path)

    print("Training complete.")
    print(metrics)
    print("Model saved:", model_path)
    print("Registry updated.")


if __name__ == "__main__":
    train_model()