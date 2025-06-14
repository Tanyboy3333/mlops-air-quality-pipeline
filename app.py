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

def fetch_current_data(lat, lon):
    api_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'list' in data and len(data['list']) > 0:
            return data['list'][0]  # Latest data point
    return None

def predict_next_3_days(state, lat, lon):
    entry = fetch_current_data(lat, lon)
    if entry is None:
        return f"Could not fetch data for {state} at ({lat}, {lon})."

    components = entry.get('components', {})
    
    # Handle missing components gracefully
    pm25 = components.get('pm2_5', 0.0)
    pm10 = components.get('pm10', 0.0)
    no2 = components.get('no2', 0.0)
    so2 = components.get('so2', 0.0)
    co = components.get('co', 0.0)
    o3 = components.get('o3', 0.0)

    # temperature, humidity, pressure not available from this API — use default values
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

    return f"🌍 Location: {state} ({lat}, {lon})\n\n" + "\n".join(results)

with gr.Blocks() as demo:
    gr.Markdown("# 🌤 Air Quality 3-Day Forecast App")
    gr.Markdown("Enter a location in India (state, latitude, longitude) to get the AQI forecast.")

    state_input = gr.Textbox(label="State", placeholder="e.g., Assam")
    lat_input = gr.Number(label="Latitude", value=24.13)
    lon_input = gr.Number(label="Longitude", value=89.46)
    predict_button = gr.Button("Predict 3-Day AQI")
    output = gr.Textbox(label="3-Day AQI Forecast")

    predict_button.click(
        fn=predict_next_3_days, 
        inputs=[state_input, lat_input, lon_input], 
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
