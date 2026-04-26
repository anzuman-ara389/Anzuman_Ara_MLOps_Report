import sqlite3
import pandas as pd

DB_PATH = "data/churn_mlops.db"


def detect_drift():
    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql("SELECT * FROM raw_customers", conn)

    conn.close()

    if len(df) < 100:
        print("Not enough data for drift detection.")
        return

    # old historical = first 70%
    split_index = int(len(df) * 0.7)

    old_df = df.iloc[:split_index]
    new_df = df.iloc[split_index:]

    features = ["MonthlyCharges", "TotalCharges", "tenure"]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for feature in features:
        old_mean = old_df[feature].mean()
        new_mean = new_df[feature].mean()

        drift_score = abs(new_mean - old_mean) / max(old_mean, 1)

        status = "Drift Detected" if drift_score > 0.20 else "Stable"

        cursor.execute("""
            INSERT INTO drift_reports
            (feature_name, old_mean, new_mean, drift_score, status, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            feature,
            round(old_mean, 2),
            round(new_mean, 2),
            round(drift_score, 4),
            status
        ))

        print(f"{feature}: {status} | Score={round(drift_score,4)}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    detect_drift()