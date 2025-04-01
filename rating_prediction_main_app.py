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
        st.title("🍽️ Restaurant Ratings Predictor")
        st.write("Enter details about a restaurant to predict its rating.")
        
        st.subheader("🏢 Restaurant Details")
        
        city_list = [...]
        city = st.selectbox("City", options=sorted(city_list), key="City")
        
        longitude = st.text_input("Longitude", placeholder="e.g., -74.0060")
        latitude = st.text_input("Latitude", placeholder="e.g., 40.7128")
        cuisines = st.text_input("Cuisines", placeholder="e.g., Italian, Chinese")
        avg_cost = st.text_input("Average Cost for two", placeholder="e.g., 50")
        table_booking = st.number_input("Has Table booking", min_value=0, max_value=1, step=1)
        online_delivery = st.number_input("Has Online delivery", min_value=0, max_value=1, step=1)
        delivering_now = st.number_input("Is delivering now", min_value=0, max_value=1, step=1)
        switch_order_menu = st.number_input("Switch to order menu", min_value=0, max_value=1, step=1)
        price_range = st.text_input("Price range", placeholder="1 to 4")
        rating_color = st.selectbox("Rating Color", ["Dark Green", "Green", "Yellow", "Orange", "White", "Red"])
        rating_text = st.selectbox("Rating Text", ["Excellent", "Very Good", "Good", "Average", "Not rated", "Poor"])
        votes = st.text_input("Votes", placeholder="e.g., 500")
        area = st.text_input("Area", placeholder="e.g., Manhattan")
        
        if st.button("🔍 Predict Rating"):
            inputs = [city, longitude, latitude, cuisines, avg_cost, table_booking, 
                      online_delivery, delivering_now, switch_order_menu, price_range, 
                      rating_color, rating_text, votes, area]
            
            if "" in inputs:
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
