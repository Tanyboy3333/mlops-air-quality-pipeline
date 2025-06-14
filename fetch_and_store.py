import requests
import sqlite3
import datetime

# ==========================
# CONFIG
# ==========================
API_TOKEN = '46a61c232e8d2b36d15a232b6a6dcdff09d66664'  # <-- Replace with your token
CITY = 'barcelona'
API_URL = f'https://api.waqi.info/feed/{CITY}/?token={API_TOKEN}'
DB_NAME = 'feature_store.db'

# ==========================
# FETCH RAW DATA
# ==========================
def fetch_data():
    print(f"Fetching data for {CITY}...")
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'ok':
            return data['data']
        else:
            print("API returned error:", data.get('data'))
    else:
        print("Failed to fetch data:", response.status_code)
    return None

# ==========================
# EXTRACT FEATURES + TARGET
# ==========================
def extract_features(raw_data):
    iaqi = raw_data.get('iaqi', {})
    features = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'pm25': iaqi.get('pm25', {}).get('v'),
        'pm10': iaqi.get('pm10', {}).get('v'),
        'no2': iaqi.get('no2', {}).get('v'),
        'so2': iaqi.get('so2', {}).get('v'),
        'co': iaqi.get('co', {}).get('v'),
        'o3': iaqi.get('o3', {}).get('v'),
        'temperature': iaqi.get('t', {}).get('v'),
        'humidity': iaqi.get('h', {}).get('v'),
        'pressure': iaqi.get('p', {}).get('v'),
        'aqi': raw_data.get('aqi'),
        'category': aqi_category(raw_data.get('aqi'))
    }
    return features

def aqi_category(aqi):
    if aqi is None:
        return "Unknown"
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

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
    print("Features stored successfully.")

# ==========================
# MAIN
# ==========================
def main():
    init_db()
    raw_data = fetch_data()
    if raw_data:
        features = extract_features(raw_data)
        store_features(features)
        print("Stored features:", features)
    else:
        print("No data fetched.")

if __name__ == "__main__":
    main()
