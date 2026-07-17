FROM python:3.11-slim

# outils système : gcc pour certains paquets, curl pour les healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. dépendances (couche cachée si requirements ne change pas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. le code
COPY shared/ ./shared/
COPY services/ ./services/
COPY orchestrator/ ./orchestrator/

# la commande sera précisée par docker-compose (chaque service la sienne)