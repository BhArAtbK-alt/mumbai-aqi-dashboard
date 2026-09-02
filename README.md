# Mumbai Live Air Quality (AQI) Data Engineering & Analytics Pipeline

An end-to-end data engineering and analytics pipeline that extracts live air quality metrics across Mumbai from the **OpenAQ v3 API**, stores the data in a local **PostgreSQL** database via secure Unix Sockets, analyzes patterns using SQL, and visualizes pollution hotspots in Python.

## 🚀 Architecture Overview
```text
[OpenAQ v3 API] ➔ [Python Extract Script] ➔ [Unix Socket (Peer Auth)] ➔ [PostgreSQL Database] ➔ [SQL Analysis & Pandas] ➔ [Matplotlib Visualization]
🛠️ Tech Stack
Languages: Python 3.12, SQL
Database: PostgreSQL (with pgAdmin for visualization)
Libraries: Requests, Psycopg2, Pandas, Matplotlib
Security & Version Control: Git, Sockets Peer Authentication
📂 Project Structure
mumbai-aqi-dashboard/
├── .gitignore               # Prevents virtual env & keys from committing
├── requirements.txt         # Project dependencies
├── secrets.json             # Private API credentials (locally ignored)
├── secrets-example.json     # Safe template for public use
├── mumbai_aqi_trends.png    # Output visualization
├── sql/
│   └── queries.sql          # Analytics queries
└── scripts/
    ├── extract_aqi.py       # API extraction and pipeline loader
    └── visualize_aqi.py     # Database connector & charting script
📊 Database Schema (readings Table)
CREATE TABLE readings (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    pollutant VARCHAR(50),
    value DOUBLE PRECISION,
    unit VARCHAR(50),
    recorded_at TIMESTAMP
);
📈 Key Insights & SQL Analysis
Using PostgreSQL, we evaluated the live air quality data retrieved from 44 monitoring stations across the Mumbai Metropolitan Region:
1. Most Polluted Locations (PM2.5 Levels)
Our horizontal bar chart showcases the highest-risk zones for particulate matter:
2. SQL Analysis Executed
-- Query 1: Calculate Average Pollution Levels across different pollutants
SELECT pollutant, ROUND(AVG(value)::numeric, 2) as avg_value, unit 
FROM readings 
GROUP BY pollutant, unit;

-- Query 2: Get active stations ordered by sensor reading counts
SELECT location_name, COUNT(*) as reading_count 
FROM readings 
GROUP BY location_name 
ORDER BY reading_count DESC;

Developed as a portfolio project showcasing production-grade Python databases and secure Linux data pipelines.

---
