import streamlit as st 
import joblib
import numpy as np
import pyodbc
from datetime import datetime

# Load model and scaler
model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")

# SQL Server connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=.;'
    'DATABASE=Stroke;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

st.title("Stroke Prediction App")
st.write("Enter the following information to predict the risk of stroke:")

# Inputs
gender = st.selectbox("Gender", ["Male", "Female"])
age = st.slider("Age", 1, 100, 25)
hypertension = st.selectbox("Has hypertension?", ["No", "Yes"])
heart_disease = st.selectbox("Has heart disease?", ["No", "Yes"])
ever_married = st.selectbox("Ever married?", ["No", "Yes"])
work_type = st.selectbox("Work type", ["Private", "Self-employed", "Govt_job", "children", "Never_worked"])
residence_type = st.selectbox("Residence type", ["Urban", "Rural"])
avg_glucose_level = st.number_input("Average glucose level", min_value=50.0, max_value=300.0, value=100.0)
bmi = st.number_input("Body Mass Index (BMI)", min_value=10.0, max_value=50.0, value=25.0)
smoking_status = st.selectbox("Smoking status", ["never smoked", "formerly smoked", "smokes", "Unknown"])

# Mappings
gender_map = {"Male": 1, "Female": 0}
hypertension_map = {"No": 0, "Yes": 1}
heart_map = {"No": 0, "Yes": 1}
married_map = {"No": 0, "Yes": 1}
work_map = {"Private": 2, "Self-employed": 3, "Govt_job": 0, "children": 1, "Never_worked": 4}
residence_map = {"Urban": 1, "Rural": 0}
smoke_map = {"never smoked": 1, "formerly smoked": 0, "smokes": 2, "Unknown": -1}

input_data = np.array([[ 
    gender_map[gender],
    age,
    hypertension_map[hypertension],
    heart_map[heart_disease],
    married_map[ever_married],
    work_map[work_type],
    residence_map[residence_type],
    avg_glucose_level,
    bmi,
    smoke_map.get(smoking_status, -1)
]])

# Scale input
input_scaled = scaler.transform(input_data)

# Predict & Save to SQL
if st.button("Predict"):
    prediction = model.predict(input_scaled)[0]
    result = "At risk" if prediction == 1 else "Not at risk"

    # Show result
    if prediction == 1:
        st.error("⚠️ The person is at risk of stroke.")
    else:
        st.success("✅ The person is not at risk of stroke currently.")

    prediction_time = datetime.now()

    # Insert into SQL Server (make sure your table has 'prediction_time' column)
    insert_query = """
    INSERT INTO StrokePredictions (
        gender, age, hypertension, heart_disease, ever_married, work_type, 
        residence_type, avg_glucose_level, bmi, smoking_status, prediction, prediction_time
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = (
        gender_map[gender],
        age,
        hypertension_map[hypertension],
        heart_map[heart_disease],
        married_map[ever_married],
        work_map[work_type],
        residence_map[residence_type],
        avg_glucose_level,
        bmi,
        smoke_map.get(smoking_status, -1),
        result,
        prediction_time
    )
    cursor.execute(insert_query, values)
    conn.commit()
    cursor.close()
    conn.close()
