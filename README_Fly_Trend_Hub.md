# Fly-Trend Hub – Airline Data Dashboard

An interactive web dashboard for analyzing airline trends, built using Streamlit and Plotly. It provides visual insights into passenger demographics, flight trends, and airport performance.

## Features
- Explore passenger demographics and nationality-based trends.
- View flight frequency and departure patterns by month.
- Drill down into airport performance metrics.
- Real-time data interaction using SQLite backend.

## Tech Stack
- Python, Pandas, SQLite
- Streamlit, Plotly

## 🚀 Live Demo
[Click here to explore the dashboard](https://fly-trend-app.streamlit.app)

## Project Structure
```
├── data/                   # Raw CSV + SQLite DB
├── app.py                  # Main Streamlit app
├── visuals.py              # Plotly chart logic
├── queries/                # SQL queries for filtering
├── requirements.txt        # Python dependencies
```

## What I Learned
- Using SQLite for backend query handling
- Streamlit layout and component integration
- Real-time chart rendering with Plotly
- End-to-end project from data cleaning to deployment
