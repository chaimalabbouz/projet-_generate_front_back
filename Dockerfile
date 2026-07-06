FROM python:3.11-slim
WORKDIR /app
COPY gen-requirements.txt .
RUN pip install --no-cache-dir -r gen-requirements.txt
