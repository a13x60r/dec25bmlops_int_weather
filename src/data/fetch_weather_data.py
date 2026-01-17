import logging
import os
from datetime import datetime

import pandas as pd
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Constants
API_KEY = os.getenv("OPENWEATHER_API_KEY")
DATA_PATH = "data/raw/weatherAUS.csv"
# Fallback to 2.5/weather because 3.0 requires subscription
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# City Coordinates (latitude, longitude)
CITIES = {
    "Sydney": (-33.8688, 151.2093),
    "Melbourne": (-37.8136, 144.9631),
    "Brisbane": (-27.4698, 153.0251),
    "Perth": (-31.9505, 115.8605),
    "Adelaide": (-34.9285, 138.6007),
    "Canberra": (-35.2809, 149.1300),
    "Hobart": (-42.8821, 147.3272),
    "Darwin": (-12.4634, 130.8456),
}


def fetch_weather_data(city, lat, lon):
    """Fetch daily weather data for a specific city."""
    try:
        url = f"{BASE_URL}?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Mapping Current Weather (2.5) to Target Schema
        main_data = data.get("main", {})
        wind_data = data.get("wind", {})
        rain_data = data.get("rain", {})
        clouds_data = data.get("clouds", {})

        return {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Location": city,
            "MinTemp": main_data.get("temp_min"),
            "MaxTemp": main_data.get("temp_max"),
            "Rainfall": rain_data.get("1h", 0),
            "Evaporation": "NA",
            "Sunshine": "NA",
            "WindGustDir": "NA",
            "WindGustSpeed": wind_data.get("speed"),
            "WindDir9am": "NA",
            "WindDir3pm": "NA",
            "WindSpeed9am": "NA",
            "WindSpeed3pm": "NA",
            "Humidity9am": main_data.get("humidity"),
            "Humidity3pm": main_data.get("humidity"),
            "Pressure9am": main_data.get("pressure"),
            "Pressure3pm": main_data.get("pressure"),
            "Cloud9am": clouds_data.get("all"),
            "Cloud3pm": clouds_data.get("all"),
            "Temp9am": main_data.get("temp"),
            "Temp3pm": main_data.get("temp"),
            "RainToday": "Yes" if rain_data.get("1h", 0) > 1 else "No",
            "RainTomorrow": "NA",
        }
    except Exception as e:
        if "response" in locals():
            logging.error(f"Failed to fetch data for {city}: {e}. Response: {response.text}")
        else:
            logging.error(f"Failed to fetch data for {city}: {e}")
        return None


def main():
    if not API_KEY:
        logging.error("OPENWEATHER_API_KEY environment variable not set.")
        return

    logging.info("Starting weather data fetch job...")

    new_rows = []
    for city, coords in CITIES.items():
        logging.info(f"Fetching data for {city}...")
        row = fetch_weather_data(city, coords[0], coords[1])
        if row:
            new_rows.append(row)

    if new_rows:
        df_new = pd.DataFrame(new_rows)

        if os.path.exists(DATA_PATH):
            df_new.to_csv(DATA_PATH, mode="a", header=False, index=False)
            logging.info(f"Appended {len(new_rows)} rows to {DATA_PATH}")
        else:
            df_new.to_csv(DATA_PATH, index=False)
            logging.info(f"Created {DATA_PATH} with {len(new_rows)} rows")
    else:
        logging.info("No data fetched.")


if __name__ == "__main__":
    main()
