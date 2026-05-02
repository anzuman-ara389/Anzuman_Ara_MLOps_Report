import pandas as pd

try:
    from src.database import get_connection, initialize_database
except ModuleNotFoundError:
    from database import get_connection, initialize_database


def preprocess_data():
    initialize_database()

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM raw_customers", conn)
    conn.close()

    if df.empty:
        raise ValueError("No raw customer data found. Please run ingestion first.")

    # Remove technical database columns
    df = df.drop(columns=["id", "created_at", "source"], errors="ignore")

    # Keep only labelled rows for training
    df = df[df["Churn"].isin(["Yes", "No"])]

    if df.empty:
        raise ValueError("No labelled customer data found for training.")

    # Target encoding
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})

    # Numeric conversion
    numeric_columns = ["tenure", "MonthlyCharges", "TotalCharges"]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
        df[column] = df[column].fillna(df[column].median())

    # Handle missing categorical values
    categorical_columns = df.select_dtypes(include=["object"]).columns

    for column in categorical_columns:
        df[column] = df[column].fillna("Unknown")

    # Feature engineering
    df["avg_monthly_value"] = df["MonthlyCharges"] / (df["tenure"] + 1)
    df["high_monthly_charge"] = (df["MonthlyCharges"] > 80).astype(int)
    df["short_tenure"] = (df["tenure"] < 12).astype(int)
    df["estimated_customer_value"] = df["MonthlyCharges"] * df["tenure"]

    # One-hot encoding
    df = pd.get_dummies(df, drop_first=True)

    df.to_csv("data/processed_data.csv", index=False)

    print("Preprocessing completed successfully.")
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])
    print("Engineered features:")
    print("- avg_monthly_value")
    print("- high_monthly_charge")
    print("- short_tenure")
    print("- estimated_customer_value")


if __name__ == "__main__":
    preprocess_data()