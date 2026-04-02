# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py routes.py model.py database.py ./

# Set default port
ENV PORT=8080

# Initialize DB and run the app
CMD ["python", "app.py"]