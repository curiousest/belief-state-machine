# backend/Dockerfile
FROM python:3.12-slim

# Install build-essential for C++ compiler support
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir poetry
RUN poetry install

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
