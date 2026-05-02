import requests
import streamlit as st
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Customer Retention System",
    page_icon="📊",
    layout="wide"
)

st.title("AI-Powered Customer Retention System")
st.write("Telecom customer churn prediction, retention recommendation, monitoring, and retraining dashboard.")


# SIDEBAR: SYSTEM CONTROLS
st.sidebar.header("System Controls")

if st.sidebar.button("Check API Health"):
    try:
        response = requests.get(f"{API_URL}/health")
        st.sidebar.success(response.json())
    except Exception as e:
        st.sidebar.error(f"API connection failed: {e}")

rows = st.sidebar.number_input("Rows to ingest", min_value=1, max_value=500, value=20)

if st.sidebar.button("Ingest Live Data"):
    try:
        response = requests.post(f"{API_URL}/ingest-live", params={"rows": rows})
        st.sidebar.success(response.json())
    except Exception as e:
        st.sidebar.error(f"Ingestion failed: {e}")

if st.sidebar.button("Run Drift Check"):
    try:
        response = requests.post(f"{API_URL}/drift-check")
        st.sidebar.success(response.json())
    except Exception as e:
        st.sidebar.error(f"Drift check failed: {e}")

if st.sidebar.button("Retrain Model"):
    try:
        response = requests.post(f"{API_URL}/retrain")
        st.sidebar.success(response.json())
    except Exception as e:
        st.sidebar.error(f"Retraining failed: {e}")


# MODEL INFO
st.subheader("Latest Model Information")

try:
    response = requests.get(f"{API_URL}/model-info")
    model_info = response.json().get("model_info")

    if model_info:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Accuracy", model_info[1])
        col2.metric("Precision", model_info[2])
        col3.metric("Recall", model_info[3])
        col4.metric("F1 Score", model_info[4])

        st.caption(f"Model version: {model_info[0]} | Created at: {model_info[5]}")
    else:
        st.warning("No model information found.")
except Exception as e:
    st.error(f"Could not load model info: {e}")


# MAIN LAYOUT
tab1, tab2, tab3 = st.tabs([
    "Customer Prediction",
    "Latest Customers",
    "System Flow"
])


# TAB 1: PREDICTION
with tab1:
    st.subheader("Customer Churn Prediction")

    col1, col2, col3 = st.columns(3)

    with col1:
        gender = st.selectbox("Gender", ["Female", "Male"])
        SeniorCitizen = st.selectbox("Senior Citizen", [0, 1])
        Partner = st.selectbox("Partner", ["Yes", "No"])
        Dependents = st.selectbox("Dependents", ["Yes", "No"])
        tenure = st.slider("Tenure", 1, 72, 12)
        PhoneService = st.selectbox("Phone Service", ["Yes", "No"])

    with col2:
        MultipleLines = st.selectbox("Multiple Lines", ["No", "Yes", "No phone service"])
        InternetService = st.selectbox("Internet Service", ["DSL", "Fiber optic", "No"])
        OnlineSecurity = st.selectbox("Online Security", ["No", "Yes", "No internet service"])
        OnlineBackup = st.selectbox("Online Backup", ["Yes", "No", "No internet service"])
        DeviceProtection = st.selectbox("Device Protection", ["No", "Yes", "No internet service"])
        TechSupport = st.selectbox("Tech Support", ["No", "Yes", "No internet service"])

    with col3:
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
        MonthlyCharges = st.number_input("Monthly Charges", min_value=0.0, value=89.5)
        TotalCharges = st.number_input("Total Charges", min_value=0.0, value=447.5)

    customer_data = {
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

    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("Save Customer Event to API"):
            try:
                response = requests.post(f"{API_URL}/customer-event", json=customer_data)
                st.success(response.json())
            except Exception as e:
                st.error(f"Customer event failed: {e}")

    with col_b:
        if st.button("Predict Retention Risk"):
            try:
                response = requests.post(f"{API_URL}/predict", json=customer_data)
                result = response.json()

                st.success("Prediction completed")

                r1, r2, r3 = st.columns(3)
                r1.metric("Prediction", result["prediction"])
                r2.metric("Probability", round(result["probability"], 4))
                r3.metric("Risk Level", result["risk_level"])

                st.metric("Revenue at Risk", result["revenue_at_risk"])
                st.info(f"Recommended Action: {result['recommended_action']}")

            except Exception as e:
                st.error(f"Prediction failed: {e}")


# TAB 2: LATEST CUSTOMERS
with tab2:
    st.subheader("Latest Customers from Database")

    if st.button("Refresh Latest Customers"):
        try:
            response = requests.get(f"{API_URL}/latest-customers")
            data = response.json()["latest_customers"]

            if data:
                df = pd.DataFrame(
                    data,
                    columns=[
                        "ID",
                        "Gender",
                        "Tenure",
                        "Contract",
                        "Monthly Charges",
                        "Source",
                        "Created At"
                    ]
                )
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No customer records found.")

        except Exception as e:
            st.error(f"Could not load latest customers: {e}")


# TAB 3: SYSTEM FLOW
with tab3:
    st.subheader("Production-like Flow")

    st.markdown("""
    **System flow:**

    1. New telecom customer data is generated or posted through the API.
    2. Customer records are stored in the `raw_customers` database table.
    3. Preprocessing converts numeric values, handles missing values, and encodes categorical features.
    4. Feature engineering creates customer value and churn-related features.
    5. The trained model predicts churn risk.
    6. The system returns prediction, probability, risk level, revenue at risk, and recommended retention action.
    7. Drift detection monitors incoming data.
    8. Retraining can be triggered when drift is detected.
    """)