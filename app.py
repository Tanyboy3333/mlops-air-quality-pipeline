import sqlite3
import pandas as pd
import joblib
import gradio as gr
import requests
from datetime import datetime, timedelta

DB_NAME = 'feature_store.db'
MODEL_PATH = 'models/latest_model.pkl'
API_KEY = os.getenv('cdc44044452cf706943159b88eb2bc4f')  # Replace with your OpenWeather API key

def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

def fetch_air_pollution_forecast(lat, lon):
    api_url = f'http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={API_KEY}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'list' in data and len(data['list']) > 0:
            return data['list']  # List of forecast points
    return []

def fetch_weather_forecast(lat, lon):
    api_url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if 'list' in data:
            return data['list']  # 3-hourly forecasts
    return []

def predict_next_3_days(state, lat, lon):
    if lat is None or lon is None:
        return "❌ Please provide both latitude and longitude."

    air_data_list = fetch_air_pollution_forecast(lat, lon)
    weather_data_list = fetch_weather_forecast(lat, lon)

    if not air_data_list:
        return f"❌ Could not fetch air pollution forecast data for {state} at ({lat:.2f}, {lon:.2f})."

    results = []

    for i in range(1, 4):
        target_date = (datetime.utcnow() + timedelta(days=i)).date()

        # Find nearest air forecast for that day
        air_forecast = next((a for a in air_data_list 
                             if datetime.utcfromtimestamp(a['dt']).date() == target_date), None)

        # Find nearest weather forecast for that day
        weather_forecast = next((w for w in weather_data_list
                                 if datetime.utcfromtimestamp(w['dt']).date() == target_date), None)

        if air_forecast:
            components = air_forecast.get('components', {})
            pm25 = components.get('pm2_5', 0.0)
            pm10 = components.get('pm10', 0.0)
            no2 = components.get('no2', 0.0)
            so2 = components.get('so2', 0.0)
            co = components.get('co', 0.0)
            o3 = components.get('o3', 0.0)
        else:
            pm25 = pm10 = no2 = so2 = co = o3 = 0.0

        if weather_forecast:
            main = weather_forecast.get('main', {})
            temperature = main.get('temp', 0.0)
            humidity = main.get('humidity', 0.0)
            pressure = main.get('pressure', 1013.0)
        else:
            temperature = 0.0
            humidity = 0.0
            pressure = 1013.0

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

        results.append(
            f"{target_date}: Predicted AQI = {pred:.2f} | "
            f"PM2.5={pm25}, PM10={pm10}, NO2={no2}, SO2={so2}, CO={co}, O3={o3}, "
            f"Temp={temperature}°C, Humidity={humidity}%, Pressure={pressure} hPa"
        )

    return f"🌍 Location: {state} ({lat:.2f}, {lon:.2f})\n\n" + "\n".join(results)

# ==========================
# Gradio Interface
# ==========================
with gr.Blocks() as demo:
    gr.Markdown("# 🌤 Air Quality 3-Day Forecast App (India)")
    gr.Markdown("Enter state and coordinates to get the AQI forecast.")

    state_input = gr.Textbox(label="State", placeholder="e.g., Assam")
    lat_input = gr.Number(label="Latitude", value=24.13)
    lon_input = gr.Number(label="Longitude", value=89.46)
    predict_button = gr.Button("Predict 3-Day AQI")
    output = gr.Textbox(label="3-Day AQI + Forecast")

    predict_button.click(
        fn=predict_next_3_days,
        inputs=[state_input, lat_input, lon_input],
        outputs=output
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
