import sqlite3
import pandas as pd
import joblib
import gradio as gr
import requests
from datetime import datetime, timedelta

DB_NAME = 'feature_store.db'
MODEL_PATH = 'models/latest_model.pkl'
API_KEY = 'cdc44044452cf706943159b88eb2bc4f'  # Replace with your OpenWeather API key

def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

def fetch_air_pollution(lat, lon):
    api_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'list' in data and len(data['list']) > 0:
            return data['list'][0]
    return None

def fetch_weather(lat, lon):
    api_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

def predict_next_3_days(state, coords):
    if coords is None:
        return "Please select a location on the map."

    lat, lon = coords
    air_data = fetch_air_pollution(lat, lon)
    weather_data = fetch_weather(lat, lon)

    if air_data is None:
        return f"❌ Could not fetch air pollution data for {state} at ({lat:.2f}, {lon:.2f})."

    components = air_data.get('components', {})
    pm25 = components.get('pm2_5', 0.0)
    pm10 = components.get('pm10', 0.0)
    no2 = components.get('no2', 0.0)
    so2 = components.get('so2', 0.0)
    co = components.get('co', 0.0)
    o3 = components.get('o3', 0.0)

    # From weather API
    if weather_data:
        main = weather_data.get('main', {})
        temperature = main.get('temp', 0.0)
        humidity = main.get('humidity', 0.0)
        pressure = main.get('pressure', 1013.0)
    else:
        temperature = 0.0
        humidity = 0.0
        pressure = 1013.0

    results = []
    for i in range(1, 4):
        future_time = datetime.utcnow() + timedelta(days=i)
        X_future = pd.DataFrame([{
            'pm25': pm25,
            'pm10': pm10,
            'no2': no2,
            'so2': so2,
            'co': co,
            'o3': o3,
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
        }])
        X_future = X_future.astype(float)
        pred = model.predict(X_future)[0]
        results.append(f"{future_time.date()}: Predicted AQI = {pred:.2f}")

    return f"🌍 Location: {state} ({lat:.2f}, {lon:.2f})\n\n" + "\n".join(results)

with gr.Blocks() as demo:
    gr.Markdown("# 🌤 Air Quality 3-Day Forecast App (India)")
    gr.Markdown("Select a location on the map and enter the state name to get the forecast.")

    state_input = gr.Textbox(label="State", placeholder="e.g., Assam")
    map_input = gr.Map(label="Pick location (latitude, longitude)", value=[24.13, 89.46], zoom=4)
    predict_button = gr.Button("Predict 3-Day AQI")
    output = gr.Textbox(label="3-Day AQI Forecast")

    predict_button.click(
        fn=predict_next_3_days,
        inputs=[state_input, map_input],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
