FROM python:3.11-slim

# build-time ARGs
ARG LOSEIT_EMAIL
ARG LOSEIT_PASSWORD
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG DB_NAME
ARG HEIGHT
ARG DOB
ARG AGE
ARG HEAVY_WEIGHT
ARG CRON_TIME
ARG DOWNLOAD_PATH

RUN apt-get update && apt-get install -y tzdata

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY weight_app/src/ /app/src/
COPY ../functions/helper_functions.py /app/
WORKDIR /app/src

# Install pip requirements
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set timezone to America/Chicago
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 5000

#CMD ["python", "app.py"]
CMD ["tail", "-f", "/dev/null"]