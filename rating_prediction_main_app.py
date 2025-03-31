import numpy as np
import pandas as pd
import joblib
import streamlit as st
import os
import hashlib

# Ensure set_page_config is the first Streamlit command
st.set_page_config(page_title="Restaurant Ratings Predictor", layout="wide")

# Load Model with compatibility options
try:
    model = joblib.load("C:/Users/chiom/Documents/Axia Africa Store/web scraping/Capstone Project/Rating_Predictions_rv3.pkl")

except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

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
        return "Error"
    
    if prediction >= 4.5:
        return "Excellent"
    elif 4.0 <= prediction < 4.5:
        return "Very Good"
    elif 3.5 <= prediction < 4.0:
        return "Good"
    elif 2.5 <= prediction < 3.5:
        return "Average"
    elif 1.0 <= prediction < 2.5:
        return "Poor"
    elif prediction == 0.0:
        return "Not rated"
    else:
        return "Invalid rating"

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_email' not in st.session_state:
        st.session_state.user_email = ""
    
    st.sidebar.subheader("🔐 Login or Register")
    auth_choice = st.sidebar.radio("Select an option", ["Login", "Register"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    if auth_choice == "Register":
        if st.sidebar.button("Register"):
            if register_user(email, password):
                st.sidebar.success("✅ Registration successful! Please log in.")
            else:
                st.sidebar.error("⚠️ User already exists!")
    
    if auth_choice == "Login":
        if st.sidebar.button("Login"):
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
        fields = ['City', 'Longitude', 'Latitude', 'Cuisines', 'Average Cost for two',
                  'Has Table booking', 'Has Online delivery', 'Is delivering now',
                  'Switch to order menu', 'Price range', 'Rating color', 'Rating text',
                  'Votes', 'Area']
        
        for i, field in enumerate(fields):
            with [col1, col2, col3][i % 3]:
                value = st.text_input(f"{field.replace('_', ' ')}", key=field)
                inputs.append(value)
        
        if st.button("🔍 Predict Rating"):
            if "" in inputs:
                st.warning("⚠️ Please fill in all fields with valid values.")
            else:
                try:
                    prediction = performance_prediction(inputs)
                    st.subheader("📊 Prediction Result:")
                    st.write(f"🏆 Predicted Rating: **{prediction}**")
                except ValueError:
                    st.warning("⚠️ Please enter valid values in all fields.")

if __name__ == '__main__':
    main()
