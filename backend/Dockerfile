# Uses a slim Python image to keep the container small.
# Multi-stage builds could reduce it further, but that's complexity
# without benefit at this project's scale -- single stage is honest
# and fast enough.
FROM python:3.12-slim

WORKDIR /app

# Copy requirements first so Docker can cache this layer -- if only
# source code changes, pip install doesn't re-run, which makes rebuilds
# fast. This is a standard Dockerfile best practice worth knowing.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed the DB on startup (safe: seed.py checks if rows already exist and
# skips if so), then start the server.
CMD ["sh", "-c", "python -m app.db.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000"]

EXPOSE 8000
