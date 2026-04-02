# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set default port
ENV PORT=8080

# Initialize DB and run the app
CMD ["python", "app.py"]