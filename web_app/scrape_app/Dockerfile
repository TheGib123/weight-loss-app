FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nano \
    tzdata \
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

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY src/ ./src/

WORKDIR /app/src

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y google-chrome-stable

# Install matching ChromeDriver for Chrome version
RUN CHROME_VERSION=$(google-chrome --version | grep -oP "\d+\.\d+\.\d+") && \
    CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" | \
    jq -r --arg ver "$CHROME_VERSION" '.channels.Stable.downloads.chromedriver[] | select(.platform == "linux64") | .url') && \
    wget -O /tmp/chromedriver.zip "$CHROMEDRIVER_VERSION" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

# Set display port to avoid crash
ENV DISPLAY=:99

########### Set up Cron Job ###########
# set working directory
WORKDIR /

# Set timezone to America/Chicago
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Set up cron job
# RUN touch crontab
RUN echo '0 1 * * * /usr/local/bin/python /app/src/scrape.py >> /var/log/cron.log 2>&1' | crontab -

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Start the cron service
CMD cron && tail -f /var/log/cron.log