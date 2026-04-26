import pandas as pd
from src.database import get_connection

def preprocess_data():
    conn = get_connection()

    df = pd.read_sql("SELECT * FROM raw_customers", conn)
    conn.close()

    df = df.drop(columns=["id", "created_at"], errors="ignore")

    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    df = df.fillna(0)

    df["avg_monthly_value"] = df["MonthlyCharges"] / (df["tenure"] + 1)

    df = pd.get_dummies(df, drop_first=True)

    df.to_csv("data/processed_data.csv", index=False)

    print("Preprocessing complete.")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])

if __name__ == "__main__":
    preprocess_data()