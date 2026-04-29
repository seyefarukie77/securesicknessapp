FROM python:3.11-slim


WORKDIR /app

RUN pip install --no-cache-dir --upgrade \
    pip \
    setuptools \
    wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py routes.py model.py database.py ./
COPY templates ./templates
COPY static ./static

RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --home /home/appuser appuser
USER appuser

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "app:app"]
