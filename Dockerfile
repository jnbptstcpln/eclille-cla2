###########
# BUILDER #
###########

FROM python:3.12-slim-bookworm

# Répertoire de travail
WORKDIR /usr/src/app

# Variables d'environnement pour Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Dépendances système
# - gcc, pkg-config, default-libmysqlclient-dev : compilation de mysqlclient (pas de wheel Linux)
# - curl : healthcheck
# - pango, harfbuzz-subset : WeasyPrint (n'utilise plus Cairo depuis la v53)
# - fonts-dejavu-core : police de repli des PDF si Google Fonts est injoignable
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    curl \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz-subset0 \
    fonts-dejavu-core \
 && rm -rf /var/lib/apt/lists/*

# Copie des dépendances Python
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Copie du reste du projet
COPY . .
# --- Déploiement (Coolify) ---
# Le docker-compose.yml de dev surcharge command + DJANGO_SETTINGS_MODULE, donc inchangé pour le dev local.
ENV DJANGO_SETTINGS_MODULE=cla_web.settings.coolify
RUN chmod +x /usr/src/app/entrypoint.sh
EXPOSE 8000
CMD ["/usr/src/app/entrypoint.sh"]
