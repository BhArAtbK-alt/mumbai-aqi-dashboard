import pandas as pd
import matplotlib
matplotlib.use('Agg') # Headless mode
import matplotlib.pyplot as plt
import psycopg2

# Connect to PostgreSQL using your working Linux Socket
try:
    conn = psycopg2.connect(
        dbname="aqi_project",
        user="bharat"
    )
except Exception as e:
    print(f"Error connecting to database: {e}")
    exit(1)

# SQL Query to fetch top 10 most polluted stations (PM2.5)
query = """
SELECT location_name, value 
FROM readings 
WHERE pollutant = 'pm25' 
ORDER BY value DESC 
LIMIT 10;
"""

# Fetch data via Cursor
try:
    cursor = conn.cursor()
    cursor.execute(query)
    raw_data = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(raw_data, columns=columns)
except Exception as e:
    print(f"Error executing query: {e}")
    conn.close()
    exit(1)

if df.empty:
    print("No PM2.5 data found in your database to visualize. Try running extract_aqi.py first!")
    exit(1)

# Generate visual chart
plt.figure(figsize=(12, 6))

colors = ['#e74c3c' if x > 50 else '#f39c12' for x in df['value']]
plt.barh(df['location_name'].iloc[::-1], df['value'].iloc[::-1], color=colors[::-1], edgecolor='black', height=0.6)

plt.xlabel('PM2.5 Concentration (µg/m³)', fontsize=12, fontweight='bold', labelpad=10)
plt.ylabel('Monitoring Station Location', fontsize=12, fontweight='bold', labelpad=10)
plt.title('Top 10 Most Polluted Locations in Mumbai (PM2.5 Levels)', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('mumbai_aqi_trends.png', dpi=300)
print("Success! Created 'mumbai_aqi_trends.png' in your project folder.")
