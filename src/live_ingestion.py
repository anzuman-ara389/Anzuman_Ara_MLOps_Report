import random
import os
import pandas as pd

try:
    from src.database import get_connection, initialize_database
except ModuleNotFoundError:
    from database import get_connection, initialize_database


# Generate realistic customer data
def generate_customer():
    tenure = random.randint(1, 72)
    monthly_charges = round(random.uniform(20, 120), 2)

    contract = random.choice(["Month-to-month", "One year", "Two year"])
    tech_support = random.choice(["Yes", "No", "No internet service"])
    internet_service = random.choice(["DSL", "Fiber optic", "No"])
    payment_method = random.choice([
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ])

    # CHURN LOGIC (IMPORTANT)
    churn_risk_score = 0

    if contract == "Month-to-month":
        churn_risk_score += 3
    if tenure < 12:
        churn_risk_score += 2
    if monthly_charges > 80:
        churn_risk_score += 2
    if tech_support == "No":
        churn_risk_score += 1
    if internet_service == "Fiber optic":
        churn_risk_score += 1
    if payment_method == "Electronic check":
        churn_risk_score += 1

    churn = "Yes" if churn_risk_score >= 5 else "No"

    return {
        "gender": random.choice(["Male", "Female"]),
        "SeniorCitizen": random.choice([0, 1]),
        "Partner": random.choice(["Yes", "No"]),
        "Dependents": random.choice(["Yes", "No"]),
        "tenure": tenure,
        "PhoneService": random.choice(["Yes", "No"]),
        "MultipleLines": random.choice(["Yes", "No", "No phone service"]),
        "InternetService": internet_service,
        "OnlineSecurity": random.choice(["Yes", "No", "No internet service"]),
        "OnlineBackup": random.choice(["Yes", "No", "No internet service"]),
        "DeviceProtection": random.choice(["Yes", "No", "No internet service"]),
        "TechSupport": tech_support,
        "StreamingTV": random.choice(["Yes", "No", "No internet service"]),
        "StreamingMovies": random.choice(["Yes", "No", "No internet service"]),
        "Contract": contract,
        "PaperlessBilling": random.choice(["Yes", "No"]),
        "PaymentMethod": payment_method,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": round(monthly_charges * tenure, 2),
        "Churn": churn,
        "source": "generated"
    }


# Insert generated data into database
def ingest_live_data(rows=100):
    initialize_database()

    customers = [generate_customer() for _ in range(rows)]
    df = pd.DataFrame(customers)

    conn = get_connection()
    df.to_sql("raw_customers", conn, if_exists="append", index=False)
    conn.close()

    os.makedirs("logs", exist_ok=True)

    with open("logs/ingestion.log", "a", encoding="utf-8") as f:
        f.write(f"{rows} generated customer records inserted\n")

    print(f"{rows} customer records inserted successfully.")


# Run manually
if __name__ == "__main__":
    ingest_live_data()