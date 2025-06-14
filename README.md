
# Air Quality 3-Day Forecast using Machine Learning & MLOps  
🚀 **Live Demo:** https://mlops-air-quality-pipeline.onrender.com/  

*(NOTE: After clicking the Live Demo link, please wait 3-4 minutes for the container to start — Render containers go to sleep after inactivity.)*

---

## 🔍 Project Overview  
This project predicts the Air Quality Index (AQI) for the next 3 days using machine learning.  
The app fetches real-time air pollution and weather data via **OpenWeather API**, predicts AQI using a trained model, and displays results on a simple web interface.  

We use **Gradio** for the frontend, a **CI/CD pipeline** (GitHub Actions) for automation, and deploy the app on **Render**.  

---

## 🚀 How It Works  

1️⃣ **Model Training & Saving**  
- The machine learning model is trained weekly using historical data (air pollution + weather) to predict AQI.  
- The trained model is saved as `latest_model.pkl` using `joblib`.  

2️⃣ **Backend: Fast Inference with Gradio**  
- The app loads the trained model and serves predictions through a Gradio interface.  
- Users input state, latitude, and longitude to get the 3-day AQI forecast.

3️⃣ **Frontend: User-Friendly Gradio UI**  
- The interface shows predicted AQI and pollutant levels.
- Clear categories are provided:  
  ```
  0-50: Good | 51-100: Moderate | 101-200: Unhealthy for Sensitive Groups | 201+: Unhealthy
  ```

4️⃣ **CI/CD Pipeline: GitHub Actions + Render**  
- **Hourly:** `fetch_features.yml` updates data using OpenWeather API.  
- **Weekly:** `train_model.yml` retrains and updates the model.  
- Auto-deployment to Render when changes are pushed.

---

## 🛠️ Deployment on Render  

1️⃣ Push your code to GitHub  
2️⃣ GitHub Actions triggers workflows for data fetch, training, and deployment  
3️⃣ Render automatically pulls and redeploys the app  
4️⃣ Accessible live at: **[Air Quality Forecast App](https://mlops-air-quality-pipeline.onrender.com/)**  

---

## ✅ Features  

✔ Predicts 3-day AQI using real-time pollution + weather data  
✔ Gradio-based intuitive UI  
✔ Categories for general public understanding (Good / Moderate / Unhealthy)  
✔ Fully automated MLOps pipeline  
✔ Live deployment on Render  
✔ Environment variable support for API key security  

---

## ⚙ Tech Stack  

- **Python 3.9**
- **Pandas, Scikit-learn, XGBoost**
- **Gradio**
- **OpenWeather API**
- **GitHub Actions**
- **Render (for hosting)**  

---

## 📜 License  

This project is **open-source**. Feel free to fork, contribute, and share!
