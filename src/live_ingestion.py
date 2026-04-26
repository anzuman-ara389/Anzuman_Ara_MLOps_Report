import random
import pandas as pd
from src.database import get_connection, initialize_database

try:
    from src.database import get_connection, initialize_database
except ModuleNotFoundError:
    from database import get_connection, initialize_database

def generate_customer():
    tenure = random.randint(1, 72)
    monthly = round(random.uniform(20, 120), 2)

    contract = random.choice(["Month-to-month", "One year", "Two year"])
    tech_support = random.choice(["Yes", "No", "No internet service"])
    internet = random.choice(["DSL", "Fiber optic", "No"])
    payment = random.choice([
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ])

    # Risk score for churn
    risk = 0

    if contract == "Month-to-month":
        risk += 3
    if tenure < 12:
        risk += 2
    if monthly > 80:
        risk += 2
    if tech_support == "No":
        risk += 1
    if internet == "Fiber optic":
        risk += 1
    if payment == "Electronic check":
        risk += 1

    churn = "Yes" if risk >= 5 else "No"

    return {
        "gender": random.choice(["Male", "Female"]),
        "SeniorCitizen": random.choice([0, 1]),
        "Partner": random.choice(["Yes", "No"]),
        "Dependents": random.choice(["Yes", "No"]),
        "tenure": tenure,
        "PhoneService": random.choice(["Yes", "No"]),
        "MultipleLines": random.choice(["Yes", "No", "No phone service"]),
        "InternetService": internet,
        "OnlineSecurity": random.choice(["Yes", "No", "No internet service"]),
        "OnlineBackup": random.choice(["Yes", "No", "No internet service"]),
        "DeviceProtection": random.choice(["Yes", "No", "No internet service"]),
        "TechSupport": tech_support,
        "StreamingTV": random.choice(["Yes", "No", "No internet service"]),
        "StreamingMovies": random.choice(["Yes", "No", "No internet service"]),
        "Contract": contract,
        "PaperlessBilling": random.choice(["Yes", "No"]),
        "PaymentMethod": payment,
        "MonthlyCharges": monthly,
        "TotalCharges": round(monthly * tenure, 2),
        "Churn": churn
    }


def ingest_live_data(rows=100):
    initialize_database()

    data = [generate_customer() for _ in range(rows)]

    df = pd.DataFrame(data)

    conn = get_connection()
    df.to_sql("raw_customers", conn, if_exists="append", index=False)
    conn.close()

    print(f"{rows} smart live customer records inserted successfully.")


if __name__ == "__main__":
    ingest_live_data()