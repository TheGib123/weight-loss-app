FROM python:3.11-slim

ARG LOSEIT_EMAIL
ARG LOSEIT_PASSWORD
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_NAME
ARG HEIGHT
ARG AGE
ARG HEAVY_WEIGHT
ARG CRON_TIME
ARG DOWNLOAD_PATH

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nano \
    tzdata \
    chromium \
    chromium-driver \
    wget \
    gnupg \
    unzip \
    curl \
    jq \
    cron \
    xvfb \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    iputils-ping \
    && apt-get clean

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY scrape_app/src/ /app/src/
COPY ../functions/helper_functions.py /app/src/
WORKDIR /app/src

# Install pip requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set display port to avoid crash
ENV DISPLAY=:99

# Set timezone to America/Chicago
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Make entrypoint script executable
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]