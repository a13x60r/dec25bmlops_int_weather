import os

import requests
import streamlit as st

# Configuration
API_URL = os.environ.get("API_URL", "http://localhost:3000")

st.set_page_config(page_title="Weather Prediction", page_icon="🌦️")


def login(username, password):
    """Authenticates with the BentoML service."""
    try:
        response = requests.post(
            f"{API_URL}/login",
            headers={"content-type": "application/json"},
            json={"username": username, "password": password},
            timeout=5,
        )
        if response.status_code == 200:
            return response.json().get("token")
        else:
            st.error(f"Login failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None


def predict(data, token):
    """Sends a prediction request to the BentoML service."""
    try:
        headers = {"content-type": "application/json", "Authorization": f"Bearer {token}"}
        response = requests.post(f"{API_URL}/predict", headers=headers, json=data, timeout=5)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.pop("token", None)
            st.rerun()
        else:
            st.error(f"Prediction failed: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None


def main():
    st.title("🌦️ Weather Prediction App")

    # Session State Initialization
    if "token" not in st.session_state:
        st.session_state.token = None

    # Login Screen
    if st.session_state.token is None:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")

            if submit_login:
                if username and password:
                    token = login(username, password)
                    if token:
                        st.session_state.token = token
                        st.success("Logged in successfully!")
                        st.rerun()
                else:
                    st.warning("Please enter both username and password.")
        return

    # Prediction Screen
    st.sidebar.button("Logout", on_click=lambda: st.session_state.pop("token", None))
    st.subheader("Enter Meteorological Data")

    with st.form("prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            min_temp = st.number_input("Min Temperature (°C)", value=15.0)
            max_temp = st.number_input("Max Temperature (°C)", value=25.0)
            rainfall = st.number_input("Rainfall (mm)", value=0.0, min_value=0.0)
            wind_gust_speed = st.number_input("Wind Gust Speed (km/h)", value=40.0)
            wind_speed_9am = st.number_input("Wind Speed 9am (km/h)", value=15.0)
            wind_speed_3pm = st.number_input("Wind Speed 3pm (km/h)", value=20.0)
            humidity_9am = st.number_input(
                "Humidity 9am (%)", value=60.0, min_value=0.0, max_value=100.0
            )

        with col2:
            humidity_3pm = st.number_input(
                "Humidity 3pm (%)", value=50.0, min_value=0.0, max_value=100.0
            )
            pressure_9am = st.number_input("Pressure 9am (hPa)", value=1015.0)
            pressure_3pm = st.number_input("Pressure 3pm (hPa)", value=1012.0)
            temp_9am = st.number_input("Temp 9am (°C)", value=18.0)
            temp_3pm = st.number_input("Temp 3pm (°C)", value=23.0)
            rain_today = st.selectbox(
                "Rain Today?", options=[0, 1], format_func=lambda x: "Yes" if x == 1 else "No"
            )
            year = st.number_input("Year", value=2024, step=1)

        # Hidden/Default fields as per schema but not relevant for user input usually or can be set to default
        # The schema requires them so we must provide them.
        # "Date", "Location", "WindGustDir", "WindDir9am", "WindDir3pm" are optional strings.

        submit_prediction = st.form_submit_button("Predict Rain")

    if submit_prediction:
        payload = {
            "MinTemp": min_temp,
            "MaxTemp": max_temp,
            "Rainfall": rainfall,
            "WindGustSpeed": wind_gust_speed,
            "WindSpeed9am": wind_speed_9am,
            "WindSpeed3pm": wind_speed_3pm,
            "Humidity9am": humidity_9am,
            "Humidity3pm": humidity_3pm,
            "Pressure9am": pressure_9am,
            "Pressure3pm": pressure_3pm,
            "Temp9am": temp_9am,
            "Temp3pm": temp_3pm,
            "RainToday": rain_today,
            "Year": year,
        }

        with st.spinner("Predicting..."):
            result = predict(payload, st.session_state.token)

        if result:
            st.divider()
            if result.get("prediction") == 1:
                st.error(f"🌧️ Prediction: {result.get('label')} (It will rain tomorrow)")
            else:
                st.success(f"☀️ Prediction: {result.get('label')} (No rain expected)")

            st.json(result)


if __name__ == "__main__":
    main()
