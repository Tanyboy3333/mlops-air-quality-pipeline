FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir pandas joblib gradio fastapi uvicorn sqlite3 xgboost

EXPOSE 8080

CMD ["python", "app.py"]
