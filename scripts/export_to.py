import os
import pandas as pd
import psycopg2

try:
    # Connect to local PostgreSQL socket
    conn = psycopg2.connect(dbname="aqi_project", user="bharat")
    cursor = conn.cursor()
    
    # 2Fetch all readings
    cursor.execute("SELECT location_name, latitude, longitude, pollutant, value, unit, recorded_at FROM readings;")
    raw_data = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    
    cursor.close()
    conn.close()

    os.makedirs("data", exist_ok=True)

    # Load into Pandas and save to CSV
    df = pd.DataFrame(raw_data, columns=columns)
    df.to_csv("data/mumbai_aqi_data.csv", index=False)
    print("Success! Data exported to data/mumbai_aqi_data.csv")

except Exception as e:
    print(f"Error exporting data to CSV: {e}")

