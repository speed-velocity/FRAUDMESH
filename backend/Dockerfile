FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/backend

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY data/ /app/data/

EXPOSE 8000
CMD ["sh", "-c", "python -m app.cli reset-and-seed --dataset /app/data/demo --database-url ${DATABASE_URL:-sqlite:///data/runtime/fraudmesh.db} && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
