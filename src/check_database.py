from src.database import get_connection, initialize_database

def check_database():
    initialize_database()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM raw_customers")
    raw_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM prediction_logs")
    prediction_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM drift_reports")
    drift_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM model_registry")
    model_count = cursor.fetchone()[0]

    conn.close()

    print("Database Status")
    print("----------------")
    print(f"Raw customer records: {raw_count}")
    print(f"Prediction logs: {prediction_count}")
    print(f"Drift reports: {drift_count}")
    print(f"Model versions: {model_count}")

if __name__ == "__main__":
    check_database()