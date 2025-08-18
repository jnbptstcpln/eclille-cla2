###########
# BUILDER #
###########

FROM python:3.9-slim

# Répertoire de travail
WORKDIR /usr/src/app

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Installation des dépendances système nécessaires aux libs Python (dont mysqlclient et weasyprint)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    musl-dev \
    libjpeg62-turbo-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    libffi-dev \
    default-libmysqlclient-dev \
    # Ajout des dépendances pour Weasyprint (incluant Cairo)
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libpango-1.0-0 \
    # La ligne suivante installe Cairo et ses dépendances
    libcairo2-dev \
    # Autres dépendances de Weasyprint
    libharfbuzz-dev \
    libfontconfig1 \
    libfreetype6-dev \
 && rm -rf /var/lib/apt/lists/*

# Copie des dépendances Python
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copie du reste du projet
COPY . .