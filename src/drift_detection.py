import sqlite3
import pandas as pd

DB_PATH = "data/churn_mlops.db"


def detect_drift():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM raw_customers", conn)
    conn.close()

    if df.empty:
        print("No customer data available for drift detection.")
        return

    if len(df) < 100:
        print("Not enough data for drift detection. Minimum 100 rows required.")
        return

    numeric_features = ["MonthlyCharges", "TotalCharges", "tenure"]

    for feature in numeric_features:
        df[feature] = pd.to_numeric(df[feature], errors="coerce")

    df = df.dropna(subset=numeric_features)

    split_index = int(len(df) * 0.7)

    old_df = df.iloc[:split_index]
    new_df = df.iloc[split_index:]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Drift Detection Report")
    print("----------------------")

    for feature in numeric_features:
        old_mean = old_df[feature].mean()
        new_mean = new_df[feature].mean()

        drift_score = abs(new_mean - old_mean) / max(abs(old_mean), 1)

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

        print(
            f"{feature}: old_mean={round(old_mean, 2)}, "
            f"new_mean={round(new_mean, 2)}, "
            f"drift_score={round(drift_score, 4)}, "
            f"status={status}"
        )

    conn.commit()
    conn.close()

    print("Drift detection completed and saved to database.")


if __name__ == "__main__":
    detect_drift()