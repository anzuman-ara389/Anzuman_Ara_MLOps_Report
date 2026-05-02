import sqlite3
import subprocess
import sys

DB_PATH = "data/churn_mlops.db"


def auto_retrain():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status
        FROM drift_reports
        ORDER BY id DESC
        LIMIT 3
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No drift report found. Please run drift detection first.")
        return

    drift_found = any(row[0] == "Drift Detected" for row in rows)

    if drift_found:
        print("Drift detected. Starting automatic retraining...")

        subprocess.run([sys.executable, "-m", "src.preprocess"], check=True)
        subprocess.run([sys.executable, "-m", "src.train"], check=True)

        print("Automatic retraining completed successfully.")
    else:
        print("No drift detected. Retraining skipped.")


if __name__ == "__main__":
    auto_retrain()