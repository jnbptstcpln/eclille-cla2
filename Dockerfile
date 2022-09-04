###########
# BUILDER #
###########

# Pull official base image
FROM python:3.9.4-buster

# Set work directory
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev musl-dev \
    && apt-get install -y --no-install-recommends libjpeg62-turbo-dev libopenjp2-7-dev zlib1g-dev \
    && apt-get install -y --no-install-recommends libsasl2-dev libldap2-dev libssl-dev libffi-dev

# Install dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# Clear build dependencies
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*
