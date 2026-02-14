FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash", "-c", "python manage.py migrate && uvicorn secure_exam_platform.asgi:application --host 0.0.0.0 --port 8000"]
