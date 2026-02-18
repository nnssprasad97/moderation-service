FROM python:3.11-slim

WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/

# The CMD is overridden in docker-compose for specific services
