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
        
        city_list = ['Makati City', 'Mandaluyong City', 'Pasay City', 'Pasig City',
       'Quezon City', 'San Juan City', 'Santa Rosa', 'Tagaytay City',
       'Taguig City', 'Brasilia', 'Rio de Janeiro', 'São Paulo', 'Albany',
       'Armidale', 'Athens', 'Augusta', 'Balingup', 'Beechworth', 'Boise',
       'Cedar Rapids/Iowa City', 'Chatham-Kent', 'Clatskanie', 'Cochrane',
       'Columbus', 'Consort', 'Dalton', 'Davenport', 'Des Moines',
       'Dicky Beach', 'Dubuque', 'East Ballina', 'Fernley', 'Flaxton',
       'Forrest', 'Gainesville', 'Hepburn Springs', 'Huskisson',
       'Inverloch', 'Lakes Entrance', 'Lakeview', 'Lincoln', 'Lorn',
       'Macedon', 'Macon', 'Mayfield', 'Mc Millan', 'Middleton Beach',
       'Monroe', 'Montville', 'Ojo Caliente', 'Orlando', 'Palm Cove',
       'Paynesville', 'Penola', 'Pensacola', 'Phillip Island',
       'Pocatello', 'Potrero', 'Princeton', 'Rest of Hawaii', 'Savannah',
       'Singapore', 'Sioux City', 'Tampa Bay', 'Tanunda', 'Trentham East',
       'Valdosta', 'Vernonia', 'Victor Harbor', 'Vineland Station',
       'Waterloo', 'Weirton', 'Winchester Bay', 'Yorkton', 'Abu Dhabi',
       'Dubai', 'Sharjah', 'Agra', 'Ahmedabad', 'Allahabad', 'Amritsar',
       'Aurangabad', 'Bangalore', 'Bhopal', 'Bhubaneshwar', 'Chandigarh',
       'Chennai', 'Coimbatore', 'Dehradun', 'Faridabad', 'Ghaziabad',
       'Goa', 'Gurgaon', 'Guwahati', 'Hyderabad', 'Indore', 'Jaipur',
       'Kanpur', 'Kochi', 'Kolkata', 'Lucknow', 'Ludhiana', 'Mangalore',
       'Mohali', 'Mumbai', 'Mysore', 'Nagpur', 'Nashik', 'New Delhi',
       'Noida', 'Panchkula', 'Patna', 'Puducherry', 'Pune', 'Ranchi',
       'Secunderabad', 'Surat', 'Vadodara', 'Varanasi', 'Vizag',
       'Bandung', 'Bogor', 'Jakarta', 'Tangerang', 'Auckland',
       'Wellington City', 'Birmingham', 'Edinburgh', 'London',
       'Manchester', 'Doha', 'Cape Town', 'Inner City', 'Johannesburg',
       'Pretoria', 'Randburg', 'Sandton', 'Colombo', 'Ankara', 'Istanbul']
        
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


        
        area_list = ['Century City Mall', 'Little Tokyo', 'Edsa Shangri-La',
       'SM Megamall', 'SM by the Bay', 'Sofitel Philippine Plaza Manila',
       'Kapitolyo', 'UP Town Center', 'Addition Hills', 'Little Baguio',
       'Nuvali', 'Solenad 3', 'Tagaytay City', 'BGC Stopover Pavillion',
       'Bonifacio Global City', 'SM Aura Premier', 'Asa Norte', 'Asa Sul',
       'guas Claras', 'Bras_lia Shopping', 'Lago Sul', 'ParkShopping',
       'Ponto Lago Sul', 'Setor De Clubes Esportivos Sul',
       'Shopping Iguatemi', 'Sudoeste', 'Barra da Tijuca', 'Centro',
       'Copacabana', 'Galeria River', 'Gvea', 'Ipanema', 'Lagoa',
       'Le Monde', 'Leblon', 'Leme', 'Madureira', 'Santa Teresa',
       'Tijuca', 'Urca', 'Bela Vista', 'Consola_o', 'Hotel Unique',
       'Itaim Bibi', 'Jardim Paulista', 'Moema', 'Pinheiros', 'Rep_blica',
       'Shopping Metr Santa Cruz', 'Shopping Morumbi', 'Vila Maria',
       'Vila Mariana', 'Vila Snia', 'Albany', 'Sylvester', 'Armidale',
       'Athens', 'Augusta', 'Evans', 'Grovetown', 'Balingup',
       'Beechworth', 'Boise', 'Meridian', 'Nampa', 'Cedar Rapids',
       'Coralville', 'Iowa City', 'Marion', 'Chatham-Kent', 'Clatskanie',
       'Cochrane', 'Columbus', 'Hamilton', 'Consort', 'Calhoun',
       'Chatsworth', 'Dalton', 'Fort Oglethorpe', 'LaFayette', 'Ringgold',
       'Rock Spring', 'Bettendorf', 'Davenport', 'Ames', 'Beaverdale',
       'Clive', 'Downtown', 'East Village', 'Fairground',
       'Greater South Side', 'Johnston',
       'Kingman Place Historic District', 'Urbandale', 'West Des Moines',
       'Dicky Beach', 'Dubuque', 'East Ballina', 'Fernley', 'Flaxton',
       'Forrest', 'Braselton', 'Clarkesville', 'Dahlonega',
       'Flowery Branch', 'Gainesville', 'Helen', 'Hepburn Springs',
       'Huskisson', 'Inverloch', 'Lakes Entrance', 'Lakeview',
       'Haymarket', 'Lorn', 'Macedon', 'Bonaire', 'Macon',
       'Warner Robins', 'Mayfield', 'Mc Millan', 'Middleton Beach',
       'Monroe', 'Montville', 'Ojo Caliente', 'Church Street District',
       'Disney World Area', 'Disney: Downtown Disney',
       'I-Drive/Universal', 'Mills 50', 'Restaurant Row', 'Sanford',
       'The Milk District', 'Windermere', 'Winter Park', 'Palm Cove',
       'Paynesville', 'Penola', 'Navarre', 'Pensacola', 'Pensacola Beach',
       'Perdido Key', 'Phillip Island', 'Blackfoot', 'Chubbuck',
       'Lava Hot Springs', 'Pocatello', 'Potrero', 'Princeton', 'Kahuku',
       'Kailua Kona', 'Kihei', 'Lahaina', 'Paia', 'Waikiki', 'Savannah',
       'Tybee Island', 'Bayfront Avenue', 'Bayfront Subzone',
       'Cantonment Road', 'Chinatown', 'City Hall', 'Duxton Hill',
       'Haji Lane', 'Hillcrest', 'Kay Siang Road', 'Lavender',
       'Marina Centre', 'Neil Road', 'North Bridge Road',
       'Robertson Quay', 'Sungai Pinang', 'Telok Ayer Street', 'Victoria',
       'Le Mars', 'Sioux City', 'South Sioux City', 'Clearwater',
       'Downtown St Petersburg', 'Hyde Park',
       'Indian Rocks/Indian Shores', 'Kenwood',
       'Madeira Beach/Redington Beach', 'New Tampa',
       'Northeast St Petersburg', 'Palma Ceia', 'Seminole Heights',
       'Ybor City', 'Tanunda', 'Trentham East', 'Valdosta', 'Vernonia',
       'Victor Harbor', 'Vineland Station', 'Cedar Falls', 'Waterloo',
       'Weirton', 'Winchester Bay', 'Yorkton', 'Abu Dhabi Mall',
       'Al Dhafrah', 'Al Mushrif', 'Al Wahda Mall',
       'Crowne Plaza Abu Dhabi', 'Dalma Mall', 'Madinat Zayed',
       'Madinat Zayed Shopping Centre', 'Mushrif Mall',
       'Mussafah Sanaiya', 'Najda', 'Venetian Village',
       'World Trade Center Mall', 'Yas Mall', 'Al Barari', 'Al Karama',
       'Barsha 2', 'CITY WALK', 'Deira City Centre Area', 'DIFC',
       'Dubai Media City', 'Festival City', 'Jumeirah 1', 'Kite Beach',
       'Mall of the Emirates', 'Mankhool', 'Nassima Royal Hotel', 'Satwa',
       'The Dubai Mall,Downtown Dubai', 'Trade Centre Area', 'Umm Hurair',
       'Abu Shagara', 'Al Khan', 'Al Majaz', 'Al Mareija', 'Al Nahda',
       'Al Nud', 'Al Qasba', 'Halwan Suburb', 'Majaz Waterfront',
       'Muwailih Commercial', 'Sahara Centre', 'University City',
       'Agra Cantt', 'Civil Lines', 'Courtyard by Marriott Agra',
       'ITC Mughal', 'Khandari', 'Radisson Blu', 'Rakabganj', 'Tajganj',
       'Ambavadi', 'Ashram Road', 'Bodakdev', 'C G Road',
       'Courtyard By Marriott', 'Ellis Bridge', 'Ghatlodia', 'Gurukul',
       'Navrangpura', 'Prahlad Nagar', 'Thaltej', 'The Fern', 'Vastrapur',
       'Tagore Town', 'Vinayak City Centre Mall', 'Basant Nagar',
       'Hathi Gate', 'INA Colony', 'Ranjit Avenue', 'Town Hall',
       'White Avenue', 'Akashwani', 'Chicalthana', 'CIDCO',
       'Hotel Green Olive', 'Mondha', 'Nirala Bazar', 'Nyay Nagar',
       'Prozone Mall', 'Shahgunj', 'Usmanpura', 'BluPetal Hotel',
       'Indiranagar', 'JP Nagar', 'Koramangala 5th Block',
       'Koramangala 6th Block', 'Koramangala 7th Block', 'Marathahalli',
       'New BEL Road', 'Residency Road', 'Sarjapur Road', 'UB City',
       'Arera Colony', 'DB City', 'Gulmohar Colony', 'Kohefiza',
       'Maharana Pratap Nagar', 'Peer Gate Area', 'Sayaji Hotel',
       'TT Nagar', 'BMC Bhawani Mall', 'Chandrasekharpur',
       'Gajapati Nagar', 'Mayfair Lagoon', 'Patia', 'Sahid Nagar',
       'The Crown', 'Unit 4', 'Chandigarh Industrial Area', 'Elante Mall',
       'Sector 26', 'Sector 28', 'Sector 35', 'Sector 7', 'Sector 8',
       'Adyar', 'Anna Nagar East', 'Ashok Nagar', 'Express Avenue Mall',
       'Gopalapuram', 'Kilpauk', 'Kotturpuram', 'Mylapore',
       'Nungambakkam', 'Perungudi', 'RA Puram', 'Ramapuram', 'Santhome',
       'T. Nagar', 'Velachery', 'Gandhipuram', 'Peelamedu', 'Podanur',
       'Race Course', 'RS Puram', 'Saibaba Colony', 'SMS Hotel',
       'Chukkuwala', 'Hathibarkala Salwala', 'Jakhan', 'Karanpur',
       'Krishna Nagar', 'Malsi', 'Pacific Mall', 'Paltan Bazaar',
       'Rajpur', 'Badarpur Border', 'Badkal Lake', 'Charmwood Village',
       'Crown Interiorz Mall', 'Crown Plaza Mall', 'Dayal Bagh',
       'Eldeco Station 1 Mall', 'Hotel Saffron Kiran',
       'Indraprastha Colony', 'K Hotel', 'NIT', 'Park Plaza',
       'Parsavnath City Mall', 'Sector 10', 'Sector 11', 'Sector 12',
       'Sector 15', 'Sector 16', 'Sector 17', 'Sector 19', 'Sector 21',
       'Sector 29']
        
        
        
        
        area = st.selectbox("Area", options=sorted(area_list), key="Area", placeholder="e.g., Manhattan")


        
        
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
