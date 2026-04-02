# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set default port
ENV PORT=8080

# Make sure your app reads PORT from environment
CMD ["python", "-c", "import os; from app import app; app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))"]