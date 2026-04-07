FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python init_db.py && gunicorn --workers ${GUNICORN_WORKERS:-3} --bind 0.0.0.0:8000 wsgi:app"]
