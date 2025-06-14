import sqlite3
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
from datetime import datetime

DB_NAME = 'feature_store.db'
MODEL_REGISTRY_DIR = 'models'

def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM features", conn)
    conn.close()
    return df

def prepare_data(df):
    # Features: pollutant & weather
    X = df[['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'temperature', 'humidity', 'pressure']]
    y = df['aqi']
    return train_test_split(X, y, test_size=0.2, random_state=42)

def train_and_evaluate(X_train, X_test, y_train, y_test):
    model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"Model Evaluation:\nMSE: {mse:.2f}\nR2 Score: {r2:.2f}")
    
    return model, mse, r2

def save_model(model, mse, r2):
    if not os.path.exists(MODEL_REGISTRY_DIR):
        os.makedirs(MODEL_REGISTRY_DIR)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"xgboost_regressor_{timestamp}_mse{mse:.2f}_r2{r2:.2f}.pkl"
    filepath = os.path.join(MODEL_REGISTRY_DIR, filename)

    joblib.dump(model, filepath)
    print(f"Model saved to: {filepath}")

def main():
    df = load_data()
    if df.empty:
        print("Feature store is empty. Please generate data first.")
        return

    X_train, X_test, y_train, y_test = prepare_data(df)
    model, mse, r2 = train_and_evaluate(X_train, X_test, y_train, y_test)
    save_model(model, mse, r2)

if __name__ == "__main__":
    main()
