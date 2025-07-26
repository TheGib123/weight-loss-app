# 🏋️‍♂️ Weight Loss Tracker - Flask App with Forecasting 📉

This is a Flask-based web application for tracking weight, calories, and BMR over time. It includes a forecasting chart using linear regression to predict future weight based on historical data. The app runs inside a Docker container and includes a dynamic 30-day forecast feature.

## 🚀 Features

- 📅 Log daily weight, calories, and BMR
- 📊 Interactive chart with Plotly showing:
  - Logged weight
  - Linear regression model
  - Forecasted weight
- 📈 Automatically forecasts weight 30 days into the future (or user-specified)
- 🐳 Runs as a Docker container for easy deployment

## 🧱 Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Charting**: Plotly
- **Containerization**: Docker


## 🐳 How to Run with Docker

Configure env file from the env_example file

```bash
# Clone the repo
git clone https://github.com/yourusername/weight-loss-tracker.git
cd weight-loss-tracker

# Build the Docker image
docker-compose build

# Run the container
docker-compose up -d
```
