FROM python:3.11-slim

WORKDIR /app

# ✅ Upgrade tooling FIRST (prevents vulnerable vendored deps)
RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

# ✅ Now install app dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy app code
COPY app.py routes.py model.py database.py ./


# ✅ Copy GUI templates & static assets
COPY templates ./templates
COPY static ./static

ENV PORT=8080

CMD ["python", "app.py"]