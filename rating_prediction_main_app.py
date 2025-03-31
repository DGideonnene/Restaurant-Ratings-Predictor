import numpy as np
import pandas as pd
import joblib
import streamlit as st
import os
import hashlib

st.set_page_config(page_title="Restaurant Ratings Predictor", layout="wide")

# Load Model
try:
    model = joblib.load("Rating_Predictions_rv3.pkl")
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# Display the uploaded image
image_path = "Front_page.jpg"
if os.path.exists(image_path):
    st.image(image_path, caption="Restaurant Ratings Prediction", use_container_width=True)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate_user(email, password):
    auth_file = "user_auth.csv"
    if os.path.exists(auth_file):
        try:
            df = pd.read_csv(auth_file, on_bad_lines='skip')
            hashed_pw = hash_password(password)
            if 'Email' in df.columns and 'Password' in df.columns:
                if ((df['Email'] == email) & (df['Password'] == hashed_pw)).any():
                    return True
        except pd.errors.ParserError:
            st.error("Corrupted user authentication file. Please reset.")
    return False

def register_user(email, password):
    auth_file = "user_auth.csv"
    hashed_pw = hash_password(password)
    new_user = pd.DataFrame([[email, hashed_pw]], columns=['Email', 'Password'])
    if os.path.exists(auth_file):
        try:
            existing_df = pd.read_csv(auth_file, on_bad_lines='skip')
            if 'Email' in existing_df.columns and (existing_df['Email'] == email).any():
                return False
            existing_df = pd.concat([existing_df, new_user], ignore_index=True)
            existing_df.to_csv(auth_file, index=False)
        except pd.errors.ParserError:
            st.error("Corrupted user authentication file. Please reset.")
    else:
        new_user.to_csv(auth_file, index=False)
    return True

def performance_prediction(input_data):
    column_names = ['City', 'Longitude', 'Latitude', 'Cuisines', 'Average Cost for two',
                    'Has Table booking', 'Has Online delivery', 'Is delivering now',
                    'Switch to order menu', 'Price range', 'Rating color', 'Rating text',
                    'Votes', 'Area']
    
    input_df = pd.DataFrame([input_data], columns=column_names)
    try:
        pred = model.predict(input_df)
        prediction_original = np.expm1(pred[0])
        prediction = round(prediction_original, 2)
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return "Error", None

    rating_category = "Not rated" if prediction == 0.0 else (
        "Excellent" if prediction >= 4.5 else
        "Very Good" if 4.0 <= prediction < 4.5 else
        "Good" if 3.5 <= prediction < 4.0 else
        "Average" if 2.5 <= prediction < 3.5 else
        "Poor"
    )

    return rating_category, prediction

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    
    st.sidebar.subheader("🔐 Login or Register")
    auth_choice = st.sidebar.radio("Select an option", ["Login", "Register"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    if auth_choice == "Register" and st.sidebar.button("Register"):
        if register_user(email, password):
            st.sidebar.success("✅ Registration successful! Please log in.")
        else:
            st.sidebar.error("⚠️ User already exists!")
    
    if auth_choice == "Login" and st.sidebar.button("Login"):
        if authenticate_user(email, password):
            st.sidebar.success("✅ Login successful!")
            st.session_state.logged_in = True
            st.session_state.user_email = email
        else:
            st.sidebar.error("⚠️ Invalid credentials!")
    
    if st.session_state.logged_in:
        st.title("🍽️ Restaurant Ratings Predictor")
        st.write("Enter details about a restaurant to predict its rating.")
        
        st.subheader("🏢 Restaurant Details")
        col1, col2, col3 = st.columns(3)
        inputs = []
        
        fields = [
            ('City', 'text'), ('Longitude', 'number'), ('Latitude', 'number'),
            ('Cuisines', 'text'), ('Average Cost for two', 'number'),
            ('Has Table booking', 'yes_no'), ('Has Online delivery', 'yes_no'),
            ('Is delivering now', 'yes_no'), ('Switch to order menu', 'yes_no'),
            ('Price range', 'number'), ('Rating color', 'text'),
            ('Rating text', 'text'), ('Votes', 'number'), ('Area', 'text')
        ]
        
        for i, (field, input_type) in enumerate(fields):
            with [col1, col2, col3][i % 3]:
                if input_type == 'number':
                    value = st.number_input(field, key=field)
                elif input_type == 'yes_no':
                    value = st.radio(field, options=[1, 0], horizontal=True, key=field)
                else:
                    value = st.text_input(field, key=field)
                inputs.append(value)
        
        if st.button("🔍 Predict Rating"):
            if any(str(val).strip() == "" for val in inputs):
                st.warning("⚠️ Please fill in all fields with valid values.")
            else:
                rating_category, prediction_value = performance_prediction(inputs)
                if prediction_value is not None:
                    st.subheader("📊 Prediction Result:")
                    st.write(f"🏆 Predicted Rating: **{rating_category}** ({prediction_value})")
                else:
                    st.warning("⚠️ Unable to generate a valid prediction.")

if __name__ == '__main__':
    main()
