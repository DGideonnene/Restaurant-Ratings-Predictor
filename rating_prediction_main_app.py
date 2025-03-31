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

    if prediction >= 4.5:
        rating_category = "Excellent"
    elif 4.0 <= prediction < 4.5:
        rating_category = "Very Good"
    elif 3.5 <= prediction < 4.0:
        rating_category = "Good"
    elif 2.5 <= prediction < 3.5:
        rating_category = "Average"
    elif 1.0 <= prediction < 2.5:
        rating_category = "Poor"
    elif prediction == 0.0:
        rating_category = "Not rated"
    else:
        rating_category = "Invalid rating"

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
        st.image("front_pic.jpg", use_container_width=True)
        st.title("🍽️ Restaurant Ratings Predictor")
        st.write("Enter details about a restaurant to predict its rating.")
        
        st.subheader("🏢 Restaurant Details")
        col1, col2, col3 = st.columns(3)
        inputs = []
        fields = [
            ('City', 'e.g., New York'), 
            ('Longitude', 'e.g., -74.0060'), 
            ('Latitude', 'e.g., 40.7128'),
            ('Cuisines', 'e.g., Italian, Chinese'), 
            ('Average Cost for two', 'e.g., 50'), 
            ('Has Table booking', '1(Yes) or 2(No)'),
            ('Has Online delivery', '1(Yes) or 2(No)'), 
            ('Is delivering now', '1(Yes) or 2(No)'),
            ('Switch to order menu', '1(Yes) or 2(No)'), 
            ('Price range', '1 to 4'), 
            ('Rating color', 'Red, Orange, etc.'),
            ('Rating text', 'Excellent, Good, etc.'), 
            ('Votes', 'e.g., 500'), 
            ('Area', 'e.g., Manhattan')
        ]
        
        for i, (field, placeholder) in enumerate(fields):
            with [col1, col2, col3][i % 3]:
                value = st.text_input(f"{field.replace('_', ' ')}", placeholder=placeholder, key=field)
                inputs.append(value)
        
        if st.button("🔍 Predict Rating"):
            if "" in inputs:
                st.warning("⚠️ Please fill in all fields with valid values.")
            else:
                try:
                    rating_category, prediction_value = performance_prediction(inputs)
                    if prediction_value is not None:
                        st.subheader("📊 Prediction Result:")
                        st.write(f"🏆 Predicted Rating: **{rating_category}** ({prediction_value})")
                    else:
                        st.warning("⚠️ Unable to generate a valid prediction.")
                except ValueError:
                    st.warning("⚠️ Please enter valid values in all fields.")

if __name__ == '__main__':
    main()
