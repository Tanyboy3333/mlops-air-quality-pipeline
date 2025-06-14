import sqlite3
import pandas as pd
import joblib
import gradio as gr

DB_NAME = 'feature_store.db'
MODEL_PATH = 'models/latest_model.pkl'  # or point to your best .pkl

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

def predict_aqi():
    df = load_latest_features()
    X = df[['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'temperature', 'humidity', 'pressure']]
    pred = model.predict(X)[0]
    return f"Predicted AQI: {pred:.2f}"

with gr.Blocks() as demo:
    gr.Markdown("# 🌤 Air Quality Prediction App")
    gr.Markdown("This app loads the latest features and predicts the AQI using the trained model.")
    predict_button = gr.Button("Predict AQI")
    output = gr.Textbox(label="Prediction Result")

    predict_button.click(fn=predict_aqi, outputs=output)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
