import sqlite3
import datetime
import random

DB_NAME = 'feature_store.db'

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

def aqi_category(aqi):
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

def generate_synthetic_features(target_datetime):
    # Simulate feature values with some trends or random noise
    pm25 = random.uniform(5, 100)
    pm10 = random.uniform(10, 150)
    no2 = random.uniform(5, 80)
    so2 = random.uniform(1, 50)
    co = random.uniform(0.1, 3.0)
    o3 = random.uniform(10, 100)
    temperature = random.uniform(10, 35)
    humidity = random.uniform(30, 90)
    pressure = random.uniform(980, 1050)
    aqi = int(0.5 * pm25 + 0.3 * pm10 + 0.2 * no2)
    category = aqi_category(aqi)

    return {
        'timestamp': target_datetime.isoformat(),
        'pm25': pm25,
        'pm10': pm10,
        'no2': no2,
        'so2': so2,
        'co': co,
        'o3': o3,
        'temperature': temperature,
        'humidity': humidity,
        'pressure': pressure,
        'aqi': aqi,
        'category': category
    }

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

def generate_past_data(days_back=30):
    for i in range(days_back):
        date = datetime.datetime.utcnow() - datetime.timedelta(days=i)
        features = generate_synthetic_features(date)
        store_features(features)
        print(f"Stored historical features for {date.date()} - AQI: {features['aqi']} ({features['category']})")

def generate_future_data(future_days=3):
    for i in range(1, future_days + 1):
        date = datetime.datetime.utcnow() + datetime.timedelta(days=i)
        features = generate_synthetic_features(date)
        store_features(features)
        print(f"Stored future features for {date.date()} - AQI: {features['aqi']} ({features['category']})")

def main():
    init_db()
    print("Generating historical data...")
    generate_past_data()
    print("Generating future forecast data...")
    generate_future_data()

if __name__ == "__main__":
    main()
