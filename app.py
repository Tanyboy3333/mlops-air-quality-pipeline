import sqlite3
import pandas as pd
import joblib
import gradio as gr
from datetime import datetime, timedelta

DB_NAME = 'feature_store.db'
MODEL_PATH = 'models/latest_model.pkl'  # Always load latest model

def load_latest_features():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT * FROM features ORDER BY timestamp DESC LIMIT 1",
        conn
    )
    conn.close()
    return df

def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

def predict_next_3_days():
    df_latest = load_latest_features()
    if df_latest.empty:
        return "No data available to base prediction on."

    base_features = df_latest.iloc[0]
    results = []

    for i in range(1, 4):
        future_time = datetime.utcnow() + timedelta(days=i)

        # Fill missing values with defaults
        temperature = base_features['temperature'] if pd.notnull(base_features['temperature']) else 0.0
        humidity = base_features['humidity'] if pd.notnull(base_features['humidity']) else 0.0
        pressure = base_features['pressure'] if pd.notnull(base_features['pressure']) else 1013.0  # Standard atmospheric pressure

        # Build input dataframe
        X_future = pd.DataFrame([{
            'pm25': base_features['pm25'],
            'pm10': base_features['pm10'],
            'no2': base_features['no2'],
            'so2': base_features['so2'],
            'co': base_features['co'],
            'o3': base_features['o3'],
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
        }])

        # Convert to float to ensure correct type for prediction
        X_future = X_future.astype(float)

        # Predict
        pred = model.predict(X_future)[0]
        results.append(f"{future_time.date()}: Predicted AQI = {pred:.2f}")

    return "\n".join(results)

with gr.Blocks() as demo:
    gr.Markdown("# 🌤 Air Quality 3-Day Forecast App")
    gr.Markdown("This app predicts the AQI for the next 3 days using the trained model.")
    predict_button = gr.Button("Predict 3-Day AQI")
    output = gr.Textbox(label="3-Day AQI Forecast")

    predict_button.click(fn=predict_next_3_days, outputs=output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
