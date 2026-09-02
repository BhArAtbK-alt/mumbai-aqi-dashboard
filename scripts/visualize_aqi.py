import pandas as pd
import matplotlib
matplotlib.use('Agg') 
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

# Write the SQL Query to fetch top 10 most polluted stations (PM2.5)
query = """
SELECT location_name, value 
FROM readings 
WHERE pollutant = 'pm25' 
ORDER BY value DESC 
LIMIT 10;
"""

# Load the data directly into a Pandas DataFrame
df = pd.read_sql_query(query, conn)
conn.close()

if df.empty:
    print("No PM2.5 data found in your database to visualize. Try running extract_aqi.py first!")
    exit(1)


plt.figure(figsize=(12, 6))


colors = ['#e74c3c' if x > 50 else '#f39c12' for x in df['value']] 
plt.barh(df['location_name'].iloc[::-1], df['value'].iloc[::-1], color=colors[::-1], edgecolor='black', height=0.6)

# Labels, title, and styling
plt.xlabel('PM2.5 Concentration (µg/m³)', fontsize=12, fontweight='bold', labelpad=10)
plt.ylabel('Monitoring Station Location', fontsize=12, fontweight='bold', labelpad=10)
plt.title('Top 10 Most Polluted Locations in Mumbai (PM2.5 Levels)', fontsize=14, fontweight='bold', pad=15)
plt.grid(axis='x', linestyle='--', alpha=0.5)

# Tight layout ensures labels don't get cut off
plt.tight_layout()

# Save the plot as a PNG image in your project root folder
plt.savefig('mumbai_aqi_trends.png', dpi=300)
