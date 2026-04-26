import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Customer Churn MLOps Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Customer Churn MLOps Dashboard")
st.write("Live ingestion, prediction, drift monitoring, and model information dashboard.")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Check API Health"):
        response = requests.get(f"{API_URL}/health")
        st.success(response.json())

with col2:
    if st.button("Ingest Live Data"):
        response = requests.post(f"{API_URL}/ingest-live?rows=20")
        st.success(response.json())

with col3:
    if st.button("Run Drift Check"):
        response = requests.post(f"{API_URL}/drift-check")
        st.success(response.json())

st.divider()

st.subheader("Latest Model Information")

try:
    model_info = requests.get(f"{API_URL}/model-info").json()
    st.json(model_info)
except Exception as e:
    st.error(f"Could not fetch model information. Make sure FastAPI is running. Error: {e}")

st.divider()

st.subheader("Customer Churn Prediction")

gender = st.selectbox("Gender", ["Male", "Female"])
SeniorCitizen = st.selectbox("Senior Citizen", [0, 1])
Partner = st.selectbox("Partner", ["Yes", "No"])
Dependents = st.selectbox("Dependents", ["Yes", "No"])
tenure = st.number_input("Tenure", min_value=1, max_value=72, value=5)

PhoneService = st.selectbox("Phone Service", ["Yes", "No"])
MultipleLines = st.selectbox("Multiple Lines", ["Yes", "No", "No phone service"])
InternetService = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
OnlineSecurity = st.selectbox("Online Security", ["Yes", "No", "No internet service"])
OnlineBackup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
DeviceProtection = st.selectbox("Device Protection", ["Yes", "No", "No internet service"])
TechSupport = st.selectbox("Tech Support", ["Yes", "No", "No internet service"])
StreamingTV = st.selectbox("Streaming TV", ["Yes", "No", "No internet service"])
StreamingMovies = st.selectbox("Streaming Movies", ["Yes", "No", "No internet service"])
Contract = st.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
PaperlessBilling = st.selectbox("Paperless Billing", ["Yes", "No"])

PaymentMethod = st.selectbox(
    "Payment Method",
    [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)"
    ]
)

MonthlyCharges = st.number_input("Monthly Charges", min_value=0.0, value=95.5)
TotalCharges = st.number_input("Total Charges", min_value=0.0, value=477.5)

payload = {
    "gender": gender,
    "SeniorCitizen": SeniorCitizen,
    "Partner": Partner,
    "Dependents": Dependents,
    "tenure": tenure,
    "PhoneService": PhoneService,
    "MultipleLines": MultipleLines,
    "InternetService": InternetService,
    "OnlineSecurity": OnlineSecurity,
    "OnlineBackup": OnlineBackup,
    "DeviceProtection": DeviceProtection,
    "TechSupport": TechSupport,
    "StreamingTV": StreamingTV,
    "StreamingMovies": StreamingMovies,
    "Contract": Contract,
    "PaperlessBilling": PaperlessBilling,
    "PaymentMethod": PaymentMethod,
    "MonthlyCharges": MonthlyCharges,
    "TotalCharges": TotalCharges
}

if st.button("Predict Churn"):
    response = requests.post(f"{API_URL}/predict", json=payload)

    if response.status_code == 200:
        result = response.json()

        if result["prediction"] == "Churn":
            st.error(f"Prediction: {result['prediction']}")
        else:
            st.success(f"Prediction: {result['prediction']}")

        st.write("Prediction probability:", result["probability"])
    else:
        st.error(response.text)