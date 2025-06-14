import requests
import sqlite3
import datetime

# ==========================
# CONFIG
# ==========================
API_KEY = 'cdc44044452cf706943159b88eb2bc4f'  # <-- Replace with your OpenWeather API key
CITY = 'Assam'
LAT = 24.13
LON = 89.46
API_URL = f'http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={LAT}&lon={LON}&appid={API_KEY}'
DB_NAME = 'feature_store.db'

# ==========================
# FETCH RAW DATA
# ==========================
def fetch_data():
    print(f"Fetching forecast data for {CITY}...")
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        if 'list' in data:
            return data['list']  # List of forecast data points
        else:
            print("API returned error:", data)
    else:
        print("Failed to fetch data:", response.status_code)
    return []

# ==========================
# EXTRACT FEATURES + TARGET
# ==========================
def extract_features(entry):
    components = entry.get('components', {})
    dt = datetime.datetime.utcfromtimestamp(entry.get('dt')).isoformat()
    features = {
        'timestamp': dt,
        'pm25': components.get('pm2_5'),
        'pm10': components.get('pm10'),
        'no2': components.get('no2'),
        'so2': components.get('so2'),
        'co': components.get('co'),
        'o3': components.get('o3'),
        'temperature': None,  # Not provided by this API
        'humidity': None,     # Not provided by this API
        'pressure': None,     # Not provided by this API
        'aqi': entry.get('main', {}).get('aqi'),
        'category': aqi_category(entry.get('main', {}).get('aqi'))
    }
    return features

def aqi_category(aqi):
    if aqi is None:
        return "Unknown"
    if aqi == 1:
        return "Good"
    elif aqi == 2:
        return "Fair"
    elif aqi == 3:
        return "Moderate"
    elif aqi == 4:
        return "Poor"
    elif aqi == 5:
        return "Very Poor"
    else:
        return "Unknown"

# ==========================
# FEATURE STORE
# ==========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pm25 REAL,
            pm10 REAL,
            no2 REAL,
            so2 REAL,
            co REAL,
            o3 REAL,
            temperature REAL,
            humidity REAL,
            pressure REAL,
            aqi INTEGER,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

def store_features(features):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO features (
            timestamp, pm25, pm10, no2, so2, co, o3, temperature, humidity, pressure, aqi, category
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        features['timestamp'],
        features['pm25'],
        features['pm10'],
        features['no2'],
        features['so2'],
        features['co'],
        features['o3'],
        features['temperature'],
        features['humidity'],
        features['pressure'],
        features['aqi'],
        features['category']
    ))
    conn.commit()
    conn.close()
    print(f"Stored features for {features['timestamp']} successfully.")

# ==========================
# MAIN
# ==========================
def main():
    init_db()
    forecast_list = fetch_data()
    if forecast_list:
        for entry in forecast_list:
            features = extract_features(entry)
            store_features(features)
    else:
        print("No forecast data fetched.")

if __name__ == "__main__":
    main()
